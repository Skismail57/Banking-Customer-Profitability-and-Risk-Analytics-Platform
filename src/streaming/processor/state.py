"""State management for stream processing.

This module provides state management capabilities including key-value state,
state checkpointing, and state restoration for fault tolerance.
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json
import pickle

logger = logging.getLogger(__name__)


class StateBackend(str, Enum):
    """State backend types."""
    MEMORY = "memory"
    REDIS = "redis"
    POSTGRESQL = "postgresql"


@dataclass
class StateSnapshot:
    """State snapshot for checkpointing."""
    snapshot_id: str
    timestamp: datetime
    state_data: Dict[str, Any]
    watermark: Optional[datetime] = None


class StateManager:
    """Manage state for stream processing."""
    
    def __init__(
        self,
        backend: StateBackend = StateBackend.MEMORY,
        checkpoint_interval_ms: int = 60000,  # 1 minute default
        max_snapshots: int = 10
    ):
        """Initialize state manager.
        
        Args:
            backend: State backend type
            checkpoint_interval_ms: Checkpoint interval in milliseconds
            max_snapshots: Maximum number of snapshots to retain
        """
        self.backend = backend
        self.checkpoint_interval_ms = checkpoint_interval_ms
        self.max_snapshots = max_snapshots
        
        # In-memory state
        self.state: Dict[str, Any] = {}
        
        # Keyed state
        self.keyed_state: Dict[str, Dict[str, Any]] = {}
        
        # State snapshots
        self.snapshots: List[StateSnapshot] = []
        
        # Last checkpoint time
        self.last_checkpoint_time: Optional[datetime] = None
        
        # Metrics
        self.metrics = {
            'state_updates': 0,
            'checkpoints_created': 0,
            'checkpoints_restored': 0,
            'snapshot_count': 0,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state.
        
        Args:
            key: State key
            default: Default value if key not found
        
        Returns:
            State value or default
        """
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in state.
        
        Args:
            key: State key
            value: Value to set
        """
        self.state[key] = value
        self.metrics['state_updates'] += 1
    
    def delete(self, key: str) -> None:
        """Delete key from state.
        
        Args:
            key: State key
        """
        if key in self.state:
            del self.state[key]
    
    def get_keyed(self, key_group: str, key: str, default: Any = None) -> Any:
        """Get value from keyed state.
        
        Args:
            key_group: Key group (e.g., customer, account)
            key: Key within group
            default: Default value if key not found
        
        Returns:
            State value or default
        """
        if key_group not in self.keyed_state:
            return default
        return self.keyed_state[key_group].get(key, default)
    
    def set_keyed(self, key_group: str, key: str, value: Any) -> None:
        """Set value in keyed state.
        
        Args:
            key_group: Key group (e.g., customer, account)
            key: Key within group
            value: Value to set
        """
        if key_group not in self.keyed_state:
            self.keyed_state[key_group] = {}
        
        self.keyed_state[key_group][key] = value
        self.metrics['state_updates'] += 1
    
    def delete_keyed(self, key_group: str, key: str) -> None:
        """Delete key from keyed state.
        
        Args:
            key_group: Key group
            key: Key within group
        """
        if key_group in self.keyed_state and key in self.keyed_state[key_group]:
            del self.keyed_state[key_group][key]
    
    def get_all_keyed(self, key_group: str) -> Dict[str, Any]:
        """Get all values for a key group.
        
        Args:
            key_group: Key group
        
        Returns:
            Dictionary of all keys and values in group
        """
        return self.keyed_state.get(key_group, {}).copy()
    
    def clear_keyed(self, key_group: str) -> None:
        """Clear all values for a key group.
        
        Args:
            key_group: Key group
        """
        if key_group in self.keyed_state:
            del self.keyed_state[key_group]
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update state with multiple key-value pairs.
        
        Args:
            updates: Dictionary of updates
        """
        self.state.update(updates)
        self.metrics['state_updates'] += len(updates)
    
    def increment(self, key: str, delta: int = 1) -> int:
        """Increment a counter in state.
        
        Args:
            key: State key
            delta: Increment amount
        
        Returns:
            New value
        """
        current = self.get(key, 0)
        new_value = current + delta
        self.set(key, new_value)
        return new_value
    
    def append(self, key: str, value: Any) -> None:
        """Append value to a list in state.
        
        Args:
            key: State key
            value: Value to append
        """
        current = self.get(key, [])
        if not isinstance(current, list):
            current = []
        current.append(value)
        self.set(key, current)
    
    def checkpoint(self, watermark: Optional[datetime] = None) -> StateSnapshot:
        """Create a state snapshot.
        
        Args:
            watermark: Current watermark to include in snapshot
        
        Returns:
            StateSnapshot object
        """
        snapshot_id = f"snapshot_{datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}"
        
        # Create snapshot
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            state_data={
                'state': self.state.copy(),
                'keyed_state': {k: v.copy() for k, v in self.keyed_state.items()},
            },
            watermark=watermark
        )
        
        # Add to snapshots
        self.snapshots.append(snapshot)
        
        # Remove old snapshots if exceeding max
        while len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
        
        self.last_checkpoint_time = datetime.now(timezone.utc).replace(tzinfo=None)
        self.metrics['checkpoints_created'] += 1
        self.metrics['snapshot_count'] = len(self.snapshots)
        
        logger.info(f"Created checkpoint {snapshot_id}")
        
        return snapshot
    
    def restore(self, snapshot_id: str) -> bool:
        """Restore state from snapshot.
        
        Args:
            snapshot_id: Snapshot ID to restore
        
        Returns:
            True if successful, False otherwise
        """
        # Find snapshot
        snapshot = None
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                snapshot = s
                break
        
        if snapshot is None:
            logger.error(f"Snapshot {snapshot_id} not found")
            return False
        
        # Restore state
        self.state = snapshot.state_data.get('state', {}).copy()
        self.keyed_state = {
            k: v.copy() for k, v in snapshot.state_data.get('keyed_state', {}).items()
        }
        
        self.metrics['checkpoints_restored'] += 1
        logger.info(f"Restored from snapshot {snapshot_id}")
        
        return True
    
    def restore_latest(self) -> bool:
        """Restore state from latest snapshot.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.snapshots:
            logger.warning("No snapshots available for restore")
            return False
        
        latest_snapshot = self.snapshots[-1]
        return self.restore(latest_snapshot.snapshot_id)
    
    def get_snapshots(self) -> List[StateSnapshot]:
        """Get all snapshots.
        
        Returns:
            List of snapshots
        """
        return self.snapshots.copy()
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot.
        
        Args:
            snapshot_id: Snapshot ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        for i, snapshot in enumerate(self.snapshots):
            if snapshot.snapshot_id == snapshot_id:
                self.snapshots.pop(i)
                self.metrics['snapshot_count'] = len(self.snapshots)
                logger.info(f"Deleted snapshot {snapshot_id}")
                return True
        
        logger.warning(f"Snapshot {snapshot_id} not found")
        return False
    
    def should_checkpoint(self) -> bool:
        """Check if it's time to create a checkpoint.
        
        Returns:
            True if checkpoint should be created
        """
        if self.last_checkpoint_time is None:
            return True
        
        elapsed = datetime.now(timezone.utc).replace(tzinfo=None) - self.last_checkpoint_time
        elapsed_ms = int(elapsed.total_seconds() * 1000)
        
        return elapsed_ms >= self.checkpoint_interval_ms
    
    def export_state(self) -> Dict[str, Any]:
        """Export state to dictionary.
        
        Returns:
            Dictionary representation of state
        """
        return {
            'state': self.state.copy(),
            'keyed_state': {k: v.copy() for k, v in self.keyed_state.items()},
            'snapshots': [
                {
                    'snapshot_id': s.snapshot_id,
                    'timestamp': s.timestamp.isoformat(),
                    'watermark': s.watermark.isoformat() if s.watermark else None,
                }
                for s in self.snapshots
            ],
        }
    
    def import_state(self, state_data: Dict[str, Any]) -> None:
        """Import state from dictionary.
        
        Args:
            state_data: Dictionary representation of state
        """
        self.state = state_data.get('state', {}).copy()
        self.keyed_state = {
            k: v.copy() for k, v in state_data.get('keyed_state', {}).items()
        }
        logger.info("Imported state from dictionary")
    
    def clear(self) -> None:
        """Clear all state."""
        self.state.clear()
        self.keyed_state.clear()
        self.snapshots.clear()
        self.last_checkpoint_time = None
        logger.debug("Cleared all state")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get state manager metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def get_status(self) -> Dict[str, Any]:
        """Get state manager status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'backend': self.backend.value,
            'checkpoint_interval_ms': self.checkpoint_interval_ms,
            'max_snapshots': self.max_snapshots,
            'state_size': len(self.state),
            'keyed_state_groups': len(self.keyed_state),
            'snapshot_count': len(self.snapshots),
            'last_checkpoint': self.last_checkpoint_time.isoformat() if self.last_checkpoint_time else None,
            'metrics': self.get_metrics(),
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'state_updates': 0,
            'checkpoints_created': 0,
            'checkpoints_restored': 0,
            'snapshot_count': len(self.snapshots),
        }