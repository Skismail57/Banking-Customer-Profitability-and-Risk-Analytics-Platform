"""Streaming pipeline orchestrator.

This module provides the main pipeline coordinator that wires together all
streaming components into a unified processing pipeline.

Assumptions:
- Events are consumed from Kafka/Redpanda
- Components are initialized with shared configuration
- Processing follows: ingest → feature compute → anomaly/risk/warning → alert → audit

Limitations:
- No support for parallel processing of events
- No support for event replay in orchestrator (separate component)
- Error handling may need refinement for production

Fairness Considerations:
- Pipeline should log fairness metrics
- Monitor component outputs across demographic segments
- Ensure audit trail captures fairness-relevant context
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import uuid

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore
from src.streaming.features.adapter import FeatureStoreAdapter
from src.streaming.anomaly.anomaly_adapter import StreamingAnomalyAdapter
from src.streaming.risk.risk_engine import RealTimeRiskEngine
from src.streaming.early_warning.warning_adapter import StreamingWarningAdapter
from src.streaming.alerts.alert_engine import AlertEngine
from src.streaming.audit.decision_auditor import DecisionAuditor
from src.streaming.model_registry.online_model import OnlineModel
from src.streaming.model_registry.registry import ModelRegistry
from src.streaming.kafka.consumer import KafkaConsumer
from src.streaming.schemas.event_schemas import create_event

logger = logging.getLogger(__name__)


class StreamingOrchestrator:
    """Main streaming pipeline orchestrator.
    
    This orchestrator coordinates all streaming components into a unified
    processing pipeline that:
    1. Consumes events from Kafka
    2. Computes features
    3. Detects anomalies
    4. Computes risk scores
    5. Generates early warnings
    6. Generates alerts
    7. Records audit trail
    
    Key Features:
    - Wires together all streaming adapters
    - Manages component lifecycle
    - Handles event processing workflow
    - Provides pipeline metrics
    - Supports graceful shutdown
    """
    
    def __init__(self, config: StreamingConfig):
        """Initialize streaming orchestrator.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        self.is_running = False
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all streaming components."""
        logger.info("Initializing streaming pipeline components")
        
        # Feature store
        self.feature_store = FeatureStore(self.config)
        
        # Feature store adapter (bridges with batch feature engineering)
        self.feature_adapter = FeatureStoreAdapter(self.feature_store)
        
        # Anomaly detector
        self.anomaly_adapter = StreamingAnomalyAdapter(
            self.config, self.feature_store
        )
        
        # Risk engine
        self.risk_engine = RealTimeRiskEngine(
            self.config, self.feature_store
        )
        
        # Early warning adapter
        self.warning_adapter = StreamingWarningAdapter(
            self.config, self.feature_store
        )
        
        # Alert engine
        self.alert_engine = AlertEngine(self.config, self.feature_store)
        
        # Decision auditor
        self.decision_auditor = DecisionAuditor(self.config, self.feature_store)
        
        # Model registry
        self.model_registry = ModelRegistry(self.config, self.feature_store)
        
        # Online model inference
        self.online_model = OnlineModel(
            self.config, self.feature_store, self.model_registry
        )
        
        # Kafka consumer
        self.kafka_consumer = KafkaConsumer(self.config)
        
        logger.info("All streaming components initialized")
    
    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single event through the pipeline.
        
        Args:
            event_data: Raw event data from Kafka
        
        Returns:
            Processing result with all outputs
        """
        event_id = event_data.get('event_id', str(uuid.uuid4()))
        customer_key = event_data.get('customer_key')
        event_type = event_data.get('event_type')
        # Use event_timestamp if available, fall back to timestamp for backward compatibility
        timestamp_str = event_data.get('event_timestamp') or event_data.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(timezone.utc).replace(tzinfo=None)
        
        logger.debug(f"Processing event {event_id} for customer {customer_key}")
        
        # Idempotency check - skip if already processed
        idempotency_key = f"idempotency:{event_id}:processed"
        if self.feature_store.redis_client.exists(idempotency_key):
            logger.info(f"Event {event_id} already processed, skipping")
            return {
                'event_id': event_id,
                'customer_key': customer_key,
                'event_type': event_type,
                'timestamp': timestamp.isoformat(),
                'processing_start': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                'processing_end': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                'processing_latency_ms': 0,
                'success': True,
                'skipped': True,
                'reason': 'already_processed',
                'anomaly_result': None,
                'risk_result': None,
                'warning_result': None,
                'alert_result': None,
                'decision_records': [],
                'errors': []
            }
        
        start_time = datetime.now(timezone.utc).replace(tzinfo=None)
        
        result = {
            'event_id': event_id,
            'customer_key': customer_key,
            'event_type': event_type,
            'timestamp': timestamp.isoformat(),
            'processing_start': start_time.isoformat(),
            'anomaly_result': None,
            'risk_result': None,
            'warning_result': None,
            'alert_result': None,
            'decision_records': [],
            'processing_end': None,
            'processing_latency_ms': None,
            'success': True,
            'errors': []
        }
        
        try:
            # Step 1: Compute and store features
            self._compute_features(event_data, customer_key, timestamp)
            
            # Step 2: Detect anomalies
            if event_type == 'transaction':
                result['anomaly_result'] = self._detect_anomalies(
                    event_id, customer_key, event_data, timestamp
                )
            
            # Step 3: Compute risk score
            risk_result = self.risk_engine.compute_risk_score(
                event_id, customer_key, timestamp
            )
            result['risk_result'] = risk_result
            
            if risk_result:
                # Update customer risk level in database
                self.risk_engine.update_customer_risk_level(
                    customer_key,
                    risk_result.risk_level,
                    risk_result.risk_score,
                    timestamp
                )
                
                # Record decision
                decision_record = self.decision_auditor.record_risk_decision(
                    risk_result.__dict__, event_id
                )
                result['decision_records'].append(decision_record.__dict__)
            
            # Step 4: Detect early warnings
            warning_result = self.warning_adapter.calculate_composite_warning_score(
                event_id, customer_key, event_data, timestamp
            )
            result['warning_result'] = warning_result
            
            if warning_result:
                # Update watchlist
                self.warning_adapter.update_watchlist(
                    customer_key,
                    warning_result.warning_level,
                    warning_result.warning_score,
                    timestamp
                )
                
                # Record decision
                decision_record = self.decision_auditor.record_warning_decision(
                    warning_result.__dict__, event_id
                )
                result['decision_records'].append(decision_record.__dict__)
            
            # Step 5: Generate alerts
            alerts = []
            
            # Alert from anomaly
            if result['anomaly_result']:
                anomaly_alert = self.alert_engine.generate_alert_from_anomaly(
                    result['anomaly_result'].__dict__
                )
                if anomaly_alert:
                    alerts.append(anomaly_alert)
                    decision_record = self.decision_auditor.record_alert_decision(
                        anomaly_alert.__dict__, event_id
                    )
                    result['decision_records'].append(decision_record.__dict__)
            
            # Alert from risk
            if risk_result:
                risk_alert = self.alert_engine.generate_alert_from_risk(
                    risk_result.__dict__
                )
                if risk_alert:
                    alerts.append(risk_alert)
                    decision_record = self.decision_auditor.record_alert_decision(
                        risk_alert.__dict__, event_id
                    )
                    result['decision_records'].append(decision_record.__dict__)
            
            # Alert from warning
            if warning_result:
                warning_alert = self.alert_engine.generate_alert_from_warning(
                    warning_result.__dict__
                )
                if warning_alert:
                    alerts.append(warning_alert)
                    decision_record = self.decision_auditor.record_alert_decision(
                        warning_alert.__dict__, event_id
                    )
                    result['decision_records'].append(decision_record.__dict__)
            
            result['alert_result'] = [alert.__dict__ for alert in alerts]
            
            # Step 6: Run model predictions (if applicable)
            if event_type in ['transaction', 'account_update']:
                self._run_predictions(customer_key, event_id)
            
            result['processing_end'] = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            result['processing_latency_ms'] = (
                datetime.now(timezone.utc).replace(tzinfo=None) - start_time
            ).total_seconds() * 1000
            
            # Mark event as processed for idempotency
            idempotency_key = f"idempotency:{event_id}:processed"
            ttl_seconds = self.config.event_processing.idempotency_ttl_seconds
            self.feature_store.redis_client.setex(
                idempotency_key, ttl_seconds, timestamp.isoformat()
            )
            
            # Commit Kafka offset after successful processing
            if not self.config.kafka.enable_auto_commit:
                try:
                    self.kafka_consumer.commit(asynchronous=True)
                    logger.debug(f"Committed offset for event {event_id}")
                except Exception as e:
                    logger.error(f"Failed to commit offset for event {event_id}: {e}")
            
            logger.info(
                f"Event {event_id} processed successfully in "
                f"{result['processing_latency_ms']:.2f}ms"
            )
        
        except Exception as e:
            logger.error(f"Error processing event {event_id}: {e}")
            result['success'] = False
            result['errors'].append(str(e))
            result['processing_end'] = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        
        return result
    
    def _compute_features(
        self,
        event_data: Dict[str, Any],
        customer_key: str,
        timestamp: datetime
    ):
        """Compute and store features from event.
        
        Args:
            event_data: Event data
            customer_key: Customer identifier
            timestamp: Event timestamp
        """
        try:
            # Use feature adapter to compute and store features
            # This bridges with existing batch feature engineering
            
            if event_data.get('event_type') == 'transaction':
                amount = event_data.get('amount', 0)
                account_id = event_data.get('account_id')
                
                # Store transaction features
                self.feature_adapter.store_transaction_features(
                    customer_key=customer_key,
                    account_id=account_id,
                    amount=amount,
                    timestamp=timestamp
                )
            
            elif event_data.get('event_type') == 'account_update':
                balance = event_data.get('balance', 0)
                account_id = event_data.get('account_id')
                
                # Store account features
                self.feature_adapter.store_account_features(
                    customer_key=customer_key,
                    account_id=account_id,
                    balance=balance,
                    timestamp=timestamp
                )
            
            # Store customer features
            self.feature_adapter.store_customer_features(
                customer_key=customer_key,
                timestamp=timestamp
            )
        
        except Exception as e:
            logger.error(f"Error computing features: {e}")
            raise
    
    def _detect_anomalies(
        self,
        event_id: str,
        customer_key: str,
        event_data: Dict[str, Any],
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Detect anomalies in event.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            event_data: Event data
            timestamp: Event timestamp
        
        Returns:
            Anomaly result or None
        """
        try:
            amount = event_data.get('amount', 0)
            
            # Detect amount anomaly
            anomaly_result = self.anomaly_adapter.detect_amount_anomaly(
                event_id, customer_key, amount, timestamp
            )
            
            if anomaly_result:
                return anomaly_result.__dict__
            
            # Detect velocity anomaly
            velocity_result = self.anomaly_adapter.detect_velocity_anomaly(
                event_id, customer_key, timestamp
            )
            
            if velocity_result:
                return velocity_result.__dict__
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return None
    
    def _run_predictions(self, customer_key: str, event_id: str):
        """Run model predictions for customer.
        
        Args:
            customer_key: Customer identifier
            event_id: Event identifier
        """
        try:
            # Run churn prediction
            churn_result = self.online_model.predict_churn(customer_key)
            logger.debug(f"Churn prediction for {customer_key}: {churn_result}")
            
            # Run risk prediction
            risk_result = self.online_model.predict_risk(customer_key)
            logger.debug(f"Risk prediction for {customer_key}: {risk_result}")
            
            # Run CLV prediction
            clv_result = self.online_model.predict_clv(customer_key)
            logger.debug(f"CLV prediction for {customer_key}: {clv_result}")
        
        except Exception as e:
            logger.error(f"Error running predictions: {e}")
    
    def start(self):
        """Start the streaming pipeline."""
        logger.info("Starting streaming pipeline")
        self.is_running = True
        
        # Start Kafka consumer
        self.kafka_consumer.start()
        
        logger.info("Streaming pipeline started")
    
    def stop(self):
        """Stop the streaming pipeline."""
        logger.info("Stopping streaming pipeline")
        self.is_running = False
        
        # Stop Kafka consumer
        self.kafka_consumer.stop()
        
        logger.info("Streaming pipeline stopped")
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics.
        
        Returns:
            Pipeline metrics
        """
        return {
            'is_running': self.is_running,
            'components_initialized': True,
            'config': {
                'kafka_brokers': self.config.kafka.bootstrap_servers,
                'redis_host': self.config.redis.host,
                'redis_port': self.config.redis.port,
            }
        }
