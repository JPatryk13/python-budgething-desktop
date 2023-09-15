from datetime import datetime

from budgeting_app.utils.types import (
    T_posix_timestamp,
    T_nonnegative_float
)
from .raw_data_validator import RawDataValidator


class RawDataConverter:
    date_str: str
    paid_in_str: str
    paid_out_str: str
    account_balance_str: str
    description: str

    def __init__(self, row: list[str], schema: list[str]) -> None:
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
        self.description = ' '.join(description)

    def get_date(self) -> T_posix_timestamp:
        day_str, month_str, year_str = self.date_str.split()
        day_int = int(day_str)
        month_int = RawDataValidator._which_month(month_str)
        if len(year_str) == 2:
            year_int = 2000 + int(year_str)
        else:
            year_int = int(year_str)

        return int(datetime(year=year_int, month=month_int, day=day_int).timestamp())

    def get_paid_in(self) -> T_nonnegative_float:
        return abs(float(self.paid_in_str))

    def get_paid_out(self) -> T_nonnegative_float:
        return abs(float(self.paid_out_str))

    def get_description(self) -> str:
        return ' '.join(self.description.split())

    def get_account_balance(self) -> float:
        return float(self.account_balance_str)
