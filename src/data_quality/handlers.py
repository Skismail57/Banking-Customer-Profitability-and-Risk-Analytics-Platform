"""Failed record handling and quarantine management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

import pandas as pd

from src.data_quality.base import ValidationResult

logger = logging.getLogger(__name__)


class FailedRecordHandler:
    """Handle failed records from data quality validation."""
    
    def __init__(self, quarantine_dir: str = "data/quarantine"):
        """Initialize failed record handler.
        
        Args:
            quarantine_dir: Directory to store quarantined records
        """
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def quarantine_failed_records(self, df: pd.DataFrame, 
                                   validation_result: ValidationResult,
                                   table_name: str) -> Tuple[pd.DataFrame, str]:
        """Separate failed records and quarantine them.
        
        Args:
            df: Original DataFrame
            validation_result: ValidationResult from schema validation
            table_name: Name of the table
        
        Returns:
            Tuple of (valid_df, quarantine_path)
        """
        if validation_result.is_valid:
            # All records valid, return original
            return df, ""
        
        # Extract failed records based on validation errors
        failed_indices = self._extract_failed_indices(validation_result, df)
        
        if not failed_indices:
            # No specific failures found, return all as valid
            return df, ""
        
        # Separate valid and failed records
        failed_df = df.iloc[failed_indices].copy()
        valid_df = df.drop(failed_indices).copy()
        
        # Add quarantine metadata
        failed_df["_quarantine_timestamp"] = datetime.utcnow().isoformat()
        failed_df["_quarantine_table"] = table_name
        failed_df["_quarantine_reason"] = "validation_failure"
        
        # Save quarantined records
        quarantine_path = self._save_quarantine(failed_df, table_name)
        
        logger.warning(
            f"Quarantined {len(failed_df)} records from {table_name}. "
            f"Valid records: {len(valid_df)}"
        )
        
        return valid_df, quarantine_path
    
    def _extract_failed_indices(self, validation_result: ValidationResult,
                                 df: pd.DataFrame) -> List[int]:
        """Extract indices of failed records from validation result.
        
        Args:
            validation_result: ValidationResult
            df: Original DataFrame
        
        Returns:
            List of failed row indices
        """
        failed_indices = []
        
        for error in validation_result.errors:
            row_number = error.get("row_number")
            if row_number is not None and isinstance(row_number, int):
                # Pandera uses 0-based indexing
                if 0 <= row_number < len(df):
                    failed_indices.append(row_number)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(failed_indices))
    
    def _save_quarantine(self, failed_df: pd.DataFrame, table_name: str) -> str:
        """Save quarantined records to file.
        
        Args:
            failed_df: DataFrame of failed records
            table_name: Name of the table
        
        Returns:
            Path to quarantined file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"quarantine_{table_name}_{timestamp}.parquet"
        quarantine_path = self.quarantine_dir / filename
        
        failed_df.to_parquet(quarantine_path, index=False)
        
        # Save metadata
        metadata = {
            "table_name": table_name,
            "quarantine_timestamp": timestamp,
            "record_count": len(failed_df),
            "columns": list(failed_df.columns)
        }
        
        metadata_path = quarantine_path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Quarantined records saved to: {quarantine_path}")
        
        return str(quarantine_path)
    
    def get_quarantine_summary(self) -> Dict[str, Any]:
        """Get summary of quarantined records.
        
        Returns:
            Summary dictionary
        """
        summary = {
            "total_quarantine_files": 0,
            "total_quarantined_records": 0,
            "tables_quarantined": {},
            "quarantine_files": []
        }
        
        # Find all quarantine files
        quarantine_files = list(self.quarantine_dir.glob("quarantine_*.parquet"))
        summary["total_quarantine_files"] = len(quarantine_files)
        
        for qf in quarantine_files:
            # Load metadata
            metadata_path = qf.with_suffix(".json")
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                
                table_name = metadata.get("table_name", "unknown")
                record_count = metadata.get("record_count", 0)
                
                summary["total_quarantined_records"] += record_count
                
                if table_name not in summary["tables_quarantined"]:
                    summary["tables_quarantined"][table_name] = 0
                summary["tables_quarantined"][table_name] += record_count
                
                summary["quarantine_files"].append({
                    "file": str(qf.name),
                    "table": table_name,
                    "records": record_count,
                    "timestamp": metadata.get("quarantine_timestamp")
                })
        
        return summary
    
    def load_quarantined_records(self, table_name: Optional[str] = None,
                                 limit: Optional[int] = None) -> pd.DataFrame:
        """Load quarantined records for review.
        
        Args:
            table_name: Optional table name filter
            limit: Optional limit on number of records
        
        Returns:
            DataFrame of quarantined records
        """
        quarantine_files = list(self.quarantine_dir.glob("quarantine_*.parquet"))
        
        if table_name:
            quarantine_files = [f for f in quarantine_files if table_name in f.name]
        
        dfs = []
        for qf in quarantine_files:
            df = pd.read_parquet(qf)
            dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        combined_df = pd.concat(dfs, ignore_index=True)
        
        if limit:
            combined_df = combined_df.head(limit)
        
        return combined_df
    
    def restore_quarantined_records(self, quarantine_file: str) -> pd.DataFrame:
        """Restore quarantined records from quarantine.
        
        Args:
            quarantine_file: Name of quarantine file to restore
        
        Returns:
            DataFrame of restored records
        """
        quarantine_path = self.quarantine_dir / quarantine_file
        
        if not quarantine_path.exists():
            raise FileNotFoundError(f"Quarantine file not found: {quarantine_file}")
        
        df = pd.read_parquet(quarantine_path)
        
        # Remove quarantine metadata columns
        quarantine_cols = [col for col in df.columns if col.startswith("_quarantine_")]
        df = df.drop(columns=quarantine_cols)
        
        logger.info(f"Restored {len(df)} records from quarantine: {quarantine_file}")
        
        return df
    
    def cleanup_old_quarantine(self, days_old: int = 30) -> int:
        """Clean up quarantine files older than specified days.
        
        Args:
            days_old: Age in days for cleanup threshold
        
        Returns:
            Number of files cleaned up
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cleaned_count = 0
        
        for qf in self.quarantine_dir.glob("quarantine_*.parquet"):
            file_mtime = datetime.fromtimestamp(qf.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                # Remove parquet file
                qf.unlink()
                
                # Remove metadata file
                metadata_path = qf.with_suffix(".json")
                if metadata_path.exists():
                    metadata_path.unlink()
                
                cleaned_count += 1
                logger.info(f"Cleaned up old quarantine file: {qf.name}")
        
        return cleaned_count


class DataQualityThreshold:
    """Define thresholds for data quality actions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize threshold configuration.
        
        Args:
            config: Configuration dictionary with thresholds
        """
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default threshold configuration."""
        return {
            "dq_score": {
                "critical": 50,  # Below this, reject data
                "warning": 75   # Below this, warn but accept
            },
            "completeness": {
                "critical": 70,
                "warning": 90
            },
            "validity": {
                "critical": 80,
                "warning": 95
            },
            "uniqueness": {
                "critical": 90,
                "warning": 98
            },
            "max_failure_percentage": {
                "critical": 10,  # More than 10% failures = critical
                "warning": 5     # More than 5% failures = warning
            }
        }
    
    def get_action(self, metrics: Any, validation_result: ValidationResult) -> str:
        """Determine action based on quality metrics.
        
        Args:
            metrics: QualityMetrics object
            validation_result: ValidationResult
        
        Returns:
            Action: "accept", "warn", "reject", "quarantine"
        """
        dq_score = metrics.dq_score
        failure_percentage = validation_result.invalid_rows / validation_result.total_rows if validation_result.total_rows > 0 else 0
        
        # Check critical thresholds
        if dq_score < self.config["dq_score"]["critical"]:
            return "reject"
        
        if failure_percentage > self.config["max_failure_percentage"]["critical"]:
            return "quarantine"
        
        # Check warning thresholds
        if dq_score < self.config["dq_score"]["warning"]:
            return "warn"
        
        if failure_percentage > self.config["max_failure_percentage"]["warning"]:
            return "warn"
        
        # Check individual dimensions
        if metrics.completeness < self.config["completeness"]["critical"]:
            return "reject"
        
        if metrics.validity < self.config["validity"]["critical"]:
            return "reject"
        
        if metrics.uniqueness < self.config["uniqueness"]["critical"]:
            return "reject"
        
        # All checks passed
        return "accept"
