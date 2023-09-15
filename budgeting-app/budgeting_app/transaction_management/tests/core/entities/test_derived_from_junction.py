import unittest
from uuid import uuid4

from budgeting_app.transaction_management.core.entities.models import DerivedFromJunction


class TestDerivedFromJunction(unittest.TestCase):
    def test_init_valid_data(self) -> None:
        data = {
            'transaction_uuid': str(uuid4()),
            'parent_uuid': str(uuid4()),
        }
        obj = DerivedFromJunction(
            transaction_uuid=data['transaction_uuid'],
            parent_uuid=data['parent_uuid']
        )
        self.assertEqual(data['parent_uuid'], obj.parent_uuid)
        self.assertEqual(data['transaction_uuid'], obj.transaction_uuid)

    def test_init_invalid_data(self) -> None:
        data = {
            'transaction_uuid': uuid4(),
            'parent_uuid': str(uuid4()),
        }
        with self.assertRaises(Exception):
            DerivedFromJunction(
                transaction_uuid=data['transaction_uuid'],
                parent_uuid=data['parent_uuid']
            )


if __name__ == "__main__":
    unittest.main()
