"""Orchestrator for managing end-to-end ingestion pipelines."""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.ingestion.base import IngestionMetadata, IngestionError
from src.ingestion.extractors import ExtractorFactory
from src.ingestion.loaders import RawLoader, StagingLoader, WarehouseLoader
from src.ingestion.cleaners import DataCleaner, DataTransformer
from src.ingestion.schema import DataQualityChecker, SchemaValidator
from src.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class IngestionOrchestrator:
    """Orchestrates the complete ingestion pipeline: RAW -> STAGING -> CLEAN -> WAREHOUSE."""
    
    def __init__(self, config_path: str = "config/ingestion.yaml"):
        """Initialize orchestrator.
        
        Args:
            config_path: Path to ingestion configuration file
        """
        self.config = self._load_config(config_path)
        self.pipeline_results: List[Dict[str, Any]] = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Configuration dictionary
        """
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def run_source_ingestion(self, source_name: str) -> Dict[str, Any]:
        """Run complete ingestion pipeline for a single source.
        
        Args:
            source_name: Name of the source to ingest
        
        Returns:
            Dictionary containing pipeline results
        """
        logger.info(f"Starting ingestion for source: {source_name}")
        
        result = {
            "source": source_name,
            "start_time": datetime.utcnow().isoformat(),
            "stages": {},
            "status": "in_progress"
        }
        
        try:
            # Get source configuration
            source_config = self.config["sources"][source_name]
            source_config["name"] = source_name
            
            # Stage 1: Extract to RAW
            raw_result = self._stage_extract(source_config)
            result["stages"]["raw"] = raw_result
            
            if raw_result["status"] != "success":
                result["status"] = "failed"
                result["error"] = raw_result.get("error")
                return result
            
            # Stage 2: Transform to STAGING
            staging_result = self._stage_transform(raw_result["data"], raw_result["metadata"])
            result["stages"]["staging"] = staging_result
            
            if staging_result["status"] != "success":
                result["status"] = "failed"
                result["error"] = staging_result.get("error")
                return result
            
            # Stage 3: Clean
            clean_result = self._stage_clean(staging_result["data"])
            result["stages"]["clean"] = clean_result
            
            if clean_result["status"] != "success":
                result["status"] = "failed"
                result["error"] = clean_result.get("error")
                return result
            
            # Stage 4: Load to WAREHOUSE (optional)
            if source_config.get("load_to_warehouse", False):
                warehouse_result = self._stage_warehouse(
                    clean_result["data"],
                    staging_result["metadata"]
                )
                result["stages"]["warehouse"] = warehouse_result
                
                if warehouse_result["status"] != "success":
                    result["status"] = "partial_success"
                    result["error"] = warehouse_result.get("error")
                else:
                    result["status"] = "success"
            else:
                result["status"] = "success"
            
            result["end_time"] = datetime.utcnow().isoformat()
            result["final_row_count"] = len(clean_result["data"])
            
            logger.info(f"Ingestion completed for source: {source_name}")
            
        except Exception as e:
            logger.error(f"Ingestion failed for source {source_name}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
        
        self.pipeline_results.append(result)
        return result
    
    def run_all_sources(self) -> Dict[str, Any]:
        """Run ingestion for all configured sources.
        
        Returns:
            Dictionary containing overall results
        """
        logger.info("Starting ingestion for all sources")
        
        overall_result = {
            "start_time": datetime.utcnow().isoformat(),
            "sources": {},
            "summary": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "partial_success": 0
            }
        }
        
        for source_name in self.config["sources"].keys():
            source_result = self.run_source_ingestion(source_name)
            overall_result["sources"][source_name] = source_result
            
            # Update summary
            overall_result["summary"]["total"] += 1
            status = source_result["status"]
            if status == "success":
                overall_result["summary"]["successful"] += 1
            elif status == "failed":
                overall_result["summary"]["failed"] += 1
            elif status == "partial_success":
                overall_result["summary"]["partial_success"] += 1
        
        overall_result["end_time"] = datetime.utcnow().isoformat()
        
        logger.info(f"All source ingestion completed. Success: {overall_result['summary']['successful']}, Failed: {overall_result['summary']['failed']}")
        
        return overall_result
    
    def _stage_extract(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 1: Extract data from source to RAW storage.
        
        Args:
            source_config: Source configuration
        
        Returns:
            Stage result dictionary
        """
        logger.info(f"Stage 1: Extract - {source_config['name']}")
        
        result = {
            "stage": "extract",
            "status": "in_progress",
            "start_time": datetime.utcnow().isoformat()
        }
        
        try:
            # Create extractor
            extractor = ExtractorFactory.create_extractor(source_config)
            
            # Extract data
            df = extractor.extract()
            
            # Create raw loader
            storage_config = {
                "path": self.config["storage"]["raw"],
                "compress": self.config["pipeline"]["compress_raw"],
                "compression_type": self.config["pipeline"]["compression_type"],
                "metadata_path": self.config["storage"]["metadata"]
            }
            loader = RawLoader(storage_config)
            
            # Load to raw storage
            output_path = loader.load(df, extractor.metadata)
            
            result["status"] = "success"
            result["row_count"] = len(df)
            result["output_path"] = output_path
            result["metadata"] = extractor.metadata.to_dict()
            result["end_time"] = datetime.utcnow().isoformat()
            
            # Return data for next stage
            result["data"] = df
            result["metadata"] = extractor.metadata
            
        except Exception as e:
            logger.error(f"Extract stage failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
        
        return result
    
    def _stage_transform(self, df: pd.DataFrame, metadata: IngestionMetadata) -> Dict[str, Any]:
        """Stage 2: Transform data to STAGING with validation.
        
        Args:
            df: DataFrame from raw stage
            metadata: Ingestion metadata
        
        Returns:
            Stage result dictionary
        """
        logger.info(f"Stage 2: Transform - {metadata.source_name}")
        
        result = {
            "stage": "transform",
            "status": "in_progress",
            "start_time": datetime.utcnow().isoformat()
        }
        
        try:
            # Data quality check
            quality_config = self.config["data_quality"]
            quality_checker = DataQualityChecker(quality_config)
            quality_passed, quality_report = quality_checker.check(df)
            
            result["quality_report"] = quality_report
            
            if not quality_passed:
                logger.warning(f"Data quality checks failed: {quality_report}")
                result["status"] = "partial_success"
                result["quality_error"] = "Data quality checks failed"
            else:
                result["status"] = "success"
            
            # Create staging loader
            storage_config = {
                "path": self.config["storage"]["staging"]
            }
            loader = StagingLoader(storage_config)
            
            # Load to staging
            output_path = loader.load(df, metadata)
            
            result["output_path"] = output_path
            result["row_count"] = len(df)
            result["end_time"] = datetime.utcnow().isoformat()
            
            # Return data for next stage
            result["data"] = df
            result["metadata"] = metadata
            
        except Exception as e:
            logger.error(f"Transform stage failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
        
        return result
    
    def _stage_clean(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Stage 3: Clean data.
        
        Args:
            df: DataFrame from staging stage
        
        Returns:
            Stage result dictionary
        """
        logger.info("Stage 3: Clean")
        
        result = {
            "stage": "clean",
            "status": "in_progress",
            "start_time": datetime.utcnow().isoformat()
        }
        
        try:
            # Create cleaner
            cleaner_config = {
                "handle_duplicates": self.config["data_quality"]["handle_duplicates"],
                "duplicate_strategy": self.config["data_quality"]["duplicate_strategy"],
                "trim_strings": True,
                "standardize_dates": True
            }
            cleaner = DataCleaner(cleaner_config)
            
            # Clean data
            df_cleaned = cleaner.clean(df)
            
            result["status"] = "success"
            result["row_count_before"] = len(df)
            result["row_count_after"] = len(df_cleaned)
            result["rows_removed"] = len(df) - len(df_cleaned)
            result["end_time"] = datetime.utcnow().isoformat()
            
            # Return cleaned data
            result["data"] = df_cleaned
            
        except Exception as e:
            logger.error(f"Clean stage failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
            result["data"] = df  # Return original data on failure
        
        return result
    
    def _stage_warehouse(self, df: pd.DataFrame, metadata: IngestionMetadata) -> Dict[str, Any]:
        """Stage 4: Load data to warehouse database.
        
        Args:
            df: DataFrame from clean stage
            metadata: Ingestion metadata
        
        Returns:
            Stage result dictionary
        """
        logger.info(f"Stage 4: Warehouse - {metadata.target_table}")
        
        result = {
            "stage": "warehouse",
            "status": "in_progress",
            "start_time": datetime.utcnow().isoformat()
        }
        
        try:
            # Get database manager
            db_manager = DatabaseManager()
            
            # Create warehouse loader
            storage_config = {
                "path": self.config["storage"]["warehouse"]
            }
            loader = WarehouseLoader(storage_config, db_manager)
            
            # Update metadata with target table
            source_config = self.config["sources"][metadata.source_name]
            metadata.target_table = source_config.get("target_table")
            
            # Load to warehouse
            table_name = loader.load(df, metadata)
            
            result["status"] = "success"
            result["table_name"] = table_name
            result["row_count"] = len(df)
            result["end_time"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Warehouse stage failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
        
        return result
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get summary of all pipeline runs.
        
        Returns:
            Summary dictionary
        """
        if not self.pipeline_results:
            return {"message": "No pipeline runs yet"}
        
        summary = {
            "total_runs": len(self.pipeline_results),
            "successful": sum(1 for r in self.pipeline_results if r["status"] == "success"),
            "failed": sum(1 for r in self.pipeline_results if r["status"] == "failed"),
            "partial_success": sum(1 for r in self.pipeline_results if r["status"] == "partial_success"),
            "runs": self.pipeline_results
        }
        
        return summary
