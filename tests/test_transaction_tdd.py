from datetime import datetime, timezone
from uuid import UUID, uuid4
from unittest.mock import patch

from app.schemas.transaction import TransactionCreate
from app.services.transaction_svc import create_transaction


def test_create_transaction_persists_pending_transaction():
    class FakeDbSession:
        def __init__(self):
            self.add_called = False
            self.commit_called = False
            self.refresh_called = False
            self.saved_object = None

        def add(self, obj):
            self.add_called = True
            self.saved_object = obj

        def commit(self):
            self.commit_called = True

        def refresh(self, obj):
            self.refresh_called = True
            obj.id = uuid4()
            obj.created_at = datetime.now(timezone.utc)

    db = FakeDbSession()

    payload = TransactionCreate(
        user_id="user-001",
        merchant_id="merchant-001",
        amount=500.0,
        currency="INR",
    )

    with patch("app.services.transaction_svc.publish_transaction_initiated") as mock_publish:
        transaction = create_transaction(db, payload)

    UUID(str(transaction.id))
    assert transaction.user_id == "user-001"
    assert transaction.merchant_id == "merchant-001"
    assert transaction.amount == 500.0
    assert transaction.currency == "INR"
    assert transaction.status == "PENDING"

    assert db.add_called is True
    assert db.commit_called is True
    assert db.refresh_called is True
    assert db.saved_object is transaction

    mock_publish.assert_called_once_with(transaction)
