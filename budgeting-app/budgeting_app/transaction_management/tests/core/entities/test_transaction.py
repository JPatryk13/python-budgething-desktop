from datetime import datetime
import time
import unittest
from uuid import uuid4

from budgeting_app.transaction_management.core.entities.models import Transaction


class TestTransaction(unittest.TestCase):
    def setUp(self):
        # Create two different Transaction objects
        self.transaction_data1 = {
            'uuid': str(uuid4()),
            'created_at': int(datetime.now().timestamp()),
            'last_updated_at': int(datetime.now().timestamp()),
            'paid_amount': -129.01,
            'notes': "foo foo bar foo",
            'transaction_type_uuid': None,
        }
        # derived from transaction_data_raw_obj1
        self.transaction_obj1 = Transaction(**self.transaction_data1)
        self.transaction_data2 = {
            'uuid': str(uuid4()),
            'created_at': int(datetime.now().timestamp()),
            'last_updated_at': int(datetime.now().timestamp()),
            'paid_amount': 32.66,
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
        }
        # derived from transaction_obj1 and transaction_data_raw_obj2
        self.transaction_obj2 = Transaction(**self.transaction_data2)

    #############################
    #    POSITIVE TEST CASES    #
    #############################

    # def test_get_paid_amount_no_parent_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_single_parent_raw_data_no_paid_amount(self) -> None:
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[self.transaction_data_raw_obj1],
    #         paid_amount=None
    #     )
    #     expected = -12.99
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_single_parent_raw_data_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[self.transaction_data_raw_obj1],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_single_parent_transaction_no_paid_amount(self) -> None:
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[self.transaction_obj1],
    #         paid_amount=None
    #     )
    #     expected = self.transaction_data1["paid_amount"]
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_single_parent_transaction_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[self.transaction_obj1],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_two_parenents_raw_data_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[
    #             self.transaction_data_raw_obj1, self.transaction_data_raw_obj2],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_two_parenents_transaction_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[
    #             self.transaction_obj1, self.transaction_obj2],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_paid_amount_two_parenents_mixed_paid_amount_set(self) -> None:
    #     paid_amount = 17.49
    #     actual = Transaction._get_paid_amount(
    #         parent_transactions=[
    #             self.transaction_obj1, self.transaction_data_raw_obj2],
    #         paid_amount=paid_amount
    #     )
    #     expected = paid_amount
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_no_type_no_category(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=None, transaction_category=[]
    #     )
    #     expected = (None, [])
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_no_type_single_category(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=None, transaction_category=[self.category_obj1]
    #     )
    #     expected = (None, [self.category_data1["uuid"]])
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_no_type_two_categories(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=None, transaction_category=[self.category_obj1, self.category_obj2]
    #     )
    #     expected = (None, [self.category_data1["uuid"],
    #                 self.category_data2["uuid"]])
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_single_type_no_category(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=self.type_obj, transaction_category=[]
    #     )
    #     expected = (self.type_data["uuid"], [])
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_single_type_single_category(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=self.type_obj, transaction_category=[
    #             self.category_obj1]
    #     )
    #     expected = (self.type_data["uuid"], [self.category_data1["uuid"]])
    #     self.assertEqual(expected, actual)

    # def test_get_category_and_type_uuid_single_type_two_categories(self) -> None:
    #     actual = Transaction._get_category_and_type_uuid(
    #         transaction_type=self.type_obj, transaction_category=[
    #             self.category_obj1, self.category_obj2]
    #     )
    #     expected = (self.type_data["uuid"], [
    #                 self.category_data1["uuid"], self.category_data2["uuid"]])
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_no_parent_transaction(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[]
    #     )
    #     expected = []
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_single_parent_transaction_raw_data(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[self.transaction_data_raw_obj1]
    #     )
    #     expected: list[DerivedFrom] = [
    #         {
    #             'entity_name': 'TransactionDataRaw',
    #             'entity_uuid': self.transaction_data_raw_data1["uuid"]
    #         }
    #     ]
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_single_parent_transaction_normal(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[self.transaction_obj1]
    #     )
    #     expected: list[DerivedFrom] = [
    #         {
    #             'entity_name': 'Transaction',
    #             'entity_uuid': self.transaction_data1["uuid"]
    #         }
    #     ]
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_two_parent_transactions_raw_data(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[
    #             self.transaction_data_raw_obj1,
    #             self.transaction_data_raw_obj2
    #         ]
    #     )
    #     expected: list[DerivedFrom] = [
    #         {
    #             'entity_name': 'TransactionDataRaw',
    #             'entity_uuid': self.transaction_data_raw_data1["uuid"]
    #         },
    #         {
    #             'entity_name': 'TransactionDataRaw',
    #             'entity_uuid': self.transaction_data_raw_data2["uuid"]
    #         }
    #     ]
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_two_parent_transactions_normal(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[
    #             self.transaction_obj1,
    #             self.transaction_obj2
    #         ]
    #     )
    #     expected: list[DerivedFrom] = [
    #         {
    #             'entity_name': 'Transaction',
    #             'entity_uuid': self.transaction_data1["uuid"]
    #         },
    #         {
    #             'entity_name': 'Transaction',
    #             'entity_uuid': self.transaction_data2["uuid"]
    #         }
    #     ]
    #     self.assertEqual(expected, actual)

    # def test_get_derived_from_two_parent_transactions_mixed(self) -> None:
    #     actual = Transaction._get_derived_from(
    #         parent_transactions=[
    #             self.transaction_obj1,
    #             self.transaction_data_raw_obj2
    #         ]
    #     )
    #     expected: list[DerivedFrom] = [
    #         {
    #             'entity_name': 'Transaction',
    #             'entity_uuid': self.transaction_data1["uuid"]
    #         },
    #         {
    #             'entity_name': 'TransactionDataRaw',
    #             'entity_uuid': self.transaction_data_raw_data2["uuid"]
    #         }
    #     ]
    #     self.assertEqual(expected, actual)

    def test_new_only_paid_amount(self) -> None:
        obj = Transaction.new(
            paid_amount=17.49
        )
        expected = {
            'paid_amount': 17.49,
            'notes': None,
            'transaction_type_uuid': None,
        }
        for key in expected.keys():
            self.assertEqual(expected[key], getattr(obj, key))

    def test_new_negative_paid_amount(self) -> None:
        obj = Transaction.new(
            paid_amount=-17.49
        )
        expected = {
            'paid_amount': -17.49,
            'notes': None,
            'transaction_type_uuid': None,
        }
        for key in expected.keys():
            self.assertEqual(expected[key], getattr(obj, key))

    def test_existing_valid_input(self) -> None:
        obj = Transaction.existing(**self.transaction_data1)
        for key in self.transaction_data1.keys():
            self.assertEqual(self.transaction_data1[key], getattr(obj, key))

    def test_update_valid_input(self) -> None:
        for key in self.transaction_data1.keys():
            obj = self.transaction_obj1
            obj.update(
                param=key,
                value=self.transaction_data2[key]
            )
            self.assertEqual(self.transaction_data2[key], getattr(
                self.transaction_obj1, key))

    def test_new_from_dict_valid_input(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
        }
        obj = Transaction.new_form_dict(data)
        for key, val in data.items():
            self.assertEqual(val, getattr(obj, key))

    def test_existing_from_dict_valid_input(self) -> None:
        obj = Transaction.existing_from_dict(self.transaction_data1)
        for key, val in self.transaction_data1.items():
            self.assertEqual(val, getattr(obj, key))

    def test_update_from_dict_valid_input(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
        }
        last_updated_at = self.transaction_obj1.last_updated_at
        time.sleep(1)
        self.transaction_obj1.update_from_dict(data)
        for key, val in data.items():
            self.assertEqual(val, getattr(self.transaction_obj1, key))
        self.assertGreater(
            self.transaction_obj1.last_updated_at, last_updated_at)

    #############################
    #    NEGATIVE TEST CASES    #
    #############################

    def test_new_invalid_paid_amount(self) -> None:
        data = {
            'paid_amount': '-25.01',
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
        }
        with self.assertRaises(TypeError):
            Transaction.new(**data)

    def test_new_invalid_notes(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': 6,
            'transaction_type_uuid': str(uuid4()),
        }
        with self.assertRaises(TypeError):
            Transaction.new(**data)

    def test_new_invalid_transaction_type_uuid(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': None,
            'transaction_type_uuid': uuid4(),
        }
        with self.assertRaises(TypeError):
            Transaction.new(**data)

    def test_update_invalid_param_name(self) -> None:
        with self.assertRaises(Exception):
            self.transaction_obj1.update('invelid_param', 4)

    def test_new_from_dict_missing_fields(self) -> None:
        data = {
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
        }
        with self.assertRaises(Exception):
            Transaction.new_form_dict(data)

    def test_new_from_dict_extra_fields(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
            'invalid_field': 4
        }
        with self.assertRaises(Exception):
            Transaction.new_form_dict(data)

    def test_existing_from_dict_missing_fields(self) -> None:
        del self.transaction_data1['paid_amount']
        with self.assertRaises(Exception):
            Transaction.existing_from_dict(self.transaction_data1)

    def test_existing_from_dict_extra_fields(self) -> None:
        self.transaction_data1['invalid_field'] = 4
        with self.assertRaises(Exception):
            Transaction.existing_from_dict(self.transaction_data1)

    def test_update_from_dict_invalid_param_name(self) -> None:
        data = {
            'paid_amount': -25.01,
            'notes': None,
            'transaction_type_uuid': str(uuid4()),
            'invalid_field': 4
        }
        with self.assertRaises(Exception):
            Transaction.update_from_dict(data)


if __name__ == "__main__":
    unittest.main()
