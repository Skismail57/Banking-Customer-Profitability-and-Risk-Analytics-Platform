"""Data quality report generation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.data_quality.metrics import QualityMetrics

logger = logging.getLogger(__name__)


class QualityReportGenerator:
    """Generate comprehensive data quality reports."""
    
    def __init__(self, output_dir: str = "data/metadata/reports"):
        """Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, metrics: QualityMetrics, 
                       column_metrics: Optional[Dict[str, Dict[str, Any]]] = None,
                       validation_errors: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate comprehensive quality report.
        
        Args:
            metrics: QualityMetrics object
            column_metrics: Optional column-level metrics
            validation_errors: Optional validation errors
        
        Returns:
            Report dictionary
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "table_name": metrics.table_name,
                "dq_score": metrics.dq_score
            },
            "overall_assessment": self._get_overall_assessment(metrics.dq_score),
            "dimension_scores": {
                "completeness": {
                    "score": metrics.completeness,
                    "status": self._get_status(metrics.completeness),
                    "description": "Proportion of non-null values in the dataset"
                },
                "validity": {
                    "score": metrics.validity,
                    "status": self._get_status(metrics.validity),
                    "description": "Proportion of rows that pass validation rules"
                },
                "uniqueness": {
                    "score": metrics.uniqueness,
                    "status": self._get_status(metrics.uniqueness),
                    "description": "Proportion of unique rows (no duplicates)"
                },
                "consistency": {
                    "score": metrics.consistency,
                    "status": self._get_status(metrics.consistency),
                    "description": "Consistency of data types and formats"
                },
                "referential_integrity": {
                    "score": metrics.referential_integrity,
                    "status": self._get_status(metrics.referential_integrity),
                    "description": "Validity of foreign key relationships"
                }
            },
            "detailed_metrics": {
                "row_count": metrics.total_rows,
                "column_count": metrics.total_columns,
                "cell_count": metrics.total_cells,
                "missing_cells": metrics.missing_cells,
                "missing_percentage": metrics.missing_percentage,
                "columns_with_missing": metrics.columns_with_missing,
                "duplicate_rows": metrics.duplicate_rows,
                "duplicate_percentage": metrics.duplicate_percentage,
                "validation_errors": metrics.validation_errors,
                "validation_error_percentage": metrics.validation_error_percentage
            },
            "column_metrics": column_metrics or {},
            "validation_errors": validation_errors or [],
            "recommendations": self._generate_recommendations(metrics, validation_errors)
        }
        
        return report
    
    def _get_overall_assessment(self, dq_score: float) -> Dict[str, Any]:
        """Get overall assessment based on DQ score.
        
        Args:
            dq_score: Overall DQ score (0-100)
        
        Returns:
            Assessment dictionary
        """
        if dq_score >= 90:
            return {
                "status": "excellent",
                "message": "Data quality is excellent. No immediate action required.",
                "color": "green"
            }
        elif dq_score >= 75:
            return {
                "status": "good",
                "message": "Data quality is good. Minor improvements recommended.",
                "color": "blue"
            }
        elif dq_score >= 50:
            return {
                "status": "fair",
                "message": "Data quality is fair. Attention needed for several issues.",
                "color": "yellow"
            }
        else:
            return {
                "status": "poor",
                "message": "Data quality is poor. Immediate action required.",
                "color": "red"
            }
    
    def _get_status(self, score: float) -> str:
        """Get status label for a score.
        
        Args:
            score: Score value (0-100)
        
        Returns:
            Status label
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
    
    def _generate_recommendations(self, metrics: QualityMetrics,
                                   validation_errors: Optional[List[Dict[str, Any]]]) -> List[str]:
        """Generate recommendations based on quality metrics.
        
        Args:
            metrics: QualityMetrics object
            validation_errors: Optional validation errors
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Completeness recommendations
        if metrics.completeness < 90:
            recommendations.append(
                f"Completeness is {metrics.completeness}%. "
                f"Review columns with missing data: {', '.join(metrics.columns_with_missing[:5])}"
            )
        
        # Uniqueness recommendations
        if metrics.duplicate_rows > 0:
            recommendations.append(
                f"Found {metrics.duplicate_rows} duplicate rows ({metrics.duplicate_percentage}%). "
                "Review duplicate handling strategy."
            )
        
        # Validity recommendations
        if metrics.validation_errors > 0:
            recommendations.append(
                f"Found {metrics.validation_errors} validation errors ({metrics.validation_error_percentage}%). "
                "Review validation rules and data quality."
            )
        
        # Dimension-specific recommendations
        if metrics.validity < 75:
            recommendations.append(
                "Validity score is low. Review data validation rules and source data quality."
            )
        
        if metrics.consistency < 75:
            recommendations.append(
                "Consistency score is low. Review data type consistency across columns."
            )
        
        if not recommendations:
            recommendations.append("No critical issues found. Continue monitoring data quality.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save report to JSON file.
        
        Args:
            report: Report dictionary
            filename: Optional filename (auto-generated if not provided)
        
        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            table_name = report.get("report_metadata", {}).get("table_name", "unknown")
            filename = f"dq_report_{table_name}_{timestamp}.json"
        
        report_path = self.output_dir / filename
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Quality report saved to: {report_path}")
        
        return str(report_path)
    
    def generate_summary_report(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report across multiple tables.
        
        Args:
            reports: List of individual table reports
        
        Returns:
            Summary report dictionary
        """
        if not reports:
            return {"message": "No reports to summarize"}
        
        # Calculate overall statistics
        total_tables = len(reports)
        avg_dq_score = sum(r["report_metadata"]["dq_score"] for r in reports) / total_tables
        
        # Count by status
        status_counts = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        for report in reports:
            status = report["overall_assessment"]["status"]
            status_counts[status] += 1
        
        # Identify worst and best tables
        sorted_reports = sorted(reports, key=lambda x: x["report_metadata"]["dq_score"])
        worst_table = sorted_reports[0]
        best_table = sorted_reports[-1]
        
        summary = {
            "summary_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_tables": total_tables
            },
            "overall_statistics": {
                "average_dq_score": round(avg_dq_score, 2),
                "overall_status": self._get_status(avg_dq_score)
            },
            "status_distribution": status_counts,
            "best_quality": {
                "table": best_table["report_metadata"]["table_name"],
                "dq_score": best_table["report_metadata"]["dq_score"]
            },
            "worst_quality": {
                "table": worst_table["report_metadata"]["table_name"],
                "dq_score": worst_table["report_metadata"]["dq_score"]
            },
            "table_reports": reports
        }
        
        return summary
    
    def generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report for visualization.
        
        Args:
            report: Report dictionary
        
        Returns:
            HTML string
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Quality Report - {report['report_metadata']['table_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
                .excellent {{ border-color: #4CAF50; }}
                .good {{ border-color: #2196F3; }}
                .fair {{ border-color: #FF9800; }}
                .poor {{ border-color: #F44336; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Quality Report</h1>
                <p><strong>Table:</strong> {report['report_metadata']['table_name']}</p>
                <p><strong>Generated:</strong> {report['report_metadata']['generated_at']}</p>
                <p><strong>Overall DQ Score:</strong> <span class="score">{report['report_metadata']['dq_score']}</span>/100</p>
                <p><strong>Status:</strong> {report['overall_assessment']['status'].upper()}</p>
                <p><em>{report['overall_assessment']['message']}</em></p>
            </div>
            
            <h2>Dimension Scores</h2>
        """
        
        for dim_name, dim_data in report["dimension_scores"].items():
            status_class = dim_data["status"]
            html += f"""
            <div class="metric {status_class}">
                <h3>{dim_name.replace('_', ' ').title()}: {dim_data['score']}/100</h3>
                <p>Status: {dim_data['status'].upper()}</p>
                <p>{dim_data['description']}</p>
            </div>
            """
        
        html += """
            <h2>Detailed Metrics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
        """
        
        for metric_name, metric_value in report["detailed_metrics"].items():
            html += f"""
                <tr>
                    <td>{metric_name.replace('_', ' ').title()}</td>
                    <td>{metric_value}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Recommendations</h2>
            <ul>
        """
        
        for rec in report["recommendations"]:
            html += f"<li>{rec}</li>"
        
        html += """
            </ul>
        </body>
        </html>
        """
        
        return html
