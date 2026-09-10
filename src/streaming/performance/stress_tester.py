"""Stress testing for streaming pipeline.

This module provides stress testing capabilities to validate system behavior
under extreme load conditions beyond normal operational limits.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StressTestResult:
    """Stress test result."""
    test_id: str
    test_name: str
    max_load_achieved: int
    breaking_point: Optional[int]
    system_degraded_at: Optional[int]
    system_failed_at: Optional[int]
    duration_seconds: float
    recovery_time_seconds: Optional[float]
    status: str
    started_at: datetime
    completed_at: datetime


class StressTester:
    """Stress tester for extreme load validation."""
    
    def __init__(self):
        """Initialize stress tester."""
        self.test_history = []
    
    def run_stress_test(
        self,
        test_name: str,
        target_function: Callable,
        initial_load: int,
        load_increment: int,
        max_load: int,
        duration_per_step: int = 60,
        health_check: Optional[Callable] = None
    ) -> StressTestResult:
        """Run a stress test with incremental load.
        
        Args:
            test_name: Name of the stress test
            target_function: Function to stress test
            initial_load: Initial load level
            load_increment: Load increment per step
            max_load: Maximum load to test
            duration_per_step: Duration per load step
            health_check: Health check function
        
        Returns:
            Stress test result
        """
        test_id = f"stress_test_{int(time.time())}"
        logger.info(f"Starting stress test {test_id}: {test_name}")
        
        started_at = datetime.utcnow()
        current_load = initial_load
        breaking_point = None
        system_degraded_at = None
        system_failed_at = None
        recovery_time = None
        status = 'completed'
        
        while current_load <= max_load:
            logger.info(f"Testing load level: {current_load}")
            
            # Run load at current level
            try:
                self._apply_load(target_function, current_load, duration_per_step)
                
                # Check system health
                if health_check:
                    health_status = health_check()
                    
                    if health_status == 'degraded' and system_degraded_at is None:
                        system_degraded_at = current_load
                        logger.warning(f"System degraded at load: {current_load}")
                    
                    elif health_status == 'failed' and system_failed_at is None:
                        system_failed_at = current_load
                        breaking_point = current_load
                        logger.error(f"System failed at load: {current_load}")
                        break
            
            except Exception as e:
                logger.error(f"System failed at load {current_load}: {e}")
                breaking_point = current_load
                system_failed_at = current_load
                status = 'failed'
                break
            
            current_load += load_increment
        
        # Test recovery
        if breaking_point:
            logger.info("Testing system recovery...")
            recovery_start = time.time()
            
            try:
                # Reduce load to initial level
                self._apply_load(target_function, initial_load, 30)
                
                if health_check:
                    health_status = health_check()
                    if health_status == 'healthy':
                        recovery_time = time.time() - recovery_start
                        logger.info(f"System recovered in {recovery_time:.2f} seconds")
                    else:
                        status = 'not_recovered'
            
            except Exception as e:
                logger.error(f"Recovery failed: {e}")
                status = 'recovery_failed'
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        result = StressTestResult(
            test_id=test_id,
            test_name=test_name,
            max_load_achieved=current_load - load_increment if breaking_point else max_load,
            breaking_point=breaking_point,
            system_degraded_at=system_degraded_at,
            system_failed_at=system_failed_at,
            duration_seconds=duration,
            recovery_time_seconds=recovery_time,
            status=status,
            started_at=started_at,
            completed_at=completed_at
        )
        
        self.test_history.append(result)
        
        logger.info(
            f"Stress test {test_id} completed: max load {result.max_load_achieved}, "
            f"breaking point {breaking_point}, status {status}"
        )
        
        return result
    
    def _apply_load(
        self,
        target_function: Callable,
        load_level: int,
        duration: int
    ):
        """Apply load to the system.
        
        Args:
            target_function: Function to execute
            load_level: Number of concurrent executions
            duration: Duration in seconds
        """
        import threading
        
        def worker():
            while time.time() < end_time:
                try:
                    target_function()
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                time.sleep(0.1)
        
        end_time = time.time() + duration
        threads = []
        
        for _ in range(load_level):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for duration
        time.sleep(duration)
        
        # Stop threads
        for thread in threads:
            thread.join(timeout=1)
    
    def get_test_history(self) -> List[StressTestResult]:
        """Get stress test history.
        
        Returns:
            List of test results
        """
        return self.test_history.copy()
    
    def generate_stress_report(self, test_id: str) -> Dict[str, Any]:
        """Generate stress test report.
        
        Args:
            test_id: Test ID
        
        Returns:
            Stress test report
        """
        result = next((r for r in self.test_history if r.test_id == test_id), None)
        
        if not result:
            return {'error': 'Test ID not found'}
        
        return {
            'test_id': result.test_id,
            'test_name': result.test_name,
            'max_load_achieved': result.max_load_achieved,
            'breaking_point': result.breaking_point,
            'system_degraded_at': result.system_degraded_at,
            'system_failed_at': result.system_failed_at,
            'duration_seconds': result.duration_seconds,
            'recovery_time_seconds': result.recovery_time_seconds,
            'status': result.status,
            'started_at': result.started_at.isoformat(),
            'completed_at': result.completed_at.isoformat(),
            'summary': {
                'system_resilience': 'high' if result.breaking_point is None else 'medium',
                'recovery_capability': 'good' if result.recovery_time and result.recovery_time < 60 else 'poor'
            }
        }
