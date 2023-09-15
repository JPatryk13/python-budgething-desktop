from typing import Literal, TypeAlias, TypedDict

from budgeting_app.utils.types import (
    T_uuid4_string,
    T_nonnegative_float,
    T_posix_timestamp,
    T_iso4217_currency_code,
    T_normalised_raw_data
)

##########################
#     COMPLEX TYPES      #
##########################

T_transaction_data_raw: TypeAlias = TypedDict(
    'T_transaction_data_raw',
    {
        'uuid': T_uuid4_string,
        'first_retrieved_at': T_posix_timestamp,
        'last_retrieved_at': T_posix_timestamp,
        'date': T_posix_timestamp,
        'description': str,
        'paid_in': T_nonnegative_float,
        'paid_out': T_nonnegative_float,
        'balance_after_transaction': float,
        'account_uuid': T_uuid4_string,
        'raw_data': T_normalised_raw_data
    },
    total=False
)
T_transaction: TypeAlias = TypedDict(
    'T_transaction',
    {
        'uuid': T_uuid4_string,
        'created_at': T_posix_timestamp,
        'last_updated_at': T_posix_timestamp,
        'paid_amount': float,
        'notes': str | None,
        'transaction_type_uuid': T_uuid4_string | None
    },
    total=False
)
T_account: TypeAlias = TypedDict(
    'T_account',
    {
        'uuid': T_uuid4_string,
        'bank': str,
        'currency': T_iso4217_currency_code
    },
    total=False
)
T_transaction_category: TypeAlias = TypedDict(
    'T_transaction_category',
    {
        'uuid': T_uuid4_string,
        'name': str
    },
    total=False
)
T_transaction_type: TypeAlias = TypedDict(
    'T_transaction_type',
    {
        'uuid': T_uuid4_string,
        'name': str
    },
    total=False
)
T_derived_from_junction: TypeAlias = TypedDict(
    'T_derived_from_junction',
    {
        'transaction_uuid': T_uuid4_string,
        'parent_uuid': T_uuid4_string
    },
    total=False
)
T_category_transaction_junction: TypeAlias = TypedDict(
    'T_category_transaction_junction',
    {
        'transaction_uuid': T_uuid4_string,
        'category_uuid': T_uuid4_string
    },
    total=False
)
