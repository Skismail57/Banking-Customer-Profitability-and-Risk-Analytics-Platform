"""Mock Data Loader for development without database."""

from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MockDataLoader:
    """Mock data loader for development without database connection."""
    
    def __init__(self):
        """Initialize mock data loader."""
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)

        # Indian customer names (Hindu, Muslim, Christian)
        hindu_names = [
            "Aarav Sharma", "Aditi Gupta", "Arjun Singh", "Ananya Patel", "Aryan Verma",
            "Anika Singh", "Arnav Gupta", "Aanya Sharma", "Advik Patel", "Aadhya Verma",
            "Vikram Singh", "Priya Sharma", "Rahul Gupta", "Neha Patel", "Amit Verma",
            "Sneha Singh", "Rajesh Gupta", "Pooja Sharma", "Amit Patel", "Sunita Verma",
            "Rohan Sharma", "Kavita Gupta", "Rahul Singh", "Anjali Patel", "Vikram Verma",
            "Deepak Sharma", "Meera Gupta", "Ravi Singh", "Lata Patel", "Sunil Verma"
        ]

        muslim_names = [
            "Mohammed Khan", "Fatima Sheikh", "Ahmed Ali", "Ayesha Khan", "Omar Farooq",
            "Zara Ahmed", "Imran Khan", "Mariam Sheikh", "Yusuf Ali", "Sana Farooq",
            "Abdul Rahman", "Khadija Khan", "Hassan Sheikh", "Zainab Ali", "Ibrahim Farooq",
            "Noor Ahmed", "Bilal Khan", "Amina Sheikh", "Khalid Ali", "Sarah Farooq",
            "Tariq Khan", "Hafiza Sheikh", "Zafar Ali", "Ruqayya Farooq", "Nasir Khan",
            "Saadia Ahmed", "Rashid Sheikh", "Zahra Ali", "Jamal Farooq", "Amira Khan"
        ]

        christian_names = [
            "John D'Souza", "Mary Thomas", "Anthony Gomes", "Grace Fernandes", "Peter D'Silva",
            "Rachel Rodrigues", "Michael Mendonca", "Elizabeth Sequeira", "David Pinto", "Sarah Braganza",
            "Joseph D'Souza", "Anna Thomas", "Paul Gomes", "Margaret Fernandes", "James D'Silva",
            "Catherine Rodrigues", "William Mendonca", "Victoria Sequeira", "Robert Pinto", "Emily Braganza",
            "Thomas D'Souza", "Helen Thomas", "Richard Gomes", "Dorothy Fernandes", "Charles D'Silva",
            "Martha Rodrigues", "George Mendonca", "Ruth Sequeira", "Henry Pinto", "Mildred Braganza"
        ]

        # Combine and shuffle names
        all_names = hindu_names + muslim_names + christian_names
        # Generate more names by repeating and shuffling
        indian_names = (all_names * 34)  # Multiply to get enough names
        np.random.shuffle(indian_names)

        # Generate sample customers
        n_customers = 1000
        self.customers = pd.DataFrame({
            'customer_key': [f'CUST_{i:06d}' for i in range(n_customers)],
            'customer_name': indian_names[:n_customers],
            'segment': np.random.choice(['Retail', 'Commercial', 'Wealth', 'SME'], n_customers),
            'region': np.random.choice(['North', 'South', 'East', 'West'], n_customers),
            'tenure_months': np.random.randint(1, 120, n_customers),
            'age': np.random.randint(18, 80, n_customers),
            'gender': np.random.choice(['M', 'F'], n_customers),
            'account_balance': np.random.uniform(10000, 1000000, n_customers),  # INR: 10K to 10L
            'currency': 'INR',
            'credit_score': np.random.randint(300, 850, n_customers),
            'created_at': [datetime.now() - timedelta(days=np.random.randint(1, 3650)) for _ in range(n_customers)]
        })
        
        # Generate sample transactions
        n_transactions = 10000
        self.transactions = pd.DataFrame({
            'transaction_key': [f'TXN_{i:08d}' for i in range(n_transactions)],
            'customer_key': np.random.choice(self.customers['customer_key'], n_transactions),
            'amount': np.random.uniform(100, 500000, n_transactions),  # INR: 100 to 5L
            'currency': 'INR',
            'transaction_type': np.random.choice(['Debit', 'Credit', 'Transfer'], n_transactions),
            'product_type': np.random.choice(['Checking', 'Savings', 'Credit Card', 'Loan'], n_transactions),
            'transaction_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_transactions)]
        })
        
        # Generate sample customer metrics (ensure no zero values)
        self.customer_metrics = pd.DataFrame({
            'customer_key': self.customers['customer_key'],
            'total_revenue': np.random.uniform(10000, 500000, n_customers),  # INR: 10K to 5L
            'total_cost': np.random.uniform(5000, 250000, n_customers),  # INR: 5K to 2.5L
            'net_profit': np.random.uniform(10000, 250000, n_customers),  # INR: 10K to 2.5L (positive)
            'risk_score': np.random.uniform(0.1, 0.9, n_customers),  # Avoid 0 and 1
            'churn_probability': np.random.uniform(0.1, 0.8, n_customers),  # Avoid 0 and 1
            'customer_lifetime_value': np.random.uniform(100000, 5000000, n_customers),  # INR: 1L to 50L
            'as_of_date': datetime.now()
        })
        
        # Generate sample risk data with better distribution
        self.risk_data = pd.DataFrame({
            'customer_key': self.customers['customer_key'],
            'risk_level': np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_customers, p=[0.4, 0.3, 0.2, 0.1]),  # Weighted distribution
            'risk_score': np.random.uniform(0.1, 0.95, n_customers),  # Avoid 0 and 1
            'exposure_amount': np.random.uniform(100000, 10000000, n_customers),  # INR: 1L to 1Cr (no zeros)
            'delinquency_days': np.random.randint(0, 180, n_customers),
            'credit_utilization': np.random.uniform(0.1, 0.95, n_customers),  # Avoid 0 and 1
            'as_of_date': datetime.now()
        })
        
        # Generate sample product data (ensure no zeros)
        self.product_data = pd.DataFrame({
            'product_type': ['Checking', 'Savings', 'Credit Card', 'Loan', 'Mortgage'],
            'total_customers': [500, 400, 300, 200, 100],
            'total_revenue': [10000000, 8000000, 12000000, 15000000, 20000000],  # INR: in lakhs
            'avg_balance': [50000, 100000, 30000, 250000, 2000000],  # INR: realistic balances
            'npl_rate': [0.01, 0.005, 0.02, 0.03, 0.01],
            'active_accounts': [450, 380, 280, 180, 90]  # Ensure no zeros
        })
    
    def load_customers(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None,
        segments: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load customer dimension data."""
        df = self.customers.copy()

        # Reorder columns: customer_key, customer_name first
        cols = ['customer_key', 'customer_name'] + [col for col in df.columns if col not in ['customer_key', 'customer_name']]
        df = df[cols]

        if customer_keys:
            df = df[df['customer_key'].isin(customer_keys)]

        if segments:
            df = df[df['segment'].isin(segments)]

        return df
    
    def load_customer_metrics(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load customer metrics."""
        df = self.customer_metrics.copy()

        # Check if customer_name, segment, region already exist
        if 'customer_name' not in df.columns or 'segment' not in df.columns or 'region' not in df.columns:
            # Join with customers to get customer_name, segment, region
            df = df.merge(
                self.customers[['customer_key', 'customer_name', 'segment', 'region']],
                on='customer_key',
                how='left'
            )

        # Reorder columns: customer_key, customer_name, segment, region first
        priority_cols = ['customer_key', 'customer_name', 'segment', 'region']
        existing_priority = [col for col in priority_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in existing_priority]
        df = df[existing_priority + other_cols]

        if customer_keys:
            df = df[df['customer_key'].isin(customer_keys)]

        return df
    
    def load_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Load transaction data."""
        df = self.transactions.copy()

        # Join with customers to get customer_name
        df = df.merge(self.customers[['customer_key', 'customer_name']], on='customer_key', how='left')

        # Reorder columns: customer_key, customer_name first
        cols = ['customer_key', 'customer_name'] + [col for col in df.columns if col not in ['customer_key', 'customer_name']]
        df = df[cols]

        if start_date:
            df = df[df['transaction_date'] >= pd.Timestamp(start_date)]

        if end_date:
            df = df[df['transaction_date'] <= pd.Timestamp(end_date)]

        if customer_keys:
            df = df[df['customer_key'].isin(customer_keys)]

        if limit:
            df = df.head(limit)

        return df
    
    def load_risk_data(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load risk data."""
        df = self.risk_data.copy()

        # Join with customers to get customer_name
        df = df.merge(self.customers[['customer_key', 'customer_name']], on='customer_key', how='left')

        # Reorder columns: customer_key, customer_name first
        cols = ['customer_key', 'customer_name'] + [col for col in df.columns if col not in ['customer_key', 'customer_name']]
        df = df[cols]

        if customer_keys:
            df = df[df['customer_key'].isin(customer_keys)]

        return df
    
    def load_product_data(self) -> pd.DataFrame:
        """Load product analytics data."""
        df = self.product_data.copy()
        # Ensure total_revenue column exists (it should from initialization)
        if 'total_revenue' not in df.columns:
            df['total_revenue'] = df['total_revenue'] if 'total_revenue' in df.columns else 0
        return df
    
    def load_segmentation_data(self) -> pd.DataFrame:
        """Load customer segmentation data."""
        # First, add total_revenue to customers if not present
        if 'total_revenue' not in self.customers.columns:
            self.customers['total_revenue'] = np.random.uniform(10000, 500000, len(self.customers))  # INR: 10K to 5L

        # Also create a detailed view with customer names
        detailed_data = self.customers[['customer_key', 'customer_name', 'segment', 'account_balance', 'total_revenue']].copy()

        # Reorder columns: customer_key, customer_name first
        cols = ['customer_key', 'customer_name'] + [col for col in detailed_data.columns if col not in ['customer_key', 'customer_name']]
        detailed_data = detailed_data[cols]

        return detailed_data
    
    def load_churn_predictions(
        self,
        as_of_date: Optional[date] = None,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Load churn prediction data."""
        df = self.customer_metrics[['customer_key', 'churn_probability']].copy()

        # Join with customers to get customer_name
        df = df.merge(self.customers[['customer_key', 'customer_name']], on='customer_key', how='left')

        # Reorder columns: customer_key, customer_name first
        cols = ['customer_key', 'customer_name'] + [col for col in df.columns if col not in ['customer_key', 'customer_name']]
        df = df[cols]

        if customer_keys:
            df = df[df['customer_key'].isin(customer_keys)]

        df['churn_risk'] = pd.cut(df['churn_probability'],
                                   bins=[0, 0.3, 0.6, 1.0],
                                   labels=['Low', 'Medium', 'High'])

        return df
    
    def get_executive_metrics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get executive summary metrics."""
        return {
            'total_customers': len(self.customers),
            'total_revenue': self.customer_metrics['total_revenue'].sum(),
            'total_profit': self.customer_metrics['net_profit'].sum(),
            'avg_risk_score': self.customer_metrics['risk_score'].mean(),
            'high_risk_customers': len(self.risk_data[self.risk_data['risk_level'].isin(['High', 'Critical'])]),
            'churn_rate': self.customer_metrics['churn_probability'].mean(),
            'total_transactions': len(self.transactions),
            'active_products': len(self.product_data)
        }
    
    def get_customer_360(self, customer_key: str) -> Dict[str, Any]:
        """Get comprehensive customer 360 view."""
        customer = self.customers[self.customers['customer_key'] == customer_key].iloc[0] if len(self.customers[self.customers['customer_key'] == customer_key]) > 0 else None
        metrics = self.customer_metrics[self.customer_metrics['customer_key'] == customer_key].iloc[0] if len(self.customer_metrics[self.customer_metrics['customer_key'] == customer_key]) > 0 else None
        risk = self.risk_data[self.risk_data['customer_key'] == customer_key].iloc[0] if len(self.risk_data[self.risk_data['customer_key'] == customer_key]) > 0 else None
        transactions = self.transactions[self.transactions['customer_key'] == customer_key]
        
        if customer is None:
            return None
        
        return {
            'customer': customer.to_dict(),
            'metrics': metrics.to_dict() if metrics is not None else {},
            'risk': risk.to_dict() if risk is not None else {},
            'recent_transactions': transactions.tail(10).to_dict('records') if len(transactions) > 0 else []
        }