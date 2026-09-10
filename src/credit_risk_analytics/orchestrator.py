"""Orchestrator for credit risk analytics."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.credit_risk_analytics.base import (
    CreditRiskBase,
    RiskIndicator,
    RiskBand,
)
from src.credit_risk_analytics.exposure import ExposureAnalyzer
from src.credit_risk_analytics.payment_behavior import PaymentBehaviorAnalyzer
from src.credit_risk_analytics.utilization import UtilizationAnalyzer
from src.credit_risk_analytics.repayment import RepaymentHistoryAnalyzer
from src.credit_risk_analytics.debt_burden import DebtBurdenAnalyzer
from src.credit_risk_analytics.default import DefaultAnalyzer
from src.credit_risk_analytics.scoring import CustomerRiskScoreCalculator
from src.credit_risk_analytics.bands import RiskBandClassifier

logger = logging.getLogger(__name__)


class CreditRiskOrchestrator(CreditRiskBase):
    """Orchestrates credit risk analytics operations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize credit risk orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        
        Note:
            This is a portfolio analytics tool, not a real-world banking credit decision model.
        """
        super().__init__(as_of_date)
        
        # Initialize components
        self.exposure_analyzer = ExposureAnalyzer(as_of_date)
        self.payment_analyzer = PaymentBehaviorAnalyzer(as_of_date)
        self.utilization_analyzer = UtilizationAnalyzer(as_of_date)
        self.repayment_analyzer = RepaymentHistoryAnalyzer(as_of_date)
        self.debt_burden_analyzer = DebtBurdenAnalyzer(as_of_date)
        self.default_analyzer = DefaultAnalyzer(as_of_date)
        self.score_calculator = CustomerRiskScoreCalculator(as_of_date)
        self.band_classifier = RiskBandClassifier(as_of_date)
    
    def generate_comprehensive_risk_report(
        self,
        loan_df: pd.DataFrame,
        payment_df: pd.DataFrame,
        account_df: Optional[pd.DataFrame] = None,
        customer_df: Optional[pd.DataFrame] = None,
        customer_key: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive credit risk analytics report.
        
        Args:
            loan_df: DataFrame with loan data
            payment_df: DataFrame with payment data
            account_df: Optional DataFrame with account data
            customer_df: Optional DataFrame with customer data
            customer_key: Optional customer key for customer-specific report
        
        Returns:
            Dictionary with comprehensive risk analytics results
        
        Note:
            This is for portfolio analytics only, not for credit decision making.
        """
        logger.info("Generating comprehensive credit risk report")
        
        report = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "disclaimer": "This risk analysis is for portfolio analytics only, not for real-world banking credit decisions."
            },
            "exposure": {},
            "payment_behavior": {},
            "utilization": {},
            "repayment_history": {},
            "debt_burden": {},
            "default_indicators": {},
            "risk_score": {},
            "risk_band": {}
        }
        
        # Exposure analysis
        report["exposure"]["total_exposure"] = self.exposure_analyzer.calculate_total_exposure(loan_df)
        report["exposure"]["outstanding_balance"] = self.exposure_analyzer.calculate_outstanding_balance(loan_df)
        report["exposure"]["average_balance"] = self.exposure_analyzer.calculate_average_balance(loan_df)
        
        # Payment behavior analysis
        report["payment_behavior"]["days_past_due"] = self.payment_analyzer.calculate_days_past_due(loan_df)
        report["payment_behavior"]["delinquency_status"] = self.payment_analyzer.calculate_delinquency_status(loan_df)
        
        # Utilization analysis (if account data available)
        if account_df is not None:
            report["utilization"]["credit_utilization"] = self.utilization_analyzer.calculate_credit_utilization(account_df)
        
        # Repayment history analysis
        report["repayment_history"]["on_time_payment_rate"] = self.repayment_analyzer.calculate_on_time_payment_rate(payment_df)
        report["repayment_history"]["late_payment_count"] = self.repayment_analyzer.calculate_late_payment_count(payment_df)
        report["repayment_history"]["missed_payment_count"] = self.repayment_analyzer.calculate_missed_payment_count(payment_df)
        
        # Debt burden analysis (if customer data available)
        if customer_df is not None:
            report["debt_burden"]["loan_to_income"] = self.debt_burden_analyzer.calculate_loan_to_income(customer_df)
            report["debt_burden"]["debt_to_income"] = self.debt_burden_analyzer.calculate_debt_to_income(customer_df)
            report["debt_burden"]["debt_burden"] = self.debt_burden_analyzer.calculate_debt_burden(customer_df)
        
        # Default indicators
        report["default_indicators"]["default_flag"] = self.default_analyzer.calculate_default_flag(loan_df)
        report["default_indicators"]["default_count"] = self.default_analyzer.calculate_default_count(loan_df)
        
        # Calculate risk score
        indicator_values = {
            RiskIndicator.DAYS_PAST_DUE: report["payment_behavior"]["days_past_due"],
            RiskIndicator.DELINQUENCY_STATUS: report["payment_behavior"]["delinquency_status"],
            RiskIndicator.ON_TIME_PAYMENT_RATE: report["repayment_history"]["on_time_payment_rate"],
        }
        
        if account_df is not None:
            indicator_values[RiskIndicator.CREDIT_UTILIZATION] = report["utilization"]["credit_utilization"]
        
        if customer_df is not None:
            indicator_values[RiskIndicator.DEBT_TO_INCOME] = report["debt_burden"]["debt_to_income"]
        
        indicator_values[RiskIndicator.DEFAULT_FLAG] = report["default_indicators"]["default_flag"]
        
        report["risk_score"] = self.score_calculator.calculate_risk_score(indicator_values)
        
        # Classify risk band
        risk_score = report["risk_score"]["risk_score"]
        risk_band = self.band_classifier.classify(risk_score)
        report["risk_band"]["classification"] = risk_band.value
        report["risk_band"]["definition"] = self.band_classifier.get_band_definition(risk_band).to_dict()
        
        return report
    
    def generate_customer_risk_report(
        self,
        loan_df: pd.DataFrame,
        payment_df: pd.DataFrame,
        customer_key: int,
        account_df: Optional[pd.DataFrame] = None,
        customer_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Generate customer-specific credit risk report.
        
        Args:
            loan_df: DataFrame with loan data
            payment_df: DataFrame with payment data
            customer_key: Customer key to analyze
            account_df: Optional DataFrame with account data
            customer_df: Optional DataFrame with customer data
        
        Returns:
            Dictionary with customer-specific risk analytics
        
        Note:
            This is for portfolio analytics only, not for credit decision making.
        """
        logger.info(f"Generating risk report for customer {customer_key}")
        
        # Filter to customer
        customer_loan_df = loan_df[loan_df["customer_key"] == customer_key].copy()
        customer_payment_df = payment_df[payment_df["customer_key"] == customer_key].copy()
        
        if len(customer_loan_df) == 0 and len(customer_payment_df) == 0:
            return {"error": f"No data found for customer {customer_key}"}
        
        return self.generate_comprehensive_risk_report(
            customer_loan_df,
            customer_payment_df,
            account_df,
            customer_df,
            customer_key
        )
    
    def update_score_weights(self, weights) -> None:
        """Update risk score weights.
        
        Args:
            weights: New list of weight configurations
        """
        self.score_calculator.update_weights(weights)
        logger.info("Updated risk score weights")
    
    def update_band_thresholds(self, thresholds) -> None:
        """Update risk band thresholds.
        
        Args:
            thresholds: New list of threshold configurations
        """
        self.band_classifier.update_thresholds(thresholds)
        logger.info("Updated risk band thresholds")
    
    def get_indicator_registry(self) -> Dict[str, Any]:
        """Get all registered indicator definitions.
        
        Returns:
            Dictionary of indicator definitions
        """
        return self.get_all_indicator_definitions()
