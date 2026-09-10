"""Integration of data quality validation with ETL pipeline."""

from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.data_quality.schemas import (
    DimCustomerSchema,
    DimAccountSchema,
    DimProductSchema,
    DimBranchSchema,
    DimDateSchema,
    DimCustomerSegmentSchema,
    FactTransactionSchema,
    FactLoanSchema,
    FactLoanPaymentSchema,
    FactCardTransactionSchema,
    FactCustomerInteractionSchema,
    FactCustomerProfitabilitySchema,
    FactCustomerRiskSchema,
)
from src.data_quality.metrics import QualityCalculator
from src.data_quality.report import QualityReportGenerator
from src.data_quality.handlers import FailedRecordHandler, DataQualityThreshold

logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Integrates data quality validation into ETL pipeline."""
    
    # Schema mapping
    SCHEMA_MAP = {
        "dim_customer": DimCustomerSchema,
        "dim_account": DimAccountSchema,
        "dim_product": DimProductSchema,
        "dim_branch": DimBranchSchema,
        "dim_date": DimDateSchema,
        "dim_customer_segment": DimCustomerSegmentSchema,
        "fact_transaction": FactTransactionSchema,
        "fact_loan": FactLoanSchema,
        "fact_loan_payment": FactLoanPaymentSchema,
        "fact_card_transaction": FactCardTransactionSchema,
        "fact_customer_interaction": FactCustomerInteractionSchema,
        "fact_customer_profitability": FactCustomerProfitabilitySchema,
        "fact_customer_risk": FactCustomerRiskSchema,
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data quality validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        self.quality_calculator = QualityCalculator()
        self.report_generator = QualityReportGenerator(
            output_dir=self.config.get("report_dir", "data/metadata/reports")
        )
        self.failed_record_handler = FailedRecordHandler(
            quarantine_dir=self.config.get("quarantine_dir", "data/quarantine")
        )
        self.threshold = DataQualityThreshold(
            config=self.config.get("thresholds")
        )
    
    def validate_and_clean(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Validate DataFrame and handle quality issues.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table/schema to validate against
        
        Returns:
            Dictionary with validation results and cleaned data
        """
        logger.info(f"Validating data for table: {table_name}")
        
        # Get schema for table
        schema_class = self.SCHEMA_MAP.get(table_name)
        
        if schema_class is None:
            logger.warning(f"No schema found for table: {table_name}, skipping validation")
            return {
                "status": "skipped",
                "message": f"No schema defined for {table_name}",
                "data": df
            }
        
        # Validate against schema
        validation_result = schema_class.validate_with_report(df, table_name)
        
        # Calculate quality metrics
        metrics = self.quality_calculator.calculate(df, validation_result, table_name)
        
        # Determine action based on thresholds
        action = self.threshold.get_action(metrics, validation_result)
        
        result = {
            "table_name": table_name,
            "validation_result": validation_result.to_dict(),
            "metrics": metrics.to_dict(),
            "action": action,
            "original_row_count": len(df)
        }
        
        # Handle based on action
        if action == "reject":
            logger.error(f"Data quality below critical threshold for {table_name}. Rejecting data.")
            result["data"] = pd.DataFrame()  # Return empty DataFrame
            result["message"] = "Data rejected due to poor quality"
        
        elif action == "quarantine":
            logger.warning(f"Quarantining failed records from {table_name}")
            valid_df, quarantine_path = self.failed_record_handler.quarantine_failed_records(
                df, validation_result, table_name
            )
            result["data"] = valid_df
            result["quarantine_path"] = quarantine_path
            result["message"] = f"Failed records quarantined to {quarantine_path}"
        
        elif action == "warn":
            logger.warning(f"Data quality warning for {table_name}. Accepting with warnings.")
            result["data"] = df  # Accept all data
            result["message"] = "Data accepted with quality warnings"
        
        else:  # accept
            logger.info(f"Data quality acceptable for {table_name}.")
            result["data"] = df
            result["message"] = "Data accepted"
        
        result["final_row_count"] = len(result["data"])
        
        # Generate and save report
        column_metrics = self.quality_calculator.calculate_column_metrics(df)
        report = self.report_generator.generate_report(
            metrics,
            column_metrics=column_metrics,
            validation_errors=validation_result.errors
        )
        report_path = self.report_generator.save_report(report)
        result["report_path"] = report_path
        
        return result
    
    def validate_batch(self, data_map: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Validate multiple DataFrames.
        
        Args:
            data_map: Dictionary mapping table names to DataFrames
        
        Returns:
            Dictionary with overall results
        """
        results = {}
        
        for table_name, df in data_map.items():
            results[table_name] = self.validate_and_clean(df, table_name)
        
        # Generate summary report
        reports = []
        for table_result in results.values():
            if "report_path" in table_result:
                # Load the saved report
                import json
                with open(table_result["report_path"], "r") as f:
                    reports.append(json.load(f))
        
        if reports:
            summary_report = self.report_generator.generate_summary_report(reports)
            summary_path = self.report_generator.save_report(
                summary_report,
                filename="dq_summary_report.json"
            )
            
            results["summary"] = {
                "summary_report_path": summary_path,
                "overall_dq_score": summary_report["overall_statistics"]["average_dq_score"],
                "total_tables": summary_report["summary_metadata"]["total_tables"]
            }
        
        return results


class PipelineQualityHook:
    """Hook for integrating quality validation into ETL pipeline stages."""
    
    def __init__(self, validator: DataQualityValidator):
        """Initialize pipeline quality hook.
        
        Args:
            validator: DataQualityValidator instance
        """
        self.validator = validator
    
    def pre_load_hook(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Hook to validate data before loading to warehouse.
        
        Args:
            df: DataFrame to validate
            table_name: Target table name
        
        Returns:
            Validated (and possibly cleaned) DataFrame
        """
        result = self.validator.validate_and_clean(df, table_name)
        
        if result["action"] == "reject":
            raise ValueError(f"Data rejected for {table_name}: {result['message']}")
        
        return result["data"]
    
    def post_load_hook(self, table_name: str, row_count: int) -> Dict[str, Any]:
        """Hook to record quality metrics after load.
        
        Args:
            table_name: Table name
            row_count: Number of rows loaded
        
        Returns:
            Quality metrics
        """
        # This would typically query the database for post-load quality checks
        # For now, return basic info
        return {
            "table_name": table_name,
            "rows_loaded": row_count,
            "timestamp": pd.Timestamp.utcnow().isoformat()
        }
