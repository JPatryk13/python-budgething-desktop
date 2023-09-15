from dataclasses import dataclass, asdict, field
from typing import Any
from uuid import uuid4
from datetime import datetime

from .base import TagBaseModel
from .types import (
    T_iso4217_currency_code,
    T_nonnegative_float,
    T_posix_timestamp,
    T_normalised_raw_data,
    T_uuid4_string,
    T_transaction_data_raw,
    T_transaction,
    T_account,
    T_derived_from_junction,
    T_category_transaction_junction,
    T_transaction_category,
    T_transaction_type
)
from budgeting_app.utils.validators import (
    is_iso4217_currency_code,
    is_nonnegative_float,
    is_posix_timestamp,
    is_normalised_raw_data,
    is_uuid4_string
)


@dataclass
class TransactionDataRaw:
    uuid: T_uuid4_string = field(compare=False)
    created_at: T_posix_timestamp = field(compare=False)
    last_updated_at: T_posix_timestamp = field(compare=False)

    date: T_posix_timestamp
    description: str
    paid_in: T_nonnegative_float
    paid_out: T_nonnegative_float
    balance_after_transaction: float

    account_uuid: T_uuid4_string
    raw_data: T_normalised_raw_data = field(compare=False)

    def __post_init__(self):
        self.__validate()

    def __validate(self) -> None:
        if not is_posix_timestamp(self.date):
            raise TypeError
        if not is_nonnegative_float(self.paid_in):
            raise TypeError
        if not is_nonnegative_float(self.paid_out):
            raise TypeError
        if not is_uuid4_string(self.account_uuid):
            raise TypeError
        if not is_normalised_raw_data(self.raw_data):
            raise TypeError

    @classmethod
    def new(
        cls,
        date: T_posix_timestamp,
        description: str,
        paid_in: T_nonnegative_float,
        paid_out: T_nonnegative_float,
        balance_after_transaction: float,
        account_uuid: T_uuid4_string,
        raw_data: T_normalised_raw_data
    ):
        uuid = str(uuid4())
        created_at = int(datetime.now().timestamp())
        last_updated_at = int(datetime.now().timestamp())

        return cls(
            uuid=uuid,
            created_at=created_at,
            last_updated_at=last_updated_at,
            date=date,
            description=description,
            paid_in=paid_in,
            paid_out=paid_out,
            balance_after_transaction=balance_after_transaction,
            account_uuid=account_uuid,
            raw_data=raw_data
        )

    def update(self, param: str, value: Any) -> None:
        # setattr doesn't throw an error on its own lol
        if (param in self.to_dict().keys()):
            setattr(self, param, value)
            self.__validate()
            self.last_updated_at = int(datetime.now().timestamp())
        else:
            raise ValueError(
                f'{param} is not a parameter of class TransactionDataRaw.')

    def to_dict(self) -> T_transaction_data_raw:
        return asdict(self)


@dataclass
class Transaction:
    uuid: T_uuid4_string
    created_at: T_posix_timestamp
    last_updated_at: T_posix_timestamp

    paid_amount: float
    notes: str | None = field(default=None)  # manually added notes
    # salary, gift, bills, subscriptions, purchases, transfer between accounts
    transaction_type_uuid: T_uuid4_string | None = field(default=None)

    def __post_init__(self):
        self.__validate()

    def __validate(self) -> None:
        if not is_nonnegative_float(self.paid_amount):
            raise TypeError
        if not isinstance(self.notes, str) and self.notes is not None:
            raise TypeError
        if not is_uuid4_string(self.transaction_type_uuid) and self.transaction_type_uuid is not None:
            raise TypeError

    @classmethod
    def new(
        cls,
        paid_amount: T_nonnegative_float,
        notes: str | None = None,
        transaction_type_uuid: T_uuid4_string | None = None
    ):
        uuid = str(uuid4())
        created_at = int(datetime.now().timestamp())
        last_updated_at = int(datetime.now().timestamp())

        return cls(
            uuid=uuid,
            created_at=created_at,
            last_updated_at=last_updated_at,
            paid_amount=paid_amount,
            notes=notes,
            transaction_type_uuid=transaction_type_uuid
        )

    def update(self, param: str, value: Any) -> None:
        if (param in self.to_dict().keys()):
            setattr(self, param, value)
            self.__validate()
            self.last_updated_at = int(datetime.now().timestamp())
        else:
            raise ValueError(
                f'{param} is not a parameter of class Transaction.')

    def to_dict(self) -> T_transaction:
        return asdict(self)


@dataclass
class Account:

    uuid: T_uuid4_string = field(compare=False)
    bank: str
    currency: T_iso4217_currency_code

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        if not isinstance(self.bank, str):
            raise TypeError
        if not is_iso4217_currency_code(self.currency):
            raise TypeError

    @classmethod
    def new(cls, bank: str, currency: T_iso4217_currency_code):
        """
        Create a new object - generates UID
        """
        return cls(
            uuid=str(uuid4()),
            bank=bank,
            currency=currency
        )

    def update(self, param: str, value: Any) -> None:
        if (param in self.to_dict().keys()):
            setattr(self, param, value)
            self.__validate()
        else:
            raise ValueError(
                f'{param} is not a parameter of class Account.')

    def to_dict(self) -> T_account:
        return asdict(self)


@dataclass
class TransactionCategory(TagBaseModel[T_transaction_category]):
    pass


@dataclass
class TransactionType(TagBaseModel[T_transaction_type]):
    pass


@dataclass
class DerivedFromJunction:
    transaction_uuid: T_uuid4_string
    parent_uuid: T_uuid4_string

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        if not is_uuid4_string(self.transaction_uuid):
            raise TypeError
        if not is_uuid4_string(self.parent_uuid):
            raise TypeError

    def to_dict(self) -> T_derived_from_junction:
        return asdict(self)


@dataclass
class CategoryTransactionJunction:
    transaction_uuid: T_uuid4_string = field()
    category_uuid: T_uuid4_string

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        if not is_uuid4_string(self.transaction_uuid):
            raise TypeError
        if not is_uuid4_string(self.category_uuid):
            raise TypeError

    def to_dict(self) -> T_category_transaction_junction:
        return asdict(self)
