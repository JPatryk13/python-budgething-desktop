from budgeting_app.utils.types import T_raw_data
from .raw_data_validator import RawDataValidator


class TableValidator:
    table: list[T_raw_data]
    schema: list[str]
    required = ['date', 'balance_after_transaction']
    optional = ['description']
    dependent = ['paid_in', 'paid_out']

    def __init__(self, table: list[T_raw_data], schema: list[str]) -> None:
        self.table = table
        self.schema = schema

    def __post_init__(self) -> None:
        if not self.__is_valid_schema():
            raise ValueError

    def validate(self) -> list[tuple[int, int] | int]:
        return self._validate_table()

    def __is_valid_schema(self) -> bool:
        return all(
            list(map(
                lambda c: c in self.required + self.optional + self.dependent,
                self.schema
            ))
        ) and all(
            list(map(
                lambda c: self.schema.count(c) == 1,
                self.required + self.dependent
            ))
        )

    def _validate_table(self) -> list[tuple[int, int] | int]:
        errors: list[tuple[int, int] | int] = []
        for i, row in enumerate(self.table):
            if len(row) != len(self.schema):
                errors.append(i)
            else:
                row_errors = self._validate_row(row)
                if len(row_errors) != 0:
                    for j in row_errors:
                        errors.append((i, j))
        return errors

    @classmethod
    def is_validate_row(self, row: T_raw_data) -> list[int]:
        """
        When fails due to an empty string returns an index pointing to that string.
        The function aggregates errors mentioned above across the whole list.
        """
        errors: list[int] = []
        for i, cell in enumerate(row):
            if self.schema[i] == 'date':
                errors.extend(RawDataValidator.is_valid_date_str(cell))
            elif self.schema[i] == 'paid_in':
                errors.extend(self._validate_paid(row=row))
            if self.schema[i] in self.required and cell == '':
                errors.append(i)
        errors.extend(self.__validate_dependent_field(row))
        return errors

    def __validate_dependent_field(self, row: T_raw_data) -> list[int]:
        paid_in_index = self.schema.index('paid_in')
        paid_out_index = self.schema.index('paid_out')
        if self.schema[paid_in_index] == '' and self.schema[paid_out_index] == '':
            return [paid_out_index, paid_in_index]
