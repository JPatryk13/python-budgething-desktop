import unittest
from uuid import uuid4
from datetime import datetime
import random

from budgeting_app.transaction_management.core.entities.models import TransactionDataRaw


class TestTransactionDataRaw(unittest.TestCase):
    def setUp(self) -> None:
        self.account_a_uuid = str(uuid4())
        self.account_b_uuid = str(uuid4())
        self.data1 = {
            'uuid': str(uuid4()),
            'first_retrieved_at': int(datetime.now().timestamp()),
            'last_retrieved_at': int(datetime.now().timestamp()),
            # transaction a week ago
            'date': int(datetime.now().timestamp()) - 604800,
            'description': 'foo bar',
            'paid_in': 12.99,
            'paid_out': 0.0,
            'balance_after_transaction': 0.0,
            'account_uuid': self.account_a_uuid,
            'raw_data': ['12 Apr 2022', 'foo', 'bar', '', '-12.99', '0']
        }
        self.obj1 = TransactionDataRaw(**self.data1)
        self.data2 = {
            'uuid': str(uuid4()),  # different uuid
            # different first_retrieved_at
            'first_retrieved_at': int(datetime.now().timestamp()),
            # different last_retrieved_at
            'last_retrieved_at': int(datetime.now().timestamp()),
            'date': self.data1["date"],
            'description': self.data1["description"],
            'paid_in': self.data1["paid_in"],
            'paid_out': self.data1["paid_out"],
            'balance_after_transaction': self.data1["balance_after_transaction"],
            'account_uuid': self.data1["account_uuid"],
            # different raw_data
            'raw_data': ['12 Apr 2022', 'foo bar', '', '-12.99', '0']
        }
        self.obj2 = TransactionDataRaw(**self.data2)
        self.data3 = {
            'uuid': str(uuid4()),
            'first_retrieved_at': int(datetime.now().timestamp()),
            'last_retrieved_at': int(datetime.now().timestamp()),
            'date': int(datetime.now().timestamp()) - 302400,  # 3.5 day ago
            'description': 'baz baz baz',
            'paid_in': 1209.0,
            'paid_out': 0.0,
            'balance_after_transaction': 2045.38,
            'account_uuid': self.account_b_uuid,
            # different raw_data
            'raw_data': ['12 Apr 2022', 'baz baz baz', '', '-12.99', '0']
        }
        self.obj3 = TransactionDataRaw(**self.data3)

    #############################
    #    POSITIVE TEST CASES    #
    #############################

    def test_new_valid_input(self):
        obj = TransactionDataRaw.new(
            date=self.data1["date"],
            description=self.data1["description"],
            paid_in=self.data1["paid_in"],
            paid_out=self.data1["paid_out"],
            balance_after_transaction=self.data1["balance_after_transaction"],
            account_uuid=self.account_a_uuid,
            raw_data=self.data1["raw_data"]
        )
        for key in ["date", "description", "paid_in", "paid_out", "balance_after_transaction", "account_uuid", "raw_data"]:
            self.assertEqual(self.data1[key], getattr(obj, key))

    def test_update_valid_input(self):
        for key in self.data1.keys():
            self.obj1.update(key, self.data3[key])
            self.assertEqual(self.data3[key], getattr(self.obj1, key))

    def test_update_from_dict_valid_single_param(self):
        for key in self.data1.keys():
            self.obj1.update_from_dict({key: self.data3[key]})
            self.assertEqual(self.data3[key], getattr(self.obj1, key))

    def test_update_from_dict_valid_multiple_params(self):
        for _ in range(10):
            obj = self.obj1

            # randomise sub-dictionary from data3
            random_num_keys = random.randint(1, len(self.data3))
            keys_to_randomize = random.sample(
                self.data3.keys(), random_num_keys)
            randomized_sub_dict = {
                key: self.data3[key] for key in keys_to_randomize}

            # update obj (self.obj1) with random dict and test it
            obj.update_from_dict(randomized_sub_dict)
            for key in randomized_sub_dict.keys():
                self.assertEqual(self.data3[key], getattr(obj, key))

    def test_to_dict(self):
        d = self.obj1.to_dict()
        self.assertEqual(d, self.data1)

    def test_comparison_same_transaction_properties_different_uuid_etc(self):
        self.assertTrue(self.obj1 == self.obj2)

    def test_comparison_different_transaction_properties(self):
        self.assertFalse(self.obj1 == self.obj3)

    #############################
    #    NEGATIVE TEST CASES    #
    #############################

    def test_update_invalid_param_name(self):
        with self.assertRaises(Exception):
            self.obj1.update('foo', 'bar')

    def test_update_from_dict_invalid_param_name(self):
        data = {
            'date': self.data1['date'],
            'foo': self.data1['description'],
            'balance_after_transaction': self.data1['balance_after_transaction'],
        }
        with self.assertRaises(Exception):
            self.obj1.update_from_dict(data)

    def test_new_invalid_timestamp(self):
        data = {
            'date': -1,
            'description': self.data1['description'],
            'paid_in': self.data1['paid_in'],
            'paid_out': self.data1['paid_out'],
            'balance_after_transaction': self.data1['balance_after_transaction'],
            'account_uuid': self.account_a_uuid,
            'raw_data': self.data1['raw_data']
        }
        with self.assertRaises(TypeError):
            TransactionDataRaw.new(data)

    def test_new_invalid_paid_in(self):
        data = {
            'date': self.data1['date'],
            'description': self.data1['description'],
            'paid_in': -1,
            'paid_out': self.data1['paid_out'],
            'balance_after_transaction': self.data1['balance_after_transaction'],
            'account_uuid': self.account_a_uuid,
            'raw_data': self.data1['raw_data']
        }
        with self.assertRaises(TypeError):
            TransactionDataRaw.new(data)

    def test_new_invalid_paid_out(self):
        data = {
            'date': self.data1['date'],
            'description': self.data1['description'],
            'paid_in': self.data1['paid_in'],
            'paid_out': -1,
            'balance_after_transaction': self.data1['balance_after_transaction'],
            'account_uuid': self.account_a_uuid,
            'raw_data': self.data1['raw_data']
        }
        with self.assertRaises(TypeError):
            TransactionDataRaw.new(data)

    def test_new_invalid_uuid_none(self):
        data = {
            'date': self.data1['date'],
            'description': self.data1['description'],
            'paid_in': self.data1['paid_in'],
            'paid_out': self.data1['paid_out'],
            'balance_after_transaction': self.data1['balance_after_transaction'],
            'account_uuid': None,
            'raw_data': self.data1['raw_data']
        }
        with self.assertRaises(TypeError):
            TransactionDataRaw.new(data)

    def test_new_invalid_uuid_format(self):
        data = {
            'date': self.data1['date'],
            'description': self.data1['description'],
            'paid_in': self.data1['paid_in'],
            'paid_out': self.data1['paid_out'],
            'balance_after_transaction': self.data1['balance_after_transaction'],
            'account_uuid': 'not UUID',
            'raw_data': self.data1['raw_data']
        }
        with self.assertRaises(TypeError):
            TransactionDataRaw.new(data)


if __name__ == "__main__":
    unittest.main()
