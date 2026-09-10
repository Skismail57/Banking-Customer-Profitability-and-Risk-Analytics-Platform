"""Base classes for customer segmentation."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SegmentationMethod(Enum):
    """Segmentation method types."""
    BUSINESS_RULES = "business_rules"
    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"
    DBSCAN = "dbscan"


@dataclass
class SegmentDefinition:
    """Definition of a customer segment."""
    
    name: str
    description: str
    method: SegmentationMethod
    criteria: Dict[str, Any]
    business_interpretation: str
    recommended_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "method": self.method.value,
            "criteria": self.criteria,
            "business_interpretation": self.business_interpretation,
            "recommended_actions": self.recommended_actions
        }


@dataclass
class SegmentProfile:
    """Profile of a customer segment."""
    
    segment_name: str
    customer_count: int
    percentage: float
    characteristics: Dict[str, Any]
    business_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "segment_name": self.segment_name,
            "customer_count": self.customer_count,
            "percentage": self.percentage,
            "characteristics": self.characteristics,
            "business_metrics": self.business_metrics
        }


class CustomerSegmentationBase:
    """Base class for customer segmentation."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize segmentation base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        self.segment_registry: Dict[str, SegmentDefinition] = {}
    
    def register_segment(self, segment: SegmentDefinition) -> None:
        """Register a segment definition.
        
        Args:
            segment: Segment definition to register
        """
        self.segment_registry[segment.name] = segment
        logger.info(f"Registered segment: {segment.name}")
    
    def get_segment_definition(self, segment_name: str) -> Optional[SegmentDefinition]:
        """Get segment definition by name.
        
        Args:
            segment_name: Name of the segment
        
        Returns:
            SegmentDefinition if found, None otherwise
        """
        return self.segment_registry.get(segment_name)
    
    def get_all_segment_definitions(self) -> Dict[str, SegmentDefinition]:
        """Get all registered segment definitions.
        
        Returns:
            Dictionary of segment definitions
        """
        return self.segment_registry.copy()
