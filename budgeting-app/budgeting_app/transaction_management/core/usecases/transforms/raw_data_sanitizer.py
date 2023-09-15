from budgeting_app.utils.types import T_raw_data


class RawDataSanitizer:
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

    def append_year_to_invalid_date(invalid_date: str, year: str) -> str:
        return invalid_date + ' ' + year

    def clean_up_paid(invalid_float: str) -> str | None:
        if invalid_float == '':
            return '0.0'

        valid_float_list = []
        found_numbers_in_str = False

        for _char in invalid_float.split(sep=''):

            if _char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
                valid_float_list.append(_char)
                found_numbers_in_str = True
            elif found_numbers_in_str:
                return None

        return ''.join(valid_float_list)
