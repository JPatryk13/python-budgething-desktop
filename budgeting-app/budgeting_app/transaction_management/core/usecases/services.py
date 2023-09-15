from typing import Literal
from budgeting_app.transaction_management.core.interfaces.repositories import (
    TransactionDataRawRepository,
    TransactionRepository,
    AccountRepository,
    TransactionTypeRepository,
    TransactionCategoryRepository,
    DerivedFromJunctionRepository,
    CategoryTransactionJunctionRepository
)
from .transforms.raw_data_validator import RawDataValidator
from .transforms.raw_data_converter import RawDataConverter
from budgeting_app.utils.types import (
    T_raw_data,
    T_uuid4_string
)


class TransactionDataRawService:
    transaction_data_raw_repository: TransactionDataRawRepository

    def __init__(
        self,
        transaction_data_raw_repository: TransactionDataRawRepository
    ) -> None:
        self.transaction_data_raw_repository = transaction_data_raw_repository

    def new_from_raw_data_table(self, table: list[T_raw_data], schema: list[str], account_uuid: T_uuid4_string) -> list[T_raw_data]:
        """
        When fails due to a row that has too few or too many entries returns index of that row.
        When fails due to an empty string returns a tuple with indices pointing to that string.
        The function aggregates errors mentioned above across the whole table, thus the output
        can be understood as such:
        list_of_invalid_entries[tuple_with_invalid_str_indices or index_of_invalid_row]
        Empty list indicates a success. Otherwise no transaction is saved.
        """
        invalid_rows: list[T_raw_data] = []

        for str_row in table:
            invalid_rows.append(self.new_from_raw_data_row(
                row=str_row, schema=schema))

        return invalid_rows

    def new_from_raw_data_row(self, row: T_raw_data, schema: list[str], account_uuid: T_uuid4_string) -> T_raw_data | None:

        if RawDataValidator(row=row, schema=schema).is_valid_row():
            row_obj = RawDataConverter(row=row, schema=schema)

            transaction_data_raw = self.transaction_data_raw_repository.create(
                date=row_obj.get_date(),
                description=row_obj.get_description(),
                paid_out=row_obj.get_paid_out(),
                paid_in=row_obj.get_paid_in(),
                balance_after_transaction=row_obj.get_account_balance(),
                account_uuid=account_uuid,
                raw_data=row
            )

            self.transaction_data_raw_repository.save(obj=transaction_data_raw)
        else:
            return row


class TransactionService:
    transaction_repository: TransactionRepository

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository


class AccountService:
    account_repository: AccountRepository

    def __init__(self, account_repository: AccountRepository) -> None:
        self.account_repository = account_repository


class TransactionTypeService:
    transaction_type_repository: TransactionTypeRepository

    def __init__(self, transaction_type_repository: TransactionTypeRepository) -> None:
        self.transaction_type_repository = transaction_type_repository


class TransactionCategoryService:
    transaction_category_repository: TransactionCategoryRepository

    def __init__(self, transaction_category_repository: TransactionCategoryRepository) -> None:
        self.transaction_category_repository = transaction_category_repository
