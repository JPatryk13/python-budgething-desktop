import unittest
from uuid import uuid4

from budgeting_app.transaction_management.core.entities.models import CategoryTransactionJunction


class TestCategoryTransactionJunction(unittest.TestCase):
    def test_init_valid_data(self) -> None:
        data = {
            'transaction_uuid': str(uuid4()),
            'category_uuid': str(uuid4()),
        }
        obj = CategoryTransactionJunction(
            transaction_uuid=data['transaction_uuid'],
            category_uuid=data['category_uuid']
        )
        self.assertEqual(data['category_uuid'], obj.category_uuid)
        self.assertEqual(data['transaction_uuid'], obj.transaction_uuid)

    def test_init_invalid_data(self) -> None:
        data = {
            'transaction_uuid': uuid4(),
            'category_uuid': str(uuid4()),
        }
        with self.assertRaises(Exception):
            CategoryTransactionJunction(
                transaction_uuid=data['transaction_uuid'],
                category_uuid=data['category_uuid']
            )


if __name__ == "__main__":
    unittest.main()
