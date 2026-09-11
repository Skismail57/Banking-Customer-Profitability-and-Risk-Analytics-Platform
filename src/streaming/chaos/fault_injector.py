"""Fault injection for chaos testing.

This module provides fault injection capabilities for testing system resilience.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import logging
import random
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FaultType(Enum):
    """Types of faults to inject."""
    NETWORK_LATENCY = "network_latency"
    NETWORK_FAILURE = "network_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    SERVICE_CRASH = "service_crash"
    HIGH_LOAD = "high_load"


@dataclass
class Fault:
    """Fault configuration."""
    fault_id: str
    fault_type: str
    target: str
    severity: str
    duration_seconds: int
    parameters: Dict[str, Any]
    injected_at: datetime
    active: bool = True


class FaultInjector:
    """Inject faults into the system for chaos testing."""
    
    def __init__(self):
        """Initialize fault injector."""
        self.active_faults = {}
        self.fault_history = []
        self.original_functions = {}
    
    def inject_fault(
        self,
        fault_type: FaultType,
        target: str,
        severity: str = "medium",
        duration_seconds: int = 60,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Inject a fault into the system.
        
        Args:
            fault_type: Type of fault to inject
            target: Target component
            severity: Fault severity (low, medium, high)
            duration_seconds: Duration of fault
            parameters: Additional fault parameters
        
        Returns:
            Fault ID
        """
        fault_id = f"fault_{int(time.time())}_{random.randint(1000, 9999)}"
        
        fault = Fault(
            fault_id=fault_id,
            fault_type=fault_type.value,
            target=target,
            severity=severity,
            duration_seconds=duration_seconds,
            parameters=parameters or {},
            injected_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        self.active_faults[fault_id] = fault
        self.fault_history.append(fault)
        
        logger.warning(f"Injected fault {fault_id}: {fault_type.value} on {target}")
        
        return fault_id
    
    def remove_fault(self, fault_id: str) -> bool:
        """Remove an active fault.
        
        Args:
            fault_id: Fault ID to remove
        
        Returns:
            True if removed, False if not found
        """
        if fault_id in self.active_faults:
            fault = self.active_faults[fault_id]
            fault.active = False
            del self.active_faults[fault_id]
            
            logger.info(f"Removed fault {fault_id}")
            return True
        
        return False
    
    def inject_network_latency(
        self,
        target: str,
        latency_ms: int = 1000,
        duration_seconds: int = 60
    ) -> str:
        """Inject network latency fault.
        
        Args:
            target: Target component
            latency_ms: Latency in milliseconds
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.NETWORK_LATENCY,
            target=target,
            severity="medium",
            duration_seconds=duration_seconds,
            parameters={'latency_ms': latency_ms}
        )
    
    def inject_network_failure(
        self,
        target: str,
        failure_rate: float = 0.5,
        duration_seconds: int = 60
    ) -> str:
        """Inject network failure fault.
        
        Args:
            target: Target component
            failure_rate: Rate of failures (0.0 to 1.0)
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.NETWORK_FAILURE,
            target=target,
            severity="high",
            duration_seconds=duration_seconds,
            parameters={'failure_rate': failure_rate}
        )
    
    def inject_resource_exhaustion(
        self,
        target: str,
        resource_type: str = "memory",
        duration_seconds: int = 60
    ) -> str:
        """Inject resource exhaustion fault.
        
        Args:
            target: Target component
            resource_type: Type of resource (memory, cpu, disk)
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.RESOURCE_EXHAUSTION,
            target=target,
            severity="high",
            duration_seconds=duration_seconds,
            parameters={'resource_type': resource_type}
        )
    
    def inject_data_corruption(
        self,
        target: str,
        corruption_rate: float = 0.1,
        duration_seconds: int = 60
    ) -> str:
        """Inject data corruption fault.
        
        Args:
            target: Target component
            corruption_rate: Rate of corruption (0.0 to 1.0)
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.DATA_CORRUPTION,
            target=target,
            severity="critical",
            duration_seconds=duration_seconds,
            parameters={'corruption_rate': corruption_rate}
        )
    
    def inject_service_crash(
        self,
        target: str,
        crash_type: str = "graceful",
        duration_seconds: int = 60
    ) -> str:
        """Inject service crash fault.
        
        Args:
            target: Target component
            crash_type: Type of crash (graceful, hard)
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.SERVICE_CRASH,
            target=target,
            severity="critical",
            duration_seconds=duration_seconds,
            parameters={'crash_type': crash_type}
        )
    
    def inject_high_load(
        self,
        target: str,
        load_multiplier: float = 10.0,
        duration_seconds: int = 60
    ) -> str:
        """Inject high load fault.
        
        Args:
            target: Target component
            load_multiplier: Load multiplier
            duration_seconds: Duration of fault
        
        Returns:
            Fault ID
        """
        return self.inject_fault(
            fault_type=FaultType.HIGH_LOAD,
            target=target,
            severity="medium",
            duration_seconds=duration_seconds,
            parameters={'load_multiplier': load_multiplier}
        )
    
    def get_active_faults(self) -> List[Fault]:
        """Get all active faults.
        
        Returns:
            List of active faults
        """
        return list(self.active_faults.values())
    
    def get_fault_history(self) -> List[Fault]:
        """Get fault history.
        
        Returns:
            List of all faults
        """
        return self.fault_history.copy()
    
    def clear_all_faults(self):
        """Clear all active faults."""
        for fault_id in list(self.active_faults.keys()):
            self.remove_fault(fault_id)
        
        logger.info("Cleared all active faults")
