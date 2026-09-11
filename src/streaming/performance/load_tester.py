"""Load testing for streaming pipeline.

This module provides load testing capabilities to validate system performance
under expected load conditions.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import threading
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result."""
    test_id: str
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    duration_seconds: float
    requests_per_second: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    error_rate: float
    started_at: datetime
    completed_at: datetime


class LoadTester:
    """Load tester for performance validation."""
    
    def __init__(self):
        """Initialize load tester."""
        self.test_history = []
    
    def run_load_test(
        self,
        test_name: str,
        target_function: Callable,
        requests_per_second: int,
        duration_seconds: int,
        concurrent_users: int = 1,
        payload: Optional[Dict[str, Any]] = None
    ) -> LoadTestResult:
        """Run a load test.
        
        Args:
            test_name: Name of the load test
            target_function: Function to test
            requests_per_second: Target requests per second
            duration_seconds: Duration of the test
            concurrent_users: Number of concurrent users
            payload: Payload for the function
        
        Returns:
            Load test result
        """
        test_id = f"load_test_{int(time.time())}"
        logger.info(f"Starting load test {test_id}: {test_name}")
        
        started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        latencies = []
        successful = 0
        failed = 0
        
        # Calculate delay between requests
        delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        
        end_time = time.time() + duration_seconds
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            while time.time() < end_time:
                future = executor.submit(
                    self._execute_request,
                    target_function,
                    payload
                )
                futures.append(future)
                
                # Wait for delay
                if delay > 0:
                    time.sleep(delay)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    latency, success = future.result()
                    latencies.append(latency)
                    if success:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Error in request execution: {e}")
                    failed += 1
        
        completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        duration = (completed_at - started_at).total_seconds()
        
        # Calculate statistics
        total_requests = successful + failed
        rps = total_requests / duration if duration > 0 else 0
        
        result = LoadTestResult(
            test_id=test_id,
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            duration_seconds=duration,
            requests_per_second=rps,
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
            p50_latency_ms=self._percentile(latencies, 50) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            min_latency_ms=min(latencies) if latencies else 0,
            error_rate=failed / total_requests if total_requests > 0 else 0,
            started_at=started_at,
            completed_at=completed_at
        )
        
        self.test_history.append(result)
        
        logger.info(
            f"Load test {test_id} completed: {successful}/{total_requests} successful, "
            f"{rps:.2f} RPS, avg latency {result.avg_latency_ms:.2f}ms"
        )
        
        return result
    
    def _execute_request(
        self,
        target_function: Callable,
        payload: Optional[Dict[str, Any]]
    ) -> tuple:
        """Execute a single request.
        
        Args:
            target_function: Function to execute
            payload: Function payload
        
        Returns:
            Tuple of (latency_ms, success)
        """
        start_time = time.time()
        
        try:
            if payload:
                target_function(payload)
            else:
                target_function()
            
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, True
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Request failed: {e}")
            return latency_ms, False
    
    def _percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile.
        
        Args:
            data: List of values
            p: Percentile (0-100)
        
        Returns:
            Percentile value
        """
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_test_history(self) -> List[LoadTestResult]:
        """Get load test history.
        
        Returns:
            List of test results
        """
        return self.test_history.copy()
    
    def compare_results(
        self,
        test_id_1: str,
        test_id_2: str
    ) -> Dict[str, Any]:
        """Compare two load test results.
        
        Args:
            test_id_1: First test ID
            test_id_2: Second test ID
        
        Returns:
            Comparison results
        """
        result1 = next((r for r in self.test_history if r.test_id == test_id_1), None)
        result2 = next((r for r in self.test_history if r.test_id == test_id_2), None)
        
        if not result1 or not result2:
            return {'error': 'One or both test IDs not found'}
        
        return {
            'test_1': result1.test_id,
            'test_2': result2.test_id,
            'rps_change': result2.requests_per_second - result1.requests_per_second,
            'rps_change_percent': (
                (result2.requests_per_second - result1.requests_per_second) /
                result1.requests_per_second * 100 if result1.requests_per_second > 0 else 0
            ),
            'latency_change_ms': result2.avg_latency_ms - result1.avg_latency_ms,
            'latency_change_percent': (
                (result2.avg_latency_ms - result1.avg_latency_ms) /
                result1.avg_latency_ms * 100 if result1.avg_latency_ms > 0 else 0
            ),
            'error_rate_change': result2.error_rate - result1.error_rate
        }
