"""Chaos scenarios for testing system resilience.

This module provides pre-defined chaos scenarios for testing.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import time

from src.streaming.chaos.fault_injector import FaultInjector, FaultType

logger = logging.getLogger(__name__)


class ChaosScenario:
    """Pre-defined chaos scenario."""
    
    def __init__(
        self,
        name: str,
        description: str,
        fault_sequence: List[Dict[str, Any]],
        expected_behavior: str
    ):
        """Initialize chaos scenario.
        
        Args:
            name: Scenario name
            description: Scenario description
            fault_sequence: Sequence of faults to inject
            expected_behavior: Expected system behavior
        """
        self.name = name
        self.description = description
        self.fault_sequence = fault_sequence
        self.expected_behavior = expected_behavior
        self.execution_history = []
    
    def execute(self, fault_injector: FaultInjector) -> Dict[str, Any]:
        """Execute the chaos scenario.
        
        Args:
            fault_injector: Fault injector instance
        
        Returns:
            Execution results
        """
        logger.info(f"Executing chaos scenario: {self.name}")
        
        execution_id = f"exec_{int(time.time())}"
        fault_ids = []
        
        try:
            for fault_config in self.fault_sequence:
                fault_id = fault_injector.inject_fault(**fault_config)
                fault_ids.append(fault_id)
                
                # Wait between faults if specified
                if 'delay_seconds' in fault_config:
                    time.sleep(fault_config['delay_seconds'])
            
            result = {
                'execution_id': execution_id,
                'scenario_name': self.name,
                'status': 'executed',
                'fault_ids': fault_ids,
                'executed_at': datetime.utcnow().isoformat()
            }
            
            self.execution_history.append(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing scenario {self.name}: {e}")
            
            # Clean up any injected faults
            for fault_id in fault_ids:
                fault_injector.remove_fault(fault_id)
            
            return {
                'execution_id': execution_id,
                'scenario_name': self.name,
                'status': 'failed',
                'error': str(e),
                'executed_at': datetime.utcnow().isoformat()
            }


class ChaosScenarioManager:
    """Manage and execute chaos scenarios."""
    
    def __init__(self, fault_injector: FaultInjector):
        """Initialize scenario manager.
        
        Args:
            fault_injector: Fault injector instance
        """
        self.fault_injector = fault_injector
        self.scenarios = {}
        self._load_default_scenarios()
    
    def _load_default_scenarios(self):
        """Load default chaos scenarios."""
        
        # Scenario 1: Redis Failure
        self.scenarios['redis_failure'] = ChaosScenario(
            name='Redis Failure',
            description='Test system resilience when Redis becomes unavailable',
            fault_sequence=[
                {
                    'fault_type': FaultType.NETWORK_FAILURE,
                    'target': 'redis',
                    'severity': 'high',
                    'duration_seconds': 30,
                    'parameters': {'failure_rate': 1.0}
                }
            ],
            expected_behavior='System should fallback gracefully and queue operations'
        )
        
        # Scenario 2: Kafka Latency
        self.scenarios['kafka_latency'] = ChaosScenario(
            name='Kafka Latency',
            description='Test system resilience under high Kafka latency',
            fault_sequence=[
                {
                    'fault_type': FaultType.NETWORK_LATENCY,
                    'target': 'kafka',
                    'severity': 'medium',
                    'duration_seconds': 60,
                    'parameters': {'latency_ms': 5000}
                }
            ],
            expected_behavior='System should handle delayed messages without data loss'
        )
        
        # Scenario 3: Database Connection Exhaustion
        self.scenarios['db_exhaustion'] = ChaosScenario(
            name='Database Connection Exhaustion',
            description='Test system resilience when database connections are exhausted',
            fault_sequence=[
                {
                    'fault_type': FaultType.RESOURCE_EXHAUSTION,
                    'target': 'database',
                    'severity': 'high',
                    'duration_seconds': 45,
                    'parameters': {'resource_type': 'connections'}
                }
            ],
            expected_behavior='System should queue requests and retry with backoff'
        )
        
        # Scenario 4: Multi-Component Failure
        self.scenarios['multi_failure'] = ChaosScenario(
            name='Multi-Component Failure',
            description='Test system resilience when multiple components fail simultaneously',
            fault_sequence=[
                {
                    'fault_type': FaultType.NETWORK_FAILURE,
                    'target': 'redis',
                    'severity': 'high',
                    'duration_seconds': 30,
                    'parameters': {'failure_rate': 0.8},
                    'delay_seconds': 5
                },
                {
                    'fault_type': FaultType.NETWORK_LATENCY,
                    'target': 'kafka',
                    'severity': 'medium',
                    'duration_seconds': 30,
                    'parameters': {'latency_ms': 2000}
                }
            ],
            expected_behavior='System should degrade gracefully and maintain core functionality'
        )
        
        # Scenario 5: High Load Spike
        self.scenarios['load_spike'] = ChaosScenario(
            name='Load Spike',
            description='Test system resilience under sudden load spike',
            fault_sequence=[
                {
                    'fault_type': FaultType.HIGH_LOAD,
                    'target': 'api',
                    'severity': 'medium',
                    'duration_seconds': 60,
                    'parameters': {'load_multiplier': 20.0}
                }
            ],
            expected_behavior='System should handle load with auto-scaling or backpressure'
        )
    
    def add_scenario(self, scenario: ChaosScenario):
        """Add a custom scenario.
        
        Args:
            scenario: Chaos scenario
        """
        self.scenarios[scenario.name] = scenario
    
    def execute_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Execute a scenario by name.
        
        Args:
            scenario_name: Name of scenario to execute
        
        Returns:
            Execution results
        """
        if scenario_name not in self.scenarios:
            return {
                'error': f'Scenario {scenario_name} not found',
                'available_scenarios': list(self.scenarios.keys())
            }
        
        scenario = self.scenarios[scenario_name]
        return scenario.execute(self.fault_injector)
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all available scenarios.
        
        Returns:
            List of scenario information
        """
        return [
            {
                'name': name,
                'description': scenario.description,
                'expected_behavior': scenario.expected_behavior
            }
            for name, scenario in self.scenarios.items()
        ]
    
    def get_scenario(self, scenario_name: str) -> Optional[ChaosScenario]:
        """Get a scenario by name.
        
        Args:
            scenario_name: Scenario name
        
        Returns:
            Chaos scenario or None if not found
        """
        return self.scenarios.get(scenario_name)
