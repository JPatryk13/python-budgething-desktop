import unittest
from uuid import uuid4

from budgeting_app.transaction_management.core.entities.models import Account


class TestAccount(unittest.TestCase):
    def setUp(self) -> None:
        self.data1 = {
            'uuid': str(uuid4()),
            'bank': 'foo',
            'currency': 'BAR'
        }
        self.obj1 = Account(
            uuid=self.data1["uuid"],
            bank=self.data1["bank"],
            currency=self.data1["currency"]
        )
        self.data2 = {
            'uuid': str(uuid4()),
            'bank': 'foo',
            'currency': 'BAR'
        }
        self.obj2 = Account(
            uuid=self.data2["uuid"],
            bank=self.data2["bank"],
            currency=self.data2["currency"]
        )
        self.data3 = {
            'uuid': str(uuid4()),
            'bank': 'baz',
            'currency': 'QUX'
        }
        self.obj3 = Account(
            uuid=self.data3["uuid"],
            bank=self.data3["bank"],
            currency=self.data3["currency"]
        )

    #############################
    #    POSITIVE TEST CASES    #
    #############################

    def test_new_valid_input(self):
        obj = Account.new(
            bank=self.data1["bank"],
            currency=self.data1["currency"]
        )
        self.assertEqual(self.data1["bank"], obj.bank)
        self.assertEqual(self.data1["currency"], obj.currency)

    def test_existing_valid_input(self):
        obj = Account.existing(
            uuid=self.data1["uuid"],
            bank=self.data1["bank"],
            currency=self.data1["currency"]
        )
        self.assertEqual(self.data1["uuid"], obj.uuid)
        self.assertEqual(self.data1["bank"], obj.bank)
        self.assertEqual(self.data1["currency"], obj.currency)

    def test_update_valid_input(self):
        self.obj1.update('bank', 'new bank')
        self.assertEqual('new bank', self.obj1.bank)

    def test_existing_from_dict_valid_input(self):
        obj = Account.existing_from_dict(self.data1)
        self.assertEqual(self.data1["uuid"], obj.uuid)
        self.assertEqual(self.data1["bank"], obj.bank)
        self.assertEqual(self.data1["currency"], obj.currency)

    def test_to_dict(self):
        d = self.obj1.to_dict()
        self.assertEqual(d, self.data1)

    def test_comparison_same_account_properties_different_uuid(self):
        self.assertTrue(self.obj1 == self.obj2)

    def test_comparison_different_account_properties(self):
        self.assertFalse(self.obj1 == self.obj3)

    #############################
    #    NEGATIVE TEST CASES    #
    #############################

    def test_update_invalid_param_name(self):
        with self.assertRaises(Exception):
            self.obj1.update('foo', 'bar')

    def test_existing_from_dict_missing_uuid(self):
        del self.data1["uuid"]
        with self.assertRaises(Exception):
            self.obj1.existing_from_dict(self.data1)

    def test_existing_from_dict_missing_bank(self):
        del self.data1["bank"]
        with self.assertRaises(Exception):
            self.obj1.existing_from_dict(self.data1)

    def test_existing_from_dict_missing_currency(self):
        del self.data1["currency"]
        with self.assertRaises(Exception):
            self.obj1.existing_from_dict(self.data1)

    def test_new_invalid_currency_four_chars(self):
        data = {
            'bank': 'foo',
            'currency': 'BAZZ'
        }
        with self.assertRaises(TypeError):
            Account.new(**data)

    def test_new_invalid_currency_lower_case(self):
        data = {
            'bank': 'foo',
            'currency': 'baz'
        }
        with self.assertRaises(TypeError):
            Account.new(**data)

    def test_existing_invalid_currency(self):
        data = {
            'bank': 'foo',
            'currency': 'bazz'
        }
        with self.assertRaises(TypeError):
            Account.existing(**data)

    def test_update_invalid_currency(self):
        with self.assertRaises(TypeError):
            self.obj1.update('currency', 'bazz')


if __name__ == "__main__":
    unittest.main()
