"""Add real-time columns to existing tables

Revision ID: 002_add_realtime_columns
Revises: 001_add_streaming_tables
Create Date: 2026-09-08

This migration adds real-time columns to existing dimension and fact tables
to support streaming analytics integration with the batch system:

- dim_customer: Add last_realtime_event_time, realtime_risk_level, realtime_risk_score, on_watchlist
- fact_transaction: Add event_time, processing_time for real-time event tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_realtime_columns'
down_revision = '001_add_streaming_tables'
branch_labels = None
depends_on = '001_add_streaming_tables'


def upgrade():
    # Add real-time columns to dim_customer
    op.add_column(
        'dim_customer',
        sa.Column('last_realtime_event_time', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'dim_customer',
        sa.Column('realtime_risk_level', sa.String(20), nullable=True)
    )
    op.add_column(
        'dim_customer',
        sa.Column('realtime_risk_score', sa.Numeric(10, 6), nullable=True)
    )
    op.add_column(
        'dim_customer',
        sa.Column('on_watchlist', sa.Boolean, default=False, nullable=False, server_default='false')
    )
    
    # Add indexes for new columns
    op.create_index('ix_customer_realtime_risk_level', 'dim_customer', ['realtime_risk_level'])
    op.create_index('ix_customer_on_watchlist', 'dim_customer', ['on_watchlist'])
    op.create_index('ix_customer_last_realtime_event_time', 'dim_customer', ['last_realtime_event_time'])
    
    # Add check constraint for realtime_risk_level
    op.execute(
        "ALTER TABLE dim_customer "
        "ADD CONSTRAINT ck_customer_realtime_risk_level "
        "CHECK (realtime_risk_level IN ('low', 'medium', 'high', 'critical') OR realtime_risk_level IS NULL)"
    )
    
    # Add check constraint for realtime_risk_score
    op.execute(
        "ALTER TABLE dim_customer "
        "ADD CONSTRAINT ck_customer_realtime_risk_score "
        "CHECK (realtime_risk_score BETWEEN 0 AND 1 OR realtime_risk_score IS NULL)"
    )
    
    # Add real-time columns to fact_transaction
    op.add_column(
        'fact_transaction',
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'fact_transaction',
        sa.Column('processing_time', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add indexes for new columns
    op.create_index('ix_transaction_event_time', 'fact_transaction', ['event_time'])
    op.create_index('ix_transaction_processing_time', 'fact_transaction', ['processing_time'])
    
    # Add comment to new columns
    op.execute("COMMENT ON COLUMN dim_customer.last_realtime_event_time IS 'Timestamp of the last real-time event processed for this customer'")
    op.execute("COMMENT ON COLUMN dim_customer.realtime_risk_level IS 'Real-time risk level from streaming pipeline (low, medium, high, critical)'")
    op.execute("COMMENT ON COLUMN dim_customer.realtime_risk_score IS 'Real-time risk score from streaming pipeline (0-1)'")
    op.execute("COMMENT ON COLUMN dim_customer.on_watchlist IS 'Flag indicating if customer is on real-time watchlist'")
    op.execute("COMMENT ON COLUMN fact_transaction.event_time IS 'Event time from source system (business time)'")
    op.execute("COMMENT ON COLUMN fact_transaction.processing_time IS 'Processing time when event was processed by streaming pipeline'")


def downgrade():
    # Remove columns from fact_transaction (in reverse order)
    op.drop_index('ix_transaction_processing_time', 'fact_transaction')
    op.drop_index('ix_transaction_event_time', 'fact_transaction')
    op.drop_column('fact_transaction', 'processing_time')
    op.drop_column('fact_transaction', 'event_time')
    
    # Remove columns from dim_customer (in reverse order)
    op.drop_constraint('ck_customer_realtime_risk_score', 'dim_customer')
    op.drop_constraint('ck_customer_realtime_risk_level', 'dim_customer')
    op.drop_index('ix_customer_last_realtime_event_time', 'dim_customer')
    op.drop_index('ix_customer_on_watchlist', 'dim_customer')
    op.drop_index('ix_customer_realtime_risk_level', 'dim_customer')
    op.drop_column('dim_customer', 'on_watchlist')
    op.drop_column('dim_customer', 'realtime_risk_score')
    op.drop_column('dim_customer', 'realtime_risk_level')
    op.drop_column('dim_customer', 'last_realtime_event_time')
