import unittest
from uuid import uuid4

from budgeting_app.transaction_management.core.entities.base import TagBaseModel


class TestTransactionTag(unittest.TestCase):
    cls = TagBaseModel

    def setUp(self) -> None:
        self.data1 = {
            'uuid': str(uuid4()),
            'name': 'bar',
        }
        self.obj1 = TagBaseModel(
            uuid=self.data1["uuid"],
            name=self.data1["name"],
        )
        self.data2 = {
            'uuid': str(uuid4()),
            'name': 'bar',
        }
        self.obj2 = TagBaseModel(
            uuid=self.data2["uuid"],
            name=self.data2["name"],
        )
        self.data3 = {
            'uuid': str(uuid4()),
            'name': 'foo',
        }
        self.obj3 = TagBaseModel(
            uuid=self.data3["uuid"],
            name=self.data3["name"],
        )

    #############################
    #    POSITIVE TEST CASES    #
    #############################

    def test_new_valid_input(self):
        obj = TagBaseModel.new(
            name=self.data1["name"]
        )
        self.assertEqual(self.data1["name"], obj.name)

    def test_existing_valid_input(self):
        obj = TagBaseModel.existing(
            uuid=self.data1["uuid"],
            name=self.data1["name"]
        )
        self.assertEqual(self.data1["uuid"], obj.uuid)
        self.assertEqual(self.data1["name"], obj.name)

    def test_update_valid_input(self):
        self.obj1.update('name', 'baz')
        self.assertEqual('baz', self.obj1.name)

    def test_existing_from_dict_valid_input(self):
        obj = TagBaseModel.existing_from_dict(self.data1)
        self.assertEqual(self.data1["uuid"], obj.uuid)
        self.assertEqual(self.data1["name"], obj.name)

    def test_to_dict(self):
        d = self.obj1.to_dict()
        self.assertEqual(d, self.data1)

    def test_comparison_same_transaction_category_properties_different_uuid(self):
        self.assertTrue(self.obj1 == self.obj2)

    def test_comparison_different_transaction_category_properties(self):
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

    def test_existing_from_dict_missing_name(self):
        del self.data1["name"]
        with self.assertRaises(Exception):
            self.obj1.existing_from_dict(self.data1)


if __name__ == "__main__":
    unittest.main()
