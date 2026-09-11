"""Performance benchmarking for streaming pipeline.

This module provides benchmarking capabilities to establish performance baselines
and track performance over time.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import json
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Benchmark result."""
    benchmark_id: str
    benchmark_name: str
    component: str
    metric_name: str
    metric_value: float
    unit: str
    baseline_value: Optional[float]
    deviation_percent: Optional[float]
    status: str
    metadata: Dict[str, Any]
    benchmarked_at: datetime


class PerformanceBenchmark:
    """Performance benchmark manager."""
    
    def __init__(self, baseline_file: Optional[str] = None):
        """Initialize benchmark manager.
        
        Args:
            baseline_file: Path to baseline file
        """
        self.baseline_file = baseline_file
        self.baselines = self._load_baselines()
        self.benchmark_history = []
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load baseline values from file.
        
        Returns:
            Dictionary of baselines
        """
        if self.baseline_file and Path(self.baseline_file).exists():
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading baselines: {e}")
        
        return {}
    
    def _save_baselines(self):
        """Save baseline values to file."""
        if self.baseline_file:
            try:
                with open(self.baseline_file, 'w') as f:
                    json.dump(self.baselines, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving baselines: {e}")
    
    def run_benchmark(
        self,
        benchmark_name: str,
        component: str,
        metric_name: str,
        benchmark_function: Callable[[], float],
        unit: str = "ms",
        metadata: Optional[Dict[str, Any]] = None
    ) -> BenchmarkResult:
        """Run a single benchmark.
        
        Args:
            benchmark_name: Name of the benchmark
            component: Component being benchmarked
            metric_name: Name of the metric
            benchmark_function: Function that returns the metric value
            unit: Unit of measurement
            metadata: Additional metadata
        
        Returns:
            Benchmark result
        """
        benchmark_id = f"benchmark_{int(time.time())}"
        logger.info(f"Running benchmark {benchmark_id}: {benchmark_name}")
        
        # Run benchmark
        start_time = time.time()
        metric_value = benchmark_function()
        duration = time.time() - start_time
        
        # Compare with baseline
        baseline_key = f"{component}.{metric_name}"
        baseline_value = self.baselines.get(baseline_key)
        
        deviation_percent = None
        status = 'baseline'
        
        if baseline_value is not None:
            deviation_percent = ((metric_value - baseline_value) / baseline_value) * 100
            
            if abs(deviation_percent) < 5:
                status = 'within_threshold'
            elif abs(deviation_percent) < 10:
                status = 'minor_deviation'
            else:
                status = 'significant_deviation'
        
        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            benchmark_name=benchmark_name,
            component=component,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            baseline_value=baseline_value,
            deviation_percent=deviation_percent,
            status=status,
            metadata=metadata or {},
            benchmarked_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        self.benchmark_history.append(result)
        
        logger.info(
            f"Benchmark {benchmark_id} completed: {metric_value} {unit}, "
            f"status {status}"
        )
        
        return result
    
    def set_baseline(
        self,
        component: str,
        metric_name: str,
        value: float
    ):
        """Set a baseline value.
        
        Args:
            component: Component name
            metric_name: Metric name
            value: Baseline value
        """
        key = f"{component}.{metric_name}"
        self.baselines[key] = value
        self._save_baselines()
        
        logger.info(f"Set baseline {key}: {value}")
    
    def run_benchmark_suite(
        self,
        suite_name: str,
        benchmarks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run a suite of benchmarks.
        
        Args:
            suite_name: Name of the benchmark suite
            benchmarks: List of benchmark configurations
        
        Returns:
            Suite results
        """
        suite_id = f"suite_{int(time.time())}"
        logger.info(f"Running benchmark suite {suite_id}: {suite_name}")
        
        results = []
        
        for benchmark_config in benchmarks:
            try:
                result = self.run_benchmark(**benchmark_config)
                results.append(result)
            except Exception as e:
                logger.error(f"Benchmark failed: {e}")
        
        # Calculate summary
        passed = sum(1 for r in results if r.status in ['within_threshold', 'baseline'])
        total = len(results)
        
        suite_result = {
            'suite_id': suite_id,
            'suite_name': suite_name,
            'total_benchmarks': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed / total if total > 0 else 0,
            'results': results,
            'completed_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
        
        return suite_result
    
    def compare_with_previous(
        self,
        benchmark_name: str,
        component: str,
        metric_name: str
    ) -> Dict[str, Any]:
        """Compare current benchmark with previous runs.
        
        Args:
            benchmark_name: Benchmark name
            component: Component name
            metric_name: Metric name
        
        Returns:
            Comparison results
        """
        # Get all matching benchmarks
        matching = [
            b for b in self.benchmark_history
            if b.benchmark_name == benchmark_name
            and b.component == component
            and b.metric_name == metric_name
        ]
        
        if len(matching) < 2:
            return {'error': 'Insufficient history for comparison'}
        
        # Compare last two runs
        current = matching[-1]
        previous = matching[-2]
        
        change = current.metric_value - previous.metric_value
        change_percent = (change / previous.metric_value) * 100 if previous.metric_value != 0 else 0
        
        return {
            'benchmark_name': benchmark_name,
            'component': component,
            'metric_name': metric_name,
            'current_value': current.metric_value,
            'previous_value': previous.metric_value,
            'change': change,
            'change_percent': change_percent,
            'trend': 'improvement' if change < 0 else 'degradation' if change > 0 else 'stable',
            'current_benchmarked_at': current.benchmarked_at.isoformat(),
            'previous_benchmarked_at': previous.benchmarked_at.isoformat()
        }
    
    def get_benchmark_history(
        self,
        component: Optional[str] = None,
        metric_name: Optional[str] = None
    ) -> List[BenchmarkResult]:
        """Get benchmark history with optional filtering.
        
        Args:
            component: Filter by component
            metric_name: Filter by metric name
        
        Returns:
            List of benchmark results
        """
        results = self.benchmark_history
        
        if component:
            results = [r for r in results if r.component == component]
        
        if metric_name:
            results = [r for r in results if r.metric_name == metric_name]
        
        return results
    
    def generate_benchmark_report(
        self,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive benchmark report.
        
        Args:
            component: Filter by component (optional)
        
        Returns:
            Benchmark report
        """
        results = self.get_benchmark_history(component)
        
        if not results:
            return {'error': 'No benchmarks found'}
        
        # Group by metric
        by_metric = {}
        for result in results:
            key = f"{result.component}.{result.metric_name}"
            if key not in by_metric:
                by_metric[key] = []
            by_metric[key].append(result)
        
        # Calculate statistics for each metric
        metric_stats = {}
        for key, metric_results in by_metric.items():
            values = [r.metric_value for r in metric_results]
            metric_stats[key] = {
                'component': metric_results[0].component,
                'metric_name': metric_results[0].metric_name,
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'current': values[-1],
                'baseline': metric_results[0].baseline_value
            }
        
        return {
            'component': component,
            'total_benchmarks': len(results),
            'unique_metrics': len(by_metric),
            'metric_statistics': metric_stats,
            'generated_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
