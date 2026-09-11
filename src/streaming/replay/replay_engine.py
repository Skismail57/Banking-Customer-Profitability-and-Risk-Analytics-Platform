"""Historical event replay engine.

This module provides historical event replay capabilities for the banking analytics
platform, allowing reprocessing of historical events for testing and validation.

Assumptions:
- Historical events are stored in PostgreSQL (fact_realtime_events)
- Replay can be accelerated with speed multiplier
- Replay results are tracked in fact_replay_runs

Limitations:
- Replay requires historical data availability
- No support for parallel replay of multiple time ranges
- Replay may be slow for large date ranges

Fairness Considerations:
- Replay should include demographic context for fairness testing
- Monitor replay results across customer segments
- Ensure replay doesn't introduce bias in testing
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
import logging
import uuid
import time
from dataclasses import dataclass

from src.streaming.config import StreamingConfig
from src.streaming.orchestrator.pipeline_orchestrator import StreamingOrchestrator

logger = logging.getLogger(__name__)


class ReplayEngine:
    """Historical event replay engine.
    
    This engine enables reprocessing of historical events for:
    - Testing new model versions
    - Validating pipeline changes
    - Debugging issues
    - Feature parity validation
    
    Key Features:
    - Replay events from historical time range
    - Accelerated replay with speed multiplier
    - Track replay results
    - Compare replay results with original
    - Support for event selection criteria
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        orchestrator: StreamingOrchestrator,
        db_session
    ):
        """Initialize replay engine.
        
        Args:
            config: Streaming configuration
            orchestrator: Streaming orchestrator
            db_session: Database session for querying historical events
        """
        self.config = config
        self.orchestrator = orchestrator
        self.db_session = db_session
    
    def create_replay_run(
        self,
        replay_name: str,
        source_range_start: datetime,
        source_range_end: datetime,
        speed_multiplier: float = 1.0,
        event_selection_criteria: Optional[Dict[str, Any]] = None,
        model_version: Optional[str] = None,
        feature_version: Optional[str] = None
    ) -> str:
        """Create a replay run.
        
        Args:
            replay_name: Name for the replay run
            source_range_start: Start of historical time range
            source_range_end: End of historical time range
            speed_multiplier: Speed multiplier for accelerated replay
            event_selection_criteria: Criteria for event selection
            model_version: Model version to use (None = current production)
            feature_version: Feature version to use (None = current)
        
        Returns:
            Replay ID
        """
        replay_id = str(uuid.uuid4())
        
        logger.info(
            f"Creating replay run {replay_id}: {replay_name} "
            f"from {source_range_start} to {source_range_end} "
            f"at {speed_multiplier}x speed"
        )
        
        # Insert replay run record
        insert_query = """
            INSERT INTO fact_replay_runs (
                replay_id, replay_name, source_range_start, source_range_end,
                event_selection_criteria, speed_multiplier, target_environment,
                model_version, feature_version, status, started_at
            ) VALUES (
                :replay_id, :replay_name, :source_range_start, :source_range_end,
                :event_selection_criteria::jsonb, :speed_multiplier, :target_environment,
                :model_version, :feature_version, :status, :started_at
            )
        """
        
        self.db_session.execute(insert_query, {
            'replay_id': replay_id,
            'replay_name': replay_name,
            'source_range_start': source_range_start,
            'source_range_end': source_range_end,
            'event_selection_criteria': event_selection_criteria,
            'speed_multiplier': speed_multiplier,
            'target_environment': 'development',
            'model_version': model_version,
            'feature_version': feature_version,
            'status': 'pending',
            'started_at': datetime.now(timezone.utc).replace(tzinfo=None)
        })
        
        self.db_session.commit()
        
        return replay_id
    
    def execute_replay(
        self,
        replay_id: str
    ) -> Dict[str, Any]:
        """Execute a replay run.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            Replay results
        """
        logger.info(f"Executing replay {replay_id}")
        
        # Get replay run details
        replay_query = """
            SELECT replay_id, replay_name, source_range_start, source_range_end,
                   event_selection_criteria, speed_multiplier, model_version,
                   feature_version
            FROM fact_replay_runs
            WHERE replay_id = :replay_id
        """
        
        replay = self.db_session.execute(replay_query, {'replay_id': replay_id}).fetchone()
        
        if not replay:
            raise ValueError(f"Replay {replay_id} not found")
        
        # Update status to running
        self.db_session.execute(
            "UPDATE fact_replay_runs SET status = 'running' WHERE replay_id = :replay_id",
            {'replay_id': replay_id}
        )
        self.db_session.commit()
        
        # Query historical events
        events = self._query_historical_events(
            replay.source_range_start,
            replay.source_range_end,
            replay.event_selection_criteria
        )
        
        logger.info(f"Found {len(events)} events to replay")
        
        # Process events with speed multiplier
        results = []
        events_processed = 0
        
        for event in events:
            # Calculate delay based on speed multiplier
            event_time = event['event_timestamp']
            next_event_time = event.get('next_event_timestamp')
            
            if next_event_time and replay.speed_multiplier > 0:
                original_delay = (next_event_time - event_time).total_seconds()
                replay_delay = original_delay / replay.speed_multiplier
                
                if replay_delay > 0:
                    time.sleep(replay_delay)
            
            # Process event
            try:
                result = self.orchestrator.process_event(event)
                results.append(result)
                events_processed += 1
            except Exception as e:
                logger.error(f"Error processing event during replay: {e}")
                results.append({
                    'event_id': event.get('event_id'),
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r.get('success', True))
        failed = len(results) - successful
        
        summary = {
            'total_events': len(events),
            'events_processed': events_processed,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(results) if results else 0.0
        }
        
        # Update replay run with results
        update_query = """
            UPDATE fact_replay_runs
            SET status = 'completed',
                completed_at = :completed_at,
                events_processed = :events_processed,
                results_summary = :results_summary::jsonb
            WHERE replay_id = :replay_id
        """
        
        self.db_session.execute(update_query, {
            'replay_id': replay_id,
            'completed_at': datetime.now(timezone.utc).replace(tzinfo=None),
            'events_processed': events_processed,
            'results_summary': summary
        })
        self.db_session.commit()
        
        logger.info(
            f"Replay {replay_id} completed: {summary['successful']}/{summary['total_events']} successful"
        )
        
        return {
            'replay_id': replay_id,
            'summary': summary,
            'results': results
        }
    
    def _query_historical_events(
        self,
        start_time: datetime,
        end_time: datetime,
        selection_criteria: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Query historical events from database.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            selection_criteria: Event selection criteria
        
        Returns:
            List of events
        """
        query = """
            SELECT 
                event_id,
                event_type,
                customer_key,
                event_timestamp,
                event_data
            FROM fact_realtime_events
            WHERE event_timestamp BETWEEN :start_time AND :end_time
            AND status = 'completed'
        """
        
        params = {
            'start_time': start_time,
            'end_time': end_time
        }
        
        # Apply selection criteria if provided
        if selection_criteria:
            if 'customer_key' in selection_criteria:
                query += " AND customer_key = :customer_key"
                params['customer_key'] = selection_criteria['customer_key']
            
            if 'event_type' in selection_criteria:
                query += " AND event_type = :event_type"
                params['event_type'] = selection_criteria['event_type']
        
        query += " ORDER BY event_timestamp ASC"
        
        result = self.db_session.execute(query, params)
        
        events = []
        for row in result:
            event = {
                'event_id': row.event_id,
                'event_type': row.event_type,
                'customer_key': row.customer_key,
                'event_timestamp': row.event_timestamp,
                **(row.event_data or {})
            }
            events.append(event)
        
        return events
    
    def get_replay_results(self, replay_id: str) -> Optional[Dict[str, Any]]:
        """Get results of a replay run.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            Replay results or None if not found
        """
        query = """
            SELECT 
                replay_id, replay_name, source_range_start, source_range_end,
                speed_multiplier, model_version, feature_version,
                started_at, completed_at, status, events_processed,
                results_summary
            FROM fact_replay_runs
            WHERE replay_id = :replay_id
        """
        
        result = self.db_session.execute(query, {'replay_id': replay_id}).fetchone()
        
        if result:
            return {
                'replay_id': result.replay_id,
                'replay_name': result.replay_name,
                'source_range_start': result.source_range_start.isoformat(),
                'source_range_end': result.source_range_end.isoformat(),
                'speed_multiplier': float(result.speed_multiplier),
                'model_version': result.model_version,
                'feature_version': result.feature_version,
                'started_at': result.started_at.isoformat(),
                'completed_at': result.completed_at.isoformat() if result.completed_at else None,
                'status': result.status,
                'events_processed': result.events_processed,
                'results_summary': result.results_summary
            }
        
        return None
    
    def list_replay_runs(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List recent replay runs.
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of replay runs
        """
        query = """
            SELECT 
                replay_id, replay_name, source_range_start, source_range_end,
                speed_multiplier, status, started_at, completed_at,
                events_processed
            FROM fact_replay_runs
            ORDER BY started_at DESC
            LIMIT :limit
        """
        
        result = self.db_session.execute(query, {'limit': limit})
        
        runs = []
        for row in result:
            runs.append({
                'replay_id': row.replay_id,
                'replay_name': row.replay_name,
                'source_range_start': row.source_range_start.isoformat(),
                'source_range_end': row.source_range_end.isoformat(),
                'speed_multiplier': float(row.speed_multiplier),
                'status': row.status,
                'started_at': row.started_at.isoformat(),
                'completed_at': row.completed_at.isoformat() if row.completed_at else None,
                'events_processed': row.events_processed
            })
        
        return runs
    
    def cancel_replay(self, replay_id: str) -> bool:
        """Cancel a running replay.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Cancelling replay {replay_id}")
        
        result = self.db_session.execute(
            "UPDATE fact_replay_runs SET status = 'cancelled' WHERE replay_id = :replay_id AND status = 'running'",
            {'replay_id': replay_id}
        )
        
        self.db_session.commit()
        
        return result.rowcount > 0


@dataclass
class ReplayState:
    """State snapshot for replay."""
    state_id: str
    replay_id: str
    timestamp: datetime
    state_data: Dict[str, Any]


class ReplayStateManager:
    """Manage state snapshots for replay."""
    
    def __init__(self, feature_store):
        """Initialize state manager.
        
        Args:
            feature_store: Redis feature store
        """
        self.feature_store = feature_store
        self.state_snapshots = defaultdict(dict)
    
    def capture_state(
        self,
        replay_id: str,
        timestamp: datetime,
        state_data: Dict[str, Any]
    ) -> str:
        """Capture state snapshot.
        
        Args:
            replay_id: Replay ID
            timestamp: State timestamp
            state_data: State data
        
        Returns:
            State ID
        """
        state_id = str(uuid.uuid4())
        
        state = ReplayState(
            state_id=state_id,
            replay_id=replay_id,
            timestamp=timestamp,
            state_data=state_data
        )
        
        # Store in memory
        self.state_snapshots[replay_id][timestamp.isoformat()] = state
        
        # Store in Redis
        state_key = f"replay_state:{replay_id}:{state_id}"
        import json
        state_json = json.dumps({
            'state_id': state_id,
            'replay_id': replay_id,
            'timestamp': timestamp.isoformat(),
            'state_data': state_data
        })
        
        ttl = 7 * 24 * 60 * 60  # 7 days
        self.feature_store.redis_client.setex(state_key, ttl, state_json)
        
        return state_id
    
    def restore_state(
        self,
        replay_id: str,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Restore state snapshot.
        
        Args:
            replay_id: Replay ID
            timestamp: Target timestamp
        
        Returns:
            State data or None if not found
        """
        # Find closest state snapshot
        snapshots = self.state_snapshots.get(replay_id, {})
        
        if not snapshots:
            return None
        
        # Find closest timestamp
        target_ts = timestamp.isoformat()
        closest_ts = min(
            snapshots.keys(),
            key=lambda ts: abs(datetime.fromisoformat(ts) - timestamp)
        )
        
        state = snapshots[closest_ts]
        return state.state_data
    
    def list_states(self, replay_id: str) -> List[Dict[str, Any]]:
        """List state snapshots for replay.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            List of state snapshots
        """
        snapshots = self.state_snapshots.get(replay_id, {})
        
        return [
            {
                'state_id': state.state_id,
                'timestamp': state.timestamp.isoformat(),
                'replay_id': state.replay_id
            }
            for state in snapshots.values()
        ]


class ReplayValidator:
    """Validate replay results against original results."""
    
    def __init__(self):
        """Initialize replay validator."""
        self.validation_history = []
    
    def validate_replay(
        self,
        replay_id: str,
        replay_results: List[Dict[str, Any]],
        original_results: List[Dict[str, Any]],
        tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """Validate replay results against original.
        
        Args:
            replay_id: Replay ID
            replay_results: Results from replay
            original_results: Original results
            tolerance: Tolerance for comparison
        
        Returns:
            Validation report
        """
        validation_id = str(uuid.uuid4())
        
        # Create lookup for original results
        original_lookup = {
            r.get('event_id'): r
            for r in original_results
        }
        
        # Compare results
        comparisons = []
        matched = 0
        mismatched = 0
        missing = 0
        
        for replay_result in replay_results:
            event_id = replay_result.get('event_id')
            original_result = original_lookup.get(event_id)
            
            if original_result:
                comparison = self._compare_results(
                    replay_result,
                    original_result,
                    tolerance
                )
                comparisons.append(comparison)
                
                if comparison['matched']:
                    matched += 1
                else:
                    mismatched += 1
            else:
                missing += 1
                comparisons.append({
                    'event_id': event_id,
                    'matched': False,
                    'reason': 'missing_in_original'
                })
        
        # Calculate validation status
        total = len(replay_results)
        match_rate = matched / total if total > 0 else 0.0
        
        if match_rate >= 0.95:
            status = 'pass'
        elif match_rate >= 0.90:
            status = 'warning'
        else:
            status = 'fail'
        
        validation_report = {
            'validation_id': validation_id,
            'replay_id': replay_id,
            'status': status,
            'summary': {
                'total_compared': total,
                'matched': matched,
                'mismatched': mismatched,
                'missing': missing,
                'match_rate': match_rate
            },
            'comparisons': comparisons,
            'validated_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
        
        self.validation_history.append(validation_report)
        
        return validation_report
    
    def _compare_results(
        self,
        replay_result: Dict[str, Any],
        original_result: Dict[str, Any],
        tolerance: float
    ) -> Dict[str, Any]:
        """Compare single result.
        
        Args:
            replay_result: Replay result
            original_result: Original result
            tolerance: Comparison tolerance
        
        Returns:
            Comparison result
        """
        # Compare key fields
        fields_to_compare = ['risk_score', 'anomaly_score', 'prediction']
        
        for field in fields_to_compare:
            replay_value = replay_result.get(field)
            original_value = original_result.get(field)
            
            if replay_value is not None and original_value is not None:
                if isinstance(replay_value, (int, float)) and isinstance(original_value, (int, float)):
                    diff = abs(replay_value - original_value)
                    if diff > tolerance:
                        return {
                            'event_id': replay_result.get('event_id'),
                            'matched': False,
                            'reason': f'{field} mismatch: {diff} > {tolerance}',
                            'field': field,
                            'replay_value': replay_value,
                            'original_value': original_value
                        }
        
        return {
            'event_id': replay_result.get('event_id'),
            'matched': True,
            'reason': 'all_fields_matched'
        }
    
    def get_validation_history(self, replay_id: str) -> List[Dict[str, Any]]:
        """Get validation history for replay.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            List of validation reports
        """
        return [
            v for v in self.validation_history
            if v.get('replay_id') == replay_id
        ]
