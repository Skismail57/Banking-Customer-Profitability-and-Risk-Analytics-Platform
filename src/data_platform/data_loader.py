"""Data Loader for Data Platform Integration Layer."""

from typing import Dict, Any, Optional, List
from datetime import date
import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class DataLoader:
    """Unified data loader for the data platform.
    
    This class provides methods to load data from the database for all
    analytics modules. It serves as the single source of truth for data access.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize data loader.
        
        Args:
            db_manager: Database manager instance (creates default if not provided)
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def get_session(self) -> Session:
        """Get database session.
        
        Returns:
            SQLAlchemy session
        """
        return self.db_manager.get_session()
    
    # ============================================================================
    # DIMENSION DATA LOADERS
    # ============================================================================
    
    def load_customers(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None,
        segments: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load customer dimension data.
        
        Args:
            as_of_date: As-of date for temporal filtering
            customer_keys: Optional list of customer keys to filter
            segments: Optional list of segments to filter
        
        Returns:
            DataFrame with customer data
        """
        query = """
        SELECT 
            customer_key,
            customer_id,
            customer_name,
            customer_age,
            gender,
            income_level,
            segment,
            region,
            branch,
            customer_since,
            customer_status,
            marital_status,
            education_level,
            occupation,
            household_size
        FROM dim_customer
        WHERE customer_status = 'active'
        """
        
        params = {}
        
        if customer_keys:
            query += " AND customer_key = ANY(:customer_keys)"
            params["customer_keys"] = customer_keys
        
        if segments:
            query += " AND segment = ANY(:segments)"
            params["segments"] = segments
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} customers from dim_customer")
        return df
    
    def load_products(
        self,
        product_keys: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        is_active: Optional[bool] = True
    ) -> pd.DataFrame:
        """Load product dimension data.
        
        Args:
            product_keys: Optional list of product keys to filter
            categories: Optional list of product categories to filter
            is_active: Filter by active status
        
        Returns:
            DataFrame with product data
        """
        query = """
        SELECT 
            product_key,
            product_id,
            product_name,
            product_category,
            product_type,
            base_rate,
            term_months,
            min_amount,
            max_amount,
            is_active,
            launch_date
        FROM dim_product
        WHERE 1=1
        """
        
        params = {}
        
        if product_keys:
            query += " AND product_key = ANY(:product_keys)"
            params["product_keys"] = product_keys
        
        if categories:
            query += " AND product_category = ANY(:categories)"
            params["categories"] = categories
        
        if is_active is not None:
            query += " AND is_active = :is_active"
            params["is_active"] = is_active
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} products from dim_product")
        return df
    
    def load_date_dimension(
        self,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Load date dimension data.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with date dimension data
        """
        query = """
        SELECT 
            date_key,
            date,
            day,
            month,
            quarter,
            year,
            day_of_week,
            day_of_year,
            week_of_year,
            is_weekend,
            is_holiday,
            month_name,
            quarter_name,
            fiscal_year,
            fiscal_quarter
        FROM dim_date
        WHERE date BETWEEN :start_date AND :end_date
        ORDER BY date
        """
        
        with self.get_session() as session:
            result = session.execute(text(query), {
                "start_date": start_date,
                "end_date": end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} dates from dim_date")
        return df
    
    # ============================================================================
    # FACT DATA LOADERS
    # ============================================================================
    
    def load_customer_metrics(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None,
        segments: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load customer metrics fact data (Core Analytics output).
        
        Args:
            as_of_date: As-of date for temporal filtering
            customer_keys: Optional list of customer keys to filter
            segments: Optional list of segments to filter
        
        Returns:
            DataFrame with customer metrics
        """
        query = """
        SELECT 
            customer_key,
            as_of_date,
            net_profit,
            revenue,
            cost,
            profit_margin,
            risk_adjusted_profit,
            risk_level,
            risk_trend,
            exposure_amount,
            credit_utilization,
            days_past_due,
            credit_score,
            balance_to_income_ratio,
            churn_probability,
            churn_risk_level,
            clv,
            clv_trend,
            segment
        FROM fact_customer_metrics
        WHERE 1=1
        """
        
        params = {}
        
        if as_of_date:
            query += " AND as_of_date = :as_of_date"
            params["as_of_date"] = as_of_date
        else:
            query += " AND as_of_date = (SELECT MAX(as_of_date) FROM fact_customer_metrics)"
        
        if customer_keys:
            query += " AND customer_key = ANY(:customer_keys)"
            params["customer_keys"] = customer_keys
        
        if segments:
            query += " AND segment = ANY(:segments)"
            params["segments"] = segments
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} customer metrics from fact_customer_metrics")
        return df
    
    def load_transactions(
        self,
        customer_key: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load transaction fact data.
        
        Args:
            customer_key: Optional customer key to filter
            start_date: Optional start date
            end_date: Optional end date
            transaction_types: Optional list of transaction types to filter
        
        Returns:
            DataFrame with transaction data
        """
        query = """
        SELECT 
            t.transaction_id,
            t.customer_key,
            t.product_key,
            t.channel_key,
            t.transaction_date,
            t.transaction_type,
            t.channel,
            t.amount,
            t.currency,
            t.description,
            t.merchant_category,
            t.location,
            p.product_name,
            p.product_category
        FROM fact_transactions t
        LEFT JOIN dim_product p ON t.product_key = p.product_key
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND t.customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params["end_date"] = end_date
        
        if transaction_types:
            query += " AND t.transaction_type = ANY(:transaction_types)"
            params["transaction_types"] = transaction_types
        
        query += " ORDER BY t.transaction_date DESC"
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} transactions from fact_transactions")
        return df
    
    def load_loans(
        self,
        customer_key: Optional[str] = None,
        as_of_date: Optional[date] = None,
        loan_status: Optional[str] = None
    ) -> pd.DataFrame:
        """Load loan fact data.
        
        Args:
            customer_key: Optional customer key to filter
            as_of_date: As-of date for temporal filtering
            loan_status: Optional loan status to filter
        
        Returns:
            DataFrame with loan data
        """
        query = """
        SELECT 
            l.loan_key,
            l.customer_key,
            l.product_key,
            l.loan_id,
            l.loan_amount,
            l.current_balance,
            l.original_balance,
            l.interest_rate,
            l.term_months,
            l.start_date,
            l.maturity_date,
            l.loan_status,
            l.days_past_due,
            l.payment_amount,
            l.next_payment_date,
            l.as_of_date,
            p.product_name,
            p.product_category
        FROM fact_loan l
        LEFT JOIN dim_product p ON l.product_key = p.product_key
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND l.customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if as_of_date:
            query += " AND l.as_of_date = :as_of_date"
            params["as_of_date"] = as_of_date
        else:
            query += " AND l.as_of_date = (SELECT MAX(as_of_date) FROM fact_loan)"
        
        if loan_status:
            query += " AND l.loan_status = :loan_status"
            params["loan_status"] = loan_status
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} loans from fact_loan")
        return df
    
    def load_accounts(
        self,
        customer_key: Optional[str] = None,
        as_of_date: Optional[date] = None,
        account_type: Optional[str] = None
    ) -> pd.DataFrame:
        """Load account fact data.
        
        Args:
            customer_key: Optional customer key to filter
            as_of_date: As-of date for temporal filtering
            account_type: Optional account type to filter
        
        Returns:
            DataFrame with account data
        """
        query = """
        SELECT 
            a.account_key,
            a.customer_key,
            a.product_key,
            a.account_id,
            a.account_type,
            a.current_balance,
            a.credit_limit,
            a.available_credit,
            a.account_status,
            a.open_date,
            a.as_of_date,
            p.product_name,
            p.product_category
        FROM fact_account a
        LEFT JOIN dim_product p ON a.product_key = p.product_key
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND a.customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if as_of_date:
            query += " AND a.as_of_date = :as_of_date"
            params["as_of_date"] = as_of_date
        else:
            query += " AND a.as_of_date = (SELECT MAX(as_of_date) FROM fact_account)"
        
        if account_type:
            query += " AND a.account_type = :account_type"
            params["account_type"] = account_type
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} accounts from fact_account")
        return df
    
    def load_payments(
        self,
        customer_key: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Load payment fact data.
        
        Args:
            customer_key: Optional customer key to filter
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            DataFrame with payment data
        """
        query = """
        SELECT 
            p.payment_id,
            p.customer_key,
            p.loan_key,
            p.payment_date,
            p.due_date,
            p.payment_amount,
            p.payment_type,
            p.payment_status,
            l.loan_id
        FROM fact_payment p
        LEFT JOIN fact_loan l ON p.loan_key = l.loan_key
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND p.customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if start_date:
            query += " AND p.payment_date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND p.payment_date <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY p.payment_date DESC"
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} payments from fact_payment")
        return df
    
    def load_customer_profitability(
        self,
        customer_key: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Load customer profitability fact data.
        
        Args:
            customer_key: Optional customer key to filter
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            DataFrame with profitability data
        """
        query = """
        SELECT 
            customer_key,
            product_key,
            period,
            period_type,
            interest_income,
            fee_income,
            service_charge_income,
            product_revenue,
            servicing_cost,
            operational_cost,
            incentive_cost,
            expected_credit_loss
        FROM fact_customer_profitability
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if start_date:
            query += " AND period >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND period <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY period DESC"
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} profitability records from fact_customer_profitability")
        return df
    
    def load_recommendations(
        self,
        customer_key: Optional[str] = None,
        segment: Optional[str] = None,
        generated_at: Optional[date] = None,
        priority: Optional[str] = None
    ) -> pd.DataFrame:
        """Load recommendations fact data (Decision Engine output).
        
        Args:
            customer_key: Optional customer key to filter
            segment: Optional segment to filter
            generated_at: Optional generation date to filter
            priority: Optional priority to filter
        
        Returns:
            DataFrame with recommendations
        """
        query = """
        SELECT 
            recommendation_key,
            customer_key,
            segment,
            priority,
            confidence_level,
            recommended_action,
            reason,
            triggering_metrics,
            limitations,
            generated_at,
            implemented_at,
            implementation_status
        FROM fact_recommendations
        WHERE 1=1
        """
        
        params = {}
        
        if customer_key:
            query += " AND customer_key = :customer_key"
            params["customer_key"] = customer_key
        
        if segment:
            query += " AND segment = :segment"
            params["segment"] = segment
        
        if generated_at:
            query += " AND generated_at = :generated_at"
            params["generated_at"] = generated_at
        
        if priority:
            query += " AND priority = :priority"
            params["priority"] = priority
        
        query += " ORDER BY generated_at DESC, priority DESC"
        
        with self.get_session() as session:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        logger.info(f"Loaded {len(df)} recommendations from fact_recommendations")
        return df
