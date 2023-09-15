from budgeting_app.utils.types import (
    T_raw_data,
    T_normalised_raw_data
)


class NormaliseRawData:
    @classmethod
    def normalise_table(cls, table: list[T_raw_data]) -> list[T_normalised_raw_data]:
        normal_table: list[T_normalised_raw_data] = []
        for row in table:
            normal_table.append(cls.normalise_row(row=row))
        return normal_table

    @classmethod
    def normalise_row(cls, row: T_raw_data, *, skip_lists: bool = False) -> T_normalised_raw_data:
        normal_row: T_normalised_raw_data = []
        for cell in row:
            if isinstance(cell, str):
                normal_row.append(cell)
            elif isinstance(cell, list) and not skip_lists:
                list_of_str = cls.normalise_row(row=cell, skip_lists=True)
                normal_row.append(cls.__get_list_as_str(_list=list_of_str))
            else:
                normal_row.append('')
        return normal_row

    @classmethod
    def __get_list_as_str(cls, _list: list[str]) -> str:
        # removing redundant whitespaces
        return ' '.join(' '.join(_list).split())
