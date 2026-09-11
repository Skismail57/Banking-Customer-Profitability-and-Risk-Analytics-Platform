"""Data lineage for streaming pipeline.

This module provides data lineage tracking capabilities to trace data
through the pipeline and understand data transformations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of data transformations."""
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    MAP = "map"
    REDUCE = "reduce"
    ENRICH = "enrich"
    VALIDATE = "validate"


@dataclass
class LineageEvent:
    """Data lineage event."""
    event_id: str
    source_system: str
    source_table: str
    target_system: str
    target_table: str
    transformation_type: str
    transformation_details: Dict[str, Any]
    record_count: int
    timestamp: datetime
    metadata: Dict[str, Any]


class DataLineage:
    """Data lineage tracker for pipeline monitoring."""
    
    def __init__(self):
        """Initialize data lineage tracker."""
        self.lineage_events = []
        self.lineage_graph = {}
    
    def track_transformation(
        self,
        source_system: str,
        source_table: str,
        target_system: str,
        target_table: str,
        transformation_type: TransformationType,
        transformation_details: Dict[str, Any],
        record_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track a data transformation.
        
        Args:
            source_system: Source system name
            source_table: Source table name
            target_system: Target system name
            target_table: Target table name
            transformation_type: Type of transformation
            transformation_details: Transformation details
            record_count: Number of records
            metadata: Additional metadata
        
        Returns:
            Event ID
        """
        event_id = f"lineage_{int(datetime.now(timezone.utc).replace(tzinfo=None).timestamp())}"
        
        event = LineageEvent(
            event_id=event_id,
            source_system=source_system,
            source_table=source_table,
            target_system=target_system,
            target_table=target_table,
            transformation_type=transformation_type.value,
            transformation_details=transformation_details,
            record_count=record_count,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            metadata=metadata or {}
        )
        
        self.lineage_events.append(event)
        self._update_lineage_graph(event)
        
        logger.info(
            f"Tracked transformation: {source_system}.{source_table} -> "
            f"{target_system}.{target_table} ({transformation_type.value})"
        )
        
        return event_id
    
    def _update_lineage_graph(self, event: LineageEvent):
        """Update lineage graph with new event.
        
        Args:
            event: Lineage event
        """
        source_key = f"{event.source_system}.{event.source_table}"
        target_key = f"{event.target_system}.{event.target_table}"
        
        if source_key not in self.lineage_graph:
            self.lineage_graph[source_key] = []
        
        self.lineage_graph[source_key].append({
            'target': target_key,
            'transformation_type': event.transformation_type,
            'timestamp': event.timestamp.isoformat()
        })
    
    def get_lineage_for_table(
        self,
        system: str,
        table: str
    ) -> List[Dict[str, Any]]:
        """Get lineage for a specific table.
        
        Args:
            system: System name
            table: Table name
        
        Returns:
            List of lineage events
        """
        table_key = f"{system}.{table}"
        
        # Get upstream lineage
        upstream = []
        for event in self.lineage_events:
            if f"{event.target_system}.{event.target_table}" == table_key:
                upstream.append({
                    'source': f"{event.source_system}.{event.source_table}",
                    'transformation': event.transformation_type,
                    'timestamp': event.timestamp.isoformat()
                })
        
        # Get downstream lineage
        downstream = []
        if table_key in self.lineage_graph:
            downstream = self.lineage_graph[table_key]
        
        return {
            'table': table_key,
            'upstream': upstream,
            'downstream': downstream
        }
    
    def get_transformation_chain(
        self,
        source_system: str,
        source_table: str,
        target_system: str,
        target_table: str
    ) -> List[Dict[str, Any]]:
        """Get full transformation chain from source to target.
        
        Args:
            source_system: Source system name
            source_table: Source table name
            target_system: Target system name
            target_table: Target table name
        
        Returns:
            List of transformations in the chain
        """
        source_key = f"{source_system}.{source_table}"
        target_key = f"{target_system}.{target_table}"
        
        chain = []
        visited = set()
        
        def dfs(current_key, path):
            if current_key in visited:
                return None
            visited.add(current_key)
            
            if current_key == target_key:
                return path
            
            if current_key in self.lineage_graph:
                for edge in self.lineage_graph[current_key]:
                    result = dfs(edge['target'], path + [edge])
                    if result:
                        return result
            
            return None
        
        result = dfs(source_key, [])
        
        if result:
            return result
        
        return []
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get lineage summary.
        
        Returns:
            Lineage summary
        """
        if not self.lineage_events:
            return {'message': 'No lineage events recorded'}
        
        # Count by transformation type
        by_transformation = {}
        for event in self.lineage_events:
            trans_type = event.transformation_type
            if trans_type not in by_transformation:
                by_transformation[trans_type] = 0
            by_transformation[trans_type] += 1
        
        # Count by system
        by_system = {}
        for event in self.lineage_events:
            source = event.source_system
            target = event.target_system
            if source not in by_system:
                by_system[source] = 0
            by_system[source] += 1
            if target not in by_system:
                by_system[target] = 0
            by_system[target] += 1
        
        return {
            'total_events': len(self.lineage_events),
            'total_records_processed': sum(e.record_count for e in self.lineage_events),
            'by_transformation': by_transformation,
            'by_system': by_system,
            'unique_tables': len(self.lineage_graph)
        }
    
    def export_lineage(self, format: str = "json") -> str:
        """Export lineage data.
        
        Args:
            format: Export format (json, csv)
        
        Returns:
            Exported data string
        """
        if format == "json":
            return json.dumps([asdict(e) for e in self.lineage_events], indent=2)
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'event_id', 'source_system', 'source_table',
                'target_system', 'target_table', 'transformation_type',
                'record_count', 'timestamp'
            ])
            
            # Data
            for event in self.lineage_events:
                writer.writerow([
                    event.event_id, event.source_system, event.source_table,
                    event.target_system, event.target_table, event.transformation_type,
                    event.record_count, event.timestamp.isoformat()
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format}")
