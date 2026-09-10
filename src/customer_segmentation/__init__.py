"""Customer Segmentation package."""

from src.customer_segmentation.base import (
    SegmentationMethod,
    SegmentDefinition,
    CustomerSegmentationBase,
)
from src.customer_segmentation.business_rules import BusinessRuleSegmenter
from src.customer_segmentation.features import FeatureEngineer
from src.customer_segmentation.clustering import (
    KMeansClusterer,
    HierarchicalClusterer,
    DBSCANClusterer,
)
from src.customer_segmentation.evaluation import ClusterEvaluator
from src.customer_segmentation.profiling import SegmentProfiler
from src.customer_segmentation.stability import StabilityAnalyzer
from src.customer_segmentation.orchestrator import SegmentationOrchestrator

__all__ = [
    "SegmentationMethod",
    "SegmentDefinition",
    "CustomerSegmentationBase",
    "BusinessRuleSegmenter",
    "FeatureEngineer",
    "KMeansClusterer",
    "HierarchicalClusterer",
    "DBSCANClusterer",
    "ClusterEvaluator",
    "SegmentProfiler",
    "StabilityAnalyzer",
    "SegmentationOrchestrator",
]
