from abc import ABCMeta, abstractmethod

from budgeting_app.transaction_management.core.entities.types import (
    T_uuid4_string,
    T_transaction_data_raw,
    T_transaction,
    T_account,
    T_transaction_category,
    T_transaction_type
)
from budgeting_app.transaction_management.core.interfaces.base import CRUDBaseGeneric, JunctionCRUDBaseGeneric
from budgeting_app.transaction_management.core.entities.models import (
    TransactionDataRaw,
    Transaction,
    TransactionCategory,
    TransactionType,
    Account,
    CategoryTransactionJunction,
    DerivedFromJunction
)
from budgeting_app.utils.types import (
    T_nonnegative_float,
    T_posix_timestamp,
    T_normalised_raw_data
)


class TransactionDataRawRepository(CRUDBaseGeneric[TransactionDataRaw, T_transaction_data_raw], metaclass=ABCMeta):
    @abstractmethod
    def create(
        self,
        date: T_posix_timestamp,
        description: str,
        paid_in: T_nonnegative_float,
        paid_out: T_nonnegative_float,
        balance_after_transaction: float,
        account_uuid: T_uuid4_string,
        raw_data: T_normalised_raw_data
    ) -> TransactionDataRaw:
        """
        Create a new TransactionDataRaw object with given Account
        """
        raise NotImplementedError


class TransactionRepository(CRUDBaseGeneric[Transaction, T_transaction], metaclass=ABCMeta):
    @abstractmethod
    def create(
        self,
        paid_amount: float,
        notes: str | None,
        transaction_type_uuid: T_uuid4_string
    ) -> Transaction:
        """
        Create a new Transaction object with given type, categories and parent transactions
        """
        raise NotImplementedError


class TransactionCategoryRepository(CRUDBaseGeneric[TransactionCategory, T_transaction_category], metaclass=ABCMeta):
    pass


class TransactionTypeRepository(CRUDBaseGeneric[TransactionType, T_transaction_type], metaclass=ABCMeta):
    pass


class AccountRepository(CRUDBaseGeneric[Account, T_account], metaclass=ABCMeta):
    pass


class CategoryTransactionJunctionRepository(
    JunctionCRUDBaseGeneric[
        CategoryTransactionJunction
    ],
    metaclass=ABCMeta
):
    @abstractmethod
    def get_by_transaction_uuid(self, uuid: T_uuid4_string) -> list[CategoryTransactionJunction]:
        raise NotImplementedError

    @abstractmethod
    def get_by_category_uuid(self, uuid: T_uuid4_string) -> list[CategoryTransactionJunction]:
        raise NotImplementedError


class DerivedFromJunctionRepository(
    JunctionCRUDBaseGeneric[
        DerivedFromJunction
    ],
    metaclass=ABCMeta
):
    @abstractmethod
    def get_by_transaction_uuid(self, uuid: T_uuid4_string) -> list[DerivedFromJunction]:
        raise NotImplementedError

    @abstractmethod
    def get_by_parent_uuid(self, uuid: T_uuid4_string) -> list[DerivedFromJunction]:
        raise NotImplementedError
