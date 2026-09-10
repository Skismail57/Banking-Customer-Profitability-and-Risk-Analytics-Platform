"""End-to-End Pipeline Orchestrator.

This orchestrator follows the analytical layer architecture:
Banking Data → Data Platform → Customer 360/Transaction/Product Analytics → 
Core Analytics → Statistical Analytics → ML → Decision Engine → Power BI/Streamlit/API
"""

from typing import Dict, Any, Optional, List
from datetime import date
import logging
from enum import Enum

from src.data_platform.data_loader import DataLoader
from src.data_platform.customer_360 import Customer360Platform
from src.data_platform.transaction_analytics import TransactionAnalyticsPlatform
from src.data_platform.product_analytics import ProductAnalyticsPlatform
from src.core_analytics.core_analytics_orchestrator import CoreAnalyticsOrchestrator
from src.statistical_analytics.integrated import IntegratedStatisticalAnalytics
from src.ml.integrated import IntegratedMLLayer
from src.decision_intelligence.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline stages."""
    DATA_PLATFORM = "data_platform"
    CORE_ANALYTICS = "core_analytics"
    STATISTICAL_ANALYTICS = "statistical_analytics"
    ML_PREDICTIONS = "ml_predictions"
    DECISION_ENGINE = "decision_engine"


class PipelineOrchestrator:
    """End-to-End Pipeline Orchestrator.
    
    This class orchestrates the entire analytical pipeline following the
    architecture: Banking Data → Data Platform → Core Analytics → 
    Statistical Analytics → ML → Decision Engine → Power BI/Streamlit/API
    """
    
    def __init__(
        self,
        as_of_date: Optional[date] = None,
        data_loader: Optional[DataLoader] = None
    ):
        """Initialize Pipeline Orchestrator.
        
        Args:
            as_of_date: As-of date for the pipeline run
            data_loader: Data loader instance
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
        
        # Initialize all pipeline components
        self.customer_360 = Customer360Platform(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.transaction_analytics = TransactionAnalyticsPlatform(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.product_analytics = ProductAnalyticsPlatform(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.core_analytics = CoreAnalyticsOrchestrator(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.statistical_analytics = IntegratedStatisticalAnalytics(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.ml_layer = IntegratedMLLayer(as_of_date=self.as_of_date, data_loader=self.data_loader)
        self.decision_engine = DecisionEngine(as_of_date=self.as_of_date, data_loader=self.data_loader, ml_layer=self.ml_layer)
        
        # Pipeline execution status
        self.execution_log: List[Dict[str, Any]] = []
    
    def run_full_pipeline(
        self,
        customer_keys: Optional[List[str]] = None,
        stages: Optional[List[PipelineStage]] = None
    ) -> Dict[str, Any]:
        """Run the full analytical pipeline.
        
        Args:
            customer_keys: Optional list of customer keys to process
            stages: Optional list of stages to run (runs all if None)
        
        Returns:
            Dictionary with pipeline execution results
        """
        logger.info(f"Starting full pipeline run for as_of_date: {self.as_of_date}")
        
        if stages is None:
            stages = list(PipelineStage)
        
        results = {}
        
        # Stage 1: Data Platform (Customer 360, Transaction, Product Analytics)
        if PipelineStage.DATA_PLATFORM in stages:
            logger.info("Running Data Platform stage")
            results['data_platform'] = self._run_data_platform_stage(customer_keys)
        
        # Stage 2: Core Analytics (Profitability, Risk, Behavior)
        if PipelineStage.CORE_ANALYTICS in stages:
            logger.info("Running Core Analytics stage")
            results['core_analytics'] = self._run_core_analytics_stage(customer_keys)
        
        # Stage 3: Statistical Analytics
        if PipelineStage.STATISTICAL_ANALYTICS in stages:
            logger.info("Running Statistical Analytics stage")
            results['statistical_analytics'] = self._run_statistical_analytics_stage()
        
        # Stage 4: ML Predictions (Churn, CLV, Risk)
        if PipelineStage.ML_PREDICTIONS in stages:
            logger.info("Running ML Predictions stage")
            results['ml_predictions'] = self._run_ml_predictions_stage(customer_keys)
        
        # Stage 5: Decision Engine
        if PipelineStage.DECISION_ENGINE in stages:
            logger.info("Running Decision Engine stage")
            results['decision_engine'] = self._run_decision_engine_stage(customer_keys)
        
        logger.info("Full pipeline run completed")
        
        return {
            'as_of_date': self.as_of_date,
            'stages_run': [stage.value for stage in stages],
            'results': results,
            'execution_log': self.execution_log
        }
    
    def _run_data_platform_stage(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run Data Platform stage.
        
        Args:
            customer_keys: Optional list of customer keys
        
        Returns:
            Dictionary with stage results
        """
        stage_result = {
            'status': 'success',
            'customer_360_processed': 0,
            'transaction_analytics_processed': 0,
            'product_analytics_processed': 0
        }
        
        try:
            # Customer 360
            if customer_keys:
                customer_360_df = self.customer_360.get_customer_360_batch(
                    customer_keys=customer_keys,
                    include_transactions=False
                )
                stage_result['customer_360_processed'] = len(customer_360_df)
            else:
                # Process all customers would be too expensive, so just count
                customers_df = self.data_loader.load_customers()
                stage_result['customer_360_processed'] = len(customers_df)
            
            # Transaction Analytics
            transactions_df = self.data_loader.load_transactions()
            stage_result['transaction_analytics_processed'] = len(transactions_df)
            
            # Product Analytics
            products_df = self.data_loader.load_products()
            stage_result['product_analytics_processed'] = len(products_df)
            
            self.execution_log.append({
                'stage': 'data_platform',
                'status': 'success',
                'timestamp': self.as_of_date
            })
            
        except Exception as e:
            logger.error(f"Error in Data Platform stage: {e}")
            stage_result['status'] = 'error'
            stage_result['error'] = str(e)
            self.execution_log.append({
                'stage': 'data_platform',
                'status': 'error',
                'error': str(e),
                'timestamp': self.as_of_date
            })
        
        return stage_result
    
    def _run_core_analytics_stage(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run Core Analytics stage.
        
        Args:
            customer_keys: Optional list of customer keys
        
        Returns:
            Dictionary with stage results
        """
        stage_result = {
            'status': 'success',
            'metrics_calculated': 0
        }
        
        try:
            # Calculate core metrics
            metrics_df = self.core_analytics.calculate_core_metrics(customer_keys=customer_keys)
            stage_result['metrics_calculated'] = len(metrics_df)
            
            # Persist metrics to fact_customer_metrics
            self.core_analytics.persist_core_metrics(metrics_df)
            
            self.execution_log.append({
                'stage': 'core_analytics',
                'status': 'success',
                'timestamp': self.as_of_date
            })
            
        except Exception as e:
            logger.error(f"Error in Core Analytics stage: {e}")
            stage_result['status'] = 'error'
            stage_result['error'] = str(e)
            self.execution_log.append({
                'stage': 'core_analytics',
                'status': 'error',
                'error': str(e),
                'timestamp': self.as_of_date
            })
        
        return stage_result
    
    def _run_statistical_analytics_stage(self) -> Dict[str, Any]:
        """Run Statistical Analytics stage.
        
        Returns:
            Dictionary with stage results
        """
        stage_result = {
            'status': 'success',
            'tests_performed': 0
        }
        
        try:
            # Perform statistical tests
            profitability_test = self.statistical_analytics.analyze_profitability_by_segment()
            correlation_test = self.statistical_analytics.analyze_risk_profitability_correlation()
            churn_drivers = self.statistical_analytics.analyze_churn_drivers()
            clv_distribution = self.statistical_analytics.analyze_clv_distribution()
            
            stage_result['tests_performed'] = 3 + len(churn_drivers)
            stage_result['profitability_test'] = profitability_test.to_dict()
            stage_result['correlation_test'] = correlation_test.to_dict()
            stage_result['churn_drivers'] = {k: v.to_dict() for k, v in churn_drivers.items()}
            stage_result['clv_distribution'] = clv_distribution
            
            self.execution_log.append({
                'stage': 'statistical_analytics',
                'status': 'success',
                'timestamp': self.as_of_date
            })
            
        except Exception as e:
            logger.error(f"Error in Statistical Analytics stage: {e}")
            stage_result['status'] = 'error'
            stage_result['error'] = str(e)
            self.execution_log.append({
                'stage': 'statistical_analytics',
                'status': 'error',
                'error': str(e),
                'timestamp': self.as_of_date
            })
        
        return stage_result
    
    def _run_ml_predictions_stage(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run ML Predictions stage.
        
        Args:
            customer_keys: Optional list of customer keys
        
        Returns:
            Dictionary with stage results
        """
        stage_result = {
            'status': 'success',
            'predictions_generated': 0
        }
        
        try:
            # Generate ML features
            features_df = self.ml_layer.generate_ml_features(customer_keys=customer_keys)
            
            if not features_df.empty:
                # Make predictions
                churn_predictions = self.ml_layer.predict_churn(features_df)
                clv_predictions = self.ml_layer.predict_clv(features_df)
                risk_predictions = self.ml_layer.predict_risk(features_df)
                
                stage_result['predictions_generated'] = len(churn_predictions)
                stage_result['churn_predictions'] = len(churn_predictions)
                stage_result['clv_predictions'] = len(clv_predictions)
                stage_result['risk_predictions'] = len(risk_predictions)
            else:
                stage_result['predictions_generated'] = 0
                stage_result['message'] = 'No features available for prediction'
            
            self.execution_log.append({
                'stage': 'ml_predictions',
                'status': 'success',
                'timestamp': self.as_of_date
            })
            
        except Exception as e:
            logger.error(f"Error in ML Predictions stage: {e}")
            stage_result['status'] = 'error'
            stage_result['error'] = str(e)
            self.execution_log.append({
                'stage': 'ml_predictions',
                'status': 'error',
                'error': str(e),
                'timestamp': self.as_of_date
            })
        
        return stage_result
    
    def _run_decision_engine_stage(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run Decision Engine stage.
        
        Args:
            customer_keys: Optional list of customer keys
        
        Returns:
            Dictionary with stage results
        """
        stage_result = {
            'status': 'success',
            'recommendations_generated': 0
        }
        
        try:
            # Generate recommendations
            recommendations_df = self.decision_engine.generate_customer_recommendations(
                customer_keys=customer_keys
            )
            
            stage_result['recommendations_generated'] = len(recommendations_df)
            
            # Generate segment recommendations
            segment_recommendations = self.decision_engine.generate_segment_recommendations()
            stage_result['segment_recommendations'] = len(segment_recommendations)
            
            # Persist recommendations
            self.decision_engine.persist_recommendations(recommendations_df)
            
            # Get recommendation summary
            summary = self.decision_engine.get_recommendation_summary()
            stage_result['recommendation_summary'] = summary
            
            self.execution_log.append({
                'stage': 'decision_engine',
                'status': 'success',
                'timestamp': self.as_of_date
            })
            
        except Exception as e:
            logger.error(f"Error in Decision Engine stage: {e}")
            stage_result['status'] = 'error'
            stage_result['error'] = str(e)
            self.execution_log.append({
                'stage': 'decision_engine',
                'status': 'error',
                'error': str(e),
                'timestamp': self.as_of_date
            })
        
        return stage_result
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status.
        
        Returns:
            Dictionary with pipeline status
        """
        return {
            'as_of_date': self.as_of_date,
            'execution_log': self.execution_log,
            'last_execution': self.execution_log[-1] if self.execution_log else None
        }
