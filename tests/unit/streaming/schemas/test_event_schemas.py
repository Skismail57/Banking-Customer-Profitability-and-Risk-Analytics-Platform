"""Unit tests for event schemas.

This module tests the Pydantic event schemas for streaming infrastructure.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from src.streaming.schemas import (
    TransactionEvent,
    AccountUpdateEvent,
    CustomerUpdateEvent,
    LoanApplicationEvent,
    PaymentEvent,
    BaseEvent,
    EventType,
    create_event,
    get_event_schema_version,
)


class TestEventType:
    """Test EventType enum."""
    
    def test_event_type_values(self):
        """Test that EventType enum has correct values."""
        assert EventType.TRANSACTION == "transaction"
        assert EventType.ACCOUNT_UPDATE == "account_update"
        assert EventType.CUSTOMER_UPDATE == "customer_update"
        assert EventType.LOAN_APPLICATION == "loan_application"
        assert EventType.PAYMENT == "payment"


class TestBaseEvent:
    """Test BaseEvent model."""
    
    def test_base_event_creation(self):
        """Test creating a base event."""
        event = BaseEvent(
            event_id="evt_123",
            event_type=EventType.TRANSACTION,
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="core_banking"
        )
        assert event.event_id == "evt_123"
        assert event.event_type == EventType.TRANSACTION
        assert event.customer_key is None
        assert event.source_system == "core_banking"
    
    def test_event_timestamp_auto_ingestion(self):
        """Test that ingestion_timestamp is auto-generated."""
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        event = BaseEvent(
            event_id="evt_123",
            event_type=EventType.TRANSACTION,
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="core_banking"
        )
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        assert before <= event.ingestion_timestamp <= after
    
    def test_event_timestamp_cannot_be_future(self):
        """Test that event timestamp cannot be in the future."""
        future_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1)
        with pytest.raises(ValueError, match="Event timestamp cannot be in the future"):
            BaseEvent(
                event_id="evt_123",
                event_type=EventType.TRANSACTION,
                event_timestamp=future_time,
                source_system="core_banking"
            )
    
    def test_event_timestamp_cannot_be_too_old(self):
        """Test that event timestamp cannot be too old."""
        old_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=400)
        with pytest.raises(ValueError, match="Event timestamp is too old"):
            BaseEvent(
                event_id="evt_123",
                event_type=EventType.TRANSACTION,
                event_timestamp=old_time,
                source_system="core_banking"
            )


class TestTransactionEvent:
    """Test TransactionEvent model."""
    
    def test_transaction_event_creation(self):
        """Test creating a transaction event."""
        event = TransactionEvent(
            event_id="evt_txn_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="core_banking",
            customer_key="cust_123",
            transaction_id="txn_456",
            transaction_type="purchase",
            channel="online",
            amount=Decimal("100.50"),
            currency="USD"
        )
        assert event.event_type == EventType.TRANSACTION
        assert event.transaction_id == "txn_456"
        assert event.transaction_type == "purchase"
        assert event.amount == Decimal("100.50")
    
    def test_transaction_event_type_validation(self):
        """Test transaction type validation."""
        valid_types = ["purchase", "payment", "transfer", "withdrawal", "deposit", "refund"]
        for t in valid_types:
            event = TransactionEvent(
                event_id="evt_txn_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                transaction_id="txn_456",
                transaction_type=t,
                channel="online",
                amount=Decimal("100.50")
            )
            assert event.transaction_type == t
    
    def test_transaction_event_invalid_type(self):
        """Test that invalid transaction type raises error."""
        with pytest.raises(ValueError, match="Invalid transaction type"):
            TransactionEvent(
                event_id="evt_txn_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                transaction_id="txn_456",
                transaction_type="invalid",
                channel="online",
                amount=Decimal("100.50")
            )
    
    def test_transaction_channel_validation(self):
        """Test channel validation."""
        valid_channels = ["online", "mobile", "branch", "ATM", "phone"]
        for c in valid_channels:
            event = TransactionEvent(
                event_id="evt_txn_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                transaction_id="txn_456",
                transaction_type="purchase",
                channel=c,
                amount=Decimal("100.50")
            )
            assert event.channel == c
    
    def test_transaction_invalid_channel(self):
        """Test that invalid channel raises error."""
        with pytest.raises(ValueError, match="Invalid channel"):
            TransactionEvent(
                event_id="evt_txn_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                transaction_id="txn_456",
                transaction_type="purchase",
                channel="invalid",
                amount=Decimal("100.50")
            )
    
    def test_transaction_amount_must_be_positive(self):
        """Test that transaction amount must be positive."""
        with pytest.raises(ValueError, match="ensure this value is greater than 0"):
            TransactionEvent(
                event_id="evt_txn_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                transaction_id="txn_456",
                transaction_type="purchase",
                channel="online",
                amount=Decimal("-100.50")
            )


class TestAccountUpdateEvent:
    """Test AccountUpdateEvent model."""
    
    def test_account_update_creation(self):
        """Test creating an account update event."""
        event = AccountUpdateEvent(
            event_id="evt_acc_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="core_banking",
            account_key="acc_456",
            account_id="ACC123",
            customer_key="cust_789",
            update_type="balance_change",
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("900.00")
        )
        assert event.event_type == EventType.ACCOUNT_UPDATE
        assert event.account_key == "acc_456"
        assert event.update_type == "balance_change"
    
    def test_account_update_balance_change_requires_amounts(self):
        """Test that balance change requires previous and new balance."""
        with pytest.raises(ValueError, match="Balance change requires"):
            AccountUpdateEvent(
                event_id="evt_acc_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                account_key="acc_456",
                account_id="ACC123",
                customer_key="cust_789",
                update_type="balance_change"
            )
    
    def test_account_update_status_change_requires_statuses(self):
        """Test that status change requires previous and new status."""
        with pytest.raises(ValueError, match="Status change requires"):
            AccountUpdateEvent(
                event_id="evt_acc_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                account_key="acc_456",
                account_id="ACC123",
                customer_key="cust_789",
                update_type="status_change"
            )
    
    def test_account_update_limit_change_requires_limits(self):
        """Test that limit change requires previous and new limit."""
        with pytest.raises(ValueError, match="Limit change requires"):
            AccountUpdateEvent(
                event_id="evt_acc_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="core_banking",
                account_key="acc_456",
                account_id="ACC123",
                customer_key="cust_789",
                update_type="limit_change"
            )


class TestCustomerUpdateEvent:
    """Test CustomerUpdateEvent model."""
    
    def test_customer_update_creation(self):
        """Test creating a customer update event."""
        event = CustomerUpdateEvent(
            event_id="evt_cust_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="crm",
            customer_key="cust_456",
            customer_id="CUST123",
            update_type="profile_change",
            updated_fields=["email", "phone"],
            email="new.email@example.com",
            phone="555-1234"
        )
        assert event.event_type == EventType.CUSTOMER_UPDATE
        assert event.customer_key == "cust_456"
        assert event.update_type == "profile_change"
    
    def test_customer_update_segment_change(self):
        """Test customer segment change."""
        event = CustomerUpdateEvent(
            event_id="evt_cust_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="crm",
            customer_key="cust_456",
            customer_id="CUST123",
            update_type="segment_change",
            previous_segment="segment_a",
            new_segment="segment_b"
        )
        assert event.previous_segment == "segment_a"
        assert event.new_segment == "segment_b"


class TestLoanApplicationEvent:
    """Test LoanApplicationEvent model."""
    
    def test_loan_application_creation(self):
        """Test creating a loan application event."""
        event = LoanApplicationEvent(
            event_id="evt_loan_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="lending",
            application_id="APP123",
            customer_key="cust_456",
            customer_id="CUST123",
            product_key="prod_789",
            loan_amount=Decimal("50000.00"),
            loan_purpose="home_improvement",
            loan_term_months=60,
            application_status="submitted",
            credit_score=720,
            annual_income=Decimal("75000.00")
        )
        assert event.event_type == EventType.LOAN_APPLICATION
        assert event.application_id == "APP123"
        assert event.loan_amount == Decimal("50000.00")
    
    def test_loan_application_status_validation(self):
        """Test application status validation."""
        valid_statuses = ["submitted", "under_review", "approved", "rejected", "cancelled"]
        for s in valid_statuses:
            event = LoanApplicationEvent(
                event_id="evt_loan_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                application_id="APP123",
                customer_key="cust_456",
                customer_id="CUST123",
                product_key="prod_789",
                loan_amount=Decimal("50000.00"),
                loan_purpose="home_improvement",
                loan_term_months=60,
                application_status=s
            )
            assert event.application_status == s
    
    def test_loan_application_invalid_status(self):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError, match="Invalid application status"):
            LoanApplicationEvent(
                event_id="evt_loan_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                application_id="APP123",
                customer_key="cust_456",
                customer_id="CUST123",
                product_key="prod_789",
                loan_amount=Decimal("50000.00"),
                loan_purpose="home_improvement",
                loan_term_months=60,
                application_status="invalid"
            )
    
    def test_credit_score_range(self):
        """Test credit score range validation."""
        # Valid score
        event = LoanApplicationEvent(
            event_id="evt_loan_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="lending",
            application_id="APP123",
            customer_key="cust_456",
            customer_id="CUST123",
            product_key="prod_789",
            loan_amount=Decimal("50000.00"),
            loan_purpose="home_improvement",
            loan_term_months=60,
            application_status="submitted",
            credit_score=720
        )
        assert event.credit_score == 720
        
        # Invalid score (too low)
        with pytest.raises(ValueError, match="ensure this value is greater than or equal to 300"):
            LoanApplicationEvent(
                event_id="evt_loan_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                application_id="APP123",
                customer_key="cust_456",
                customer_id="CUST123",
                product_key="prod_789",
                loan_amount=Decimal("50000.00"),
                loan_purpose="home_improvement",
                loan_term_months=60,
                application_status="submitted",
                credit_score=250
            )
        
        # Invalid score (too high)
        with pytest.raises(ValueError, match="ensure this value is less than or equal to 850"):
            LoanApplicationEvent(
                event_id="evt_loan_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                application_id="APP123",
                customer_key="cust_456",
                customer_id="CUST123",
                product_key="prod_789",
                loan_amount=Decimal("50000.00"),
                loan_purpose="home_improvement",
                loan_term_months=60,
                application_status="submitted",
                credit_score=900
            )


class TestPaymentEvent:
    """Test PaymentEvent model."""
    
    def test_payment_event_creation(self):
        """Test creating a payment event."""
        payment_date = datetime.now(timezone.utc).replace(tzinfo=None)
        due_date = payment_date - timedelta(days=5)
        
        event = PaymentEvent(
            event_id="evt_pay_123",
            event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            source_system="lending",
            payment_id="PAY123",
            customer_key="cust_456",
            customer_id="CUST123",
            loan_key="loan_789",
            payment_date=payment_date,
            due_date=due_date,
            payment_amount=Decimal("500.00"),
            payment_type="principal",
            payment_status="completed"
        )
        assert event.event_type == EventType.PAYMENT
        assert event.payment_id == "PAY123"
        assert event.payment_amount == Decimal("500.00")
    
    def test_payment_type_validation(self):
        """Test payment type validation."""
        valid_types = ["principal", "interest", "fee", "penalty"]
        for t in valid_types:
            event = PaymentEvent(
                event_id="evt_pay_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                payment_id="PAY123",
                customer_key="cust_456",
                customer_id="CUST123",
                payment_date=datetime.now(timezone.utc).replace(tzinfo=None),
                due_date=datetime.now(timezone.utc).replace(tzinfo=None),
                payment_amount=Decimal("500.00"),
                payment_type=t,
                payment_status="completed"
            )
            assert event.payment_type == t
    
    def test_payment_status_validation(self):
        """Test payment status validation."""
        valid_statuses = ["scheduled", "processing", "completed", "failed", "returned"]
        for s in valid_statuses:
            event = PaymentEvent(
                event_id="evt_pay_123",
                event_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                source_system="lending",
                payment_id="PAY123",
                customer_key="cust_456",
                customer_id="CUST123",
                payment_date=datetime.now(timezone.utc).replace(tzinfo=None),
                due_date=datetime.now(timezone.utc).replace(tzinfo=None),
                payment_amount=Decimal("500.00"),
                payment_type="principal",
                payment_status=s
            )
            assert event.payment_status == s


class TestCreateEvent:
    """Test create_event factory function."""
    
    def test_create_transaction_event(self):
        """Test creating a transaction event via factory."""
        event_data = {
            "event_id": "evt_txn_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "transaction_id": "txn_456",
            "transaction_type": "purchase",
            "channel": "online",
            "amount": "100.50"
        }
        event = create_event(event_data)
        assert isinstance(event, TransactionEvent)
        assert event.transaction_id == "txn_456"
    
    def test_create_account_update_event(self):
        """Test creating an account update event via factory."""
        event_data = {
            "event_id": "evt_acc_123",
            "event_type": EventType.ACCOUNT_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "account_key": "acc_456",
            "account_id": "ACC123",
            "customer_key": "cust_789",
            "update_type": "balance_change",
            "previous_balance": "1000.00",
            "new_balance": "900.00"
        }
        event = create_event(event_data)
        assert isinstance(event, AccountUpdateEvent)
        assert event.account_key == "acc_456"
    
    def test_create_customer_update_event(self):
        """Test creating a customer update event via factory."""
        event_data = {
            "event_id": "evt_cust_123",
            "event_type": EventType.CUSTOMER_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "crm",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "update_type": "profile_change",
            "updated_fields": ["email"]
        }
        event = create_event(event_data)
        assert isinstance(event, CustomerUpdateEvent)
        assert event.customer_key == "cust_456"
    
    def test_create_loan_application_event(self):
        """Test creating a loan application event via factory."""
        event_data = {
            "event_id": "evt_loan_123",
            "event_type": EventType.LOAN_APPLICATION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "application_id": "APP123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "product_key": "prod_789",
            "loan_amount": "50000.00",
            "loan_purpose": "home_improvement",
            "loan_term_months": 60,
            "application_status": "submitted"
        }
        event = create_event(event_data)
        assert isinstance(event, LoanApplicationEvent)
        assert event.application_id == "APP123"
    
    def test_create_payment_event(self):
        """Test creating a payment event via factory."""
        event_data = {
            "event_id": "evt_pay_123",
            "event_type": EventType.PAYMENT,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "payment_id": "PAY123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "payment_date": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "due_date": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "payment_amount": "500.00",
            "payment_type": "principal",
            "payment_status": "completed"
        }
        event = create_event(event_data)
        assert isinstance(event, PaymentEvent)
        assert event.payment_id == "PAY123"
    
    def test_create_event_invalid_type(self):
        """Test that invalid event type raises error."""
        event_data = {
            "event_id": "evt_123",
            "event_type": "invalid_type",
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "test"
        }
        with pytest.raises(ValueError, match="Invalid event type"):
            create_event(event_data)


class TestGetEventSchemaVersion:
    """Test get_event_schema_version function."""
    
    def test_get_schema_version_for_all_types(self):
        """Test getting schema version for all event types."""
        for event_type in EventType:
            version = get_event_schema_version(event_type)
            assert version == "v1"
    
    def test_get_schema_version_unknown_type(self):
        """Test getting schema version for unknown type returns default."""
        from src.streaming.schemas.event_schemas import get_event_schema_version
        # Pass a string that's not in the enum
        version = get_event_schema_version("unknown_type")
        assert version == "v1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])