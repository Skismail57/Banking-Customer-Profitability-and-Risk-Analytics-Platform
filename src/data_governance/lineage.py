"""Data Lineage Tracking.

This module implements data lineage tracking to trace the flow of data
through the analytics pipeline from source to destination.

Key Lineage Capabilities:
- Source-to-destination mapping
- Transformation tracking
- Data dependency graph
- Impact analysis
- Audit trail

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of data transformations."""
    EXTRACTION = "extraction"
    LOADING = "loading"
    CLEANING = "cleaning"
    AGGREGATION = "aggregation"
    CALCULATION = "calculation"
    FILTERING = "filtering"
    JOIN = "join"
    PIVOT = "pivot"
    ENRICHMENT = "enrichment"


class DataLineageTracker:
    """Track data lineage through the analytics pipeline.
    
    This class provides visibility into how data flows through the system,
    enabling impact analysis and audit trails.
    
    Assumptions:
    - All data transformations are logged
    - Source and destination tables are known
    - Transformation metadata is captured
    
    Limitations:
    - Requires manual registration of transformations
    - Does not automatically detect lineage
    - May not capture all implicit dependencies
    - Lineage is only as good as the logging
    
    Fairness Considerations:
    - Ensure lineage tracking is consistent across all data
    - Check for disparate impact in data transformations
    - Ensure audit trail is complete and unbiased
    - Regular audit for bias in lineage tracking
    """
    
    def __init__(self):
        """Initialize Data Lineage Tracker."""
        self.lineage_graph: Dict[str, List[Dict[str, Any]]] = {}
        self.transformation_log: List[Dict[str, Any]] = []
    
    def log_transformation(
        self,
        source: str,
        destination: str,
        transformation_type: TransformationType,
        transformation_details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Log a data transformation.
        
        Args:
            source: Source table/system
            destination: Destination table/system
            transformation_type: Type of transformation
            transformation_details: Additional details about transformation
            timestamp: Timestamp of transformation
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        transformation_record = {
            'source': source,
            'destination': destination,
            'transformation_type': transformation_type.value,
            'transformation_details': transformation_details or {},
            'timestamp': timestamp.isoformat()
        }
        
        self.transformation_log.append(transformation_record)
        
        # Update lineage graph
        if source not in self.lineage_graph:
            self.lineage_graph[source] = []
        
        self.lineage_graph[source].append({
            'destination': destination,
            'transformation_type': transformation_type.value,
            'timestamp': timestamp.isoformat()
        })
        
        logger.info(f"Logged transformation: {source} -> {destination} ({transformation_type.value})")
    
    def get_lineage(self, table: str) -> Dict[str, Any]:
        """Get lineage for a specific table.
        
        Args:
            table: Table name
        
        Returns:
            Dictionary with lineage information
        """
        # Find upstream sources
        upstream = self._find_upstream(table)
        
        # Find downstream destinations
        downstream = self._find_downstream(table)
        
        return {
            'table': table,
            'upstream_sources': upstream,
            'downstream_destinations': downstream,
            'transformation_count': len(self.transformation_log)
        }
    
    def _find_upstream(self, table: str, visited: Optional[set] = None) -> List[str]:
        """Find all upstream sources for a table.
        
        Args:
            table: Table name
            visited: Set of visited tables (to prevent cycles)
        
        Returns:
            List of upstream sources
        """
        if visited is None:
            visited = set()
        
        if table in visited:
            return []
        
        visited.add(table)
        
        upstream = []
        
        for source, destinations in self.lineage_graph.items():
            for dest_info in destinations:
                if dest_info['destination'] == table:
                    upstream.append(source)
                    upstream.extend(self._find_upstream(source, visited))
        
        return list(set(upstream))
    
    def _find_downstream(self, table: str, visited: Optional[set] = None) -> List[str]:
        """Find all downstream destinations for a table.
        
        Args:
            table: Table name
            visited: Set of visited tables (to prevent cycles)
        
        Returns:
            List of downstream destinations
        """
        if visited is None:
            visited = set()
        
        if table in visited:
            return []
        
        visited.add(table)
        
        downstream = []
        
        if table in self.lineage_graph:
            for dest_info in self.lineage_graph[table]:
                downstream.append(dest_info['destination'])
                downstream.extend(self._find_downstream(dest_info['destination'], visited))
        
        return list(set(downstream))
    
    def analyze_impact(
        self,
        source_table: str,
        impact_type: str = "modification"
    ) -> Dict[str, Any]:
        """Analyze impact of changes to a source table.
        
        Args:
            source_table: Source table that changed
            impact_type: Type of change (modification, deletion, addition)
        
        Returns:
            Dictionary with impact analysis
        """
        downstream = self._find_downstream(source_table)
        
        impact_analysis = {
            'source_table': source_table,
            'impact_type': impact_type,
            'directly_affected': [],
            'indirectly_affected': [],
            'total_affected': len(downstream)
        }
        
        # Find directly affected (one hop)
        if source_table in self.lineage_graph:
            for dest_info in self.lineage_graph[source_table]:
                impact_analysis['directly_affected'].append(dest_info['destination'])
        
        # Find indirectly affected (more than one hop)
        directly_affected = set(impact_analysis['directly_affected'])
        impact_analysis['indirectly_affected'] = [t for t in downstream if t not in directly_affected]
        
        return impact_analysis
    
    def get_transformation_history(
        self,
        table: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get transformation history.
        
        Args:
            table: Optional table to filter by
            limit: Maximum number of records to return
        
        Returns:
            List of transformation records
        """
        if table:
            filtered_log = [
                record for record in self.transformation_log
                if record['source'] == table or record['destination'] == table
            ]
        else:
            filtered_log = self.transformation_log
        
        return filtered_log[-limit:]
    
    def generate_lineage_report(self) -> Dict[str, Any]:
        """Generate comprehensive lineage report.
        
        Returns:
            Dictionary with lineage report
        """
        logger.info("Generating lineage report")
        
        # Calculate statistics
        total_transformations = len(self.transformation_log)
        unique_sources = len(set(record['source'] for record in self.transformation_log))
        unique_destinations = len(set(record['destination'] for record in self.transformation_log))
        
        # Count by transformation type
        transformation_counts = {}
        for record in self.transformation_log:
            t_type = record['transformation_type']
            transformation_counts[t_type] = transformation_counts.get(t_type, 0) + 1
        
        return {
            'total_transformations': total_transformations,
            'unique_sources': unique_sources,
            'unique_destinations': unique_destinations,
            'transformation_counts': transformation_counts,
            'lineage_graph': self.lineage_graph,
            'assumptions': [
                'All transformations are logged',
                'Source and destination tables are known',
                'Transformation metadata is captured'
            ],
            'limitations': [
                'Requires manual registration of transformations',
                'Does not automatically detect lineage',
                'May not capture all implicit dependencies',
                'Lineage is only as good as the logging'
            ],
            'fairness_considerations': [
                'Ensure lineage tracking is consistent',
                'Check for disparate impact in transformations',
                'Ensure audit trail is complete',
                'Regular audit for bias in lineage tracking'
            ]
        }
    
    def export_lineage(self, filepath: str) -> None:
        """Export lineage data to file.
        
        Args:
            filepath: Path to export file
        """
        lineage_data = {
            'lineage_graph': self.lineage_graph,
            'transformation_log': self.transformation_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(lineage_data, f, indent=2, default=str)
        
        logger.info(f"Lineage data exported to {filepath}")
