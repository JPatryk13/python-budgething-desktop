from budgeting_app.utils.types import T_raw_data
from budgeting_app.transaction_management.core.entities.types import T_transaction_data_raw


class RawDataValidator:
    date_str: str
    paid_in_str: str
    paid_out_str: str
    account_balance_str: str
    description: list[str] | str

    def __init__(self, row: T_raw_data, schema: list[str]) -> None:
        description: list[str] = []
        for i, col_name in enumerate(schema):
            if col_name == 'date':
                self.date_str = row[i]
            elif col_name == 'paid_in':
                self.paid_in_str = row[i]
            elif col_name == 'paid_out':
                self.paid_out_str = row[i]
            elif col_name == 'balance_after_transaction':
                self.account_balance_str = row[i]
            else:
                description.append(row[i])
        if len(description) == 1:
            self.description = description[0]
        else:
            self.description = description

    @classmethod
    def _which_month(cls, month: str) -> int | None:
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        for i, m in enumerate(months):
            if m.startswith(month):
                return i
        return None

    @classmethod
    def _is_valid_month_str(cls, month: str) -> bool:
        return cls._which_month(month) is not None

    @classmethod
    def _is_convertible_to_float(cls, f: str) -> bool:
        try:
            float(f)
            return True
        except:
            return False

    @classmethod
    def _is_convertible_to_nonnegative_float(cls, paid: str) -> bool:
        if cls._is_convertible_to_float(paid):
            _paid = float(paid)
            return _paid >= 0.0

        return False

    def is_valid_date_str(self) -> bool:
        date_chunks = self.date_str.split()

        if len(date_chunks) == 3:

            day = date_chunks[0]
            month = date_chunks[1].lower()
            year = date_chunks[2]

            if len(day) in [1, 2] and len(year) in [2, 4] and len(month) >= 3:
                try:
                    day_int = int(day)
                    int(year)
                except:
                    return False

                if self._is_valid_month_str(month=date_chunks[1].lower()):
                    day_count_for_month = [31, 29, 31, 30,
                                           31, 30, 31, 31, 30, 31, 30, 31]
                    return int(day) <= day_count_for_month[self._which_month(month)]

        return False

    def is_valid_paid_in_str(self) -> bool:
        return self._is_convertible_to_nonnegative_float(self.paid_in_str)

    def is_valid_paid_out_str(self) -> bool:
        return self._is_convertible_to_nonnegative_float(self.paid_out_str)

    def is_valid_description(self) -> bool:
        if isinstance(self.description, list):
            return all(list(map(lambda s: isinstance(s, str), self.description)))
        return isinstance(self.description, str)

    def is_valid_account_balance_str(self) -> bool:
        return self._is_convertible_to_float(self.account_balance_str)

    def is_valid_row(self) -> bool:
        return all([
            self.is_valid_date_str(),
            self.is_valid_paid_in_str(),
            self.is_valid_paid_out_str(),
            self.is_valid_account_balance_str,
            self.is_valid_description()
        ])
