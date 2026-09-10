# Architecture Audit

**Generated:** 2026-09-08
**Repository:** Banking Customer Profitability and Risk Analytics Platform

## Executive Summary

This audit examines the architecture of the streaming platform implementation, focusing on imports, dependencies, component integration, and structural integrity.

## Critical Issues

### CRITICAL-001: Configuration Structure Mismatch

**Location:** `src/streaming/config.py` vs `config/streaming.yaml`

**Problem:** The `StreamingConfig` class expects a `kafka` configuration object, but the YAML configuration uses `broker` as the key name.

**Evidence:**
- `config.py` line 146: `broker_config = BrokerConfig(**streaming_settings.get("broker", {}))`
- `config.py` defines `BrokerConfig` dataclass
- `consumer.py` line 40: `'bootstrap.servers': config.kafka.bootstrap_servers`
- `consumer.py` line 41: `'group.id': config.kafka.group_id`
- `config/streaming.yaml` line 20: `broker:` (not `kafka:`)

**Impact:** Kafka consumer and producer will fail to initialize with AttributeError.

**Root Cause:** Inconsistent naming between configuration class and YAML structure.

**Fix Required:** 
1. Update `StreamingConfig` to use `broker` instead of `kafka` for the configuration object
2. Update all references from `config.kafka` to `config.broker` in consumer/producer

**Severity:** CRITICAL - System will not start

---

### CRITICAL-002: Missing Kafka Configuration Fields

**Location:** `src/streaming/config.py` BrokerConfig dataclass

**Problem:** The `BrokerConfig` dataclass is missing required fields that are referenced in consumer/producer but not defined.

**Evidence:**
- `consumer.py` line 42: `config.kafka.client_id`
- `consumer.py` line 43: `config.kafka.auto_offset_reset`
- `consumer.py` line 44: `config.kafka.enable_auto_commit`
- `consumer.py` line 45: `config.kafka.auto_commit_interval_ms`
- `consumer.py` line 50: `config.kafka.fetch_min_bytes`
- `consumer.py` line 51: `config.kafka.fetch_max_wait_ms`
- `producer.py` line 42: `config.kafka.client_id`
- `producer.py` line 43: `config.kafka.acks`
- `producer.py` line 44: `config.kafka.compression_type`
- `producer.py` line 45: `config.kafka.linger_ms`
- `producer.py` line 46: `config.kafka.batch_size`
- `producer.py` line 47: `config.kafka.max_in_flight`
- `producer.py` line 48: `config.kafka.enable_idempotence`
- `producer.py` line 49: `config.kafka.message_timeout_ms`
- `producer.py` line 50: `config.kafka.queue_buffering_max_messages`
- `producer.py` line 51: `config.kafka.queue_buffering_max_kbytes`

**Impact:** AttributeError when initializing Kafka consumer/producer.

**Root Cause:** Incomplete BrokerConfig dataclass definition.

**Fix Required:** Add all missing fields to BrokerConfig dataclass with appropriate defaults.

**Severity:** CRITICAL - System will not start

---

### CRITICAL-003: Orchestrator Configuration Reference Error

**Location:** `src/streaming/orchestrator/pipeline_orchestrator.py`

**Problem:** The orchestrator references `config.broker.brokers` which doesn't exist in the BrokerConfig dataclass.

**Evidence:**
- `pipeline_orchestrator.py` line 417: `'kafka_brokers': self.config.broker.brokers`
- `BrokerConfig` only has `bootstrap_servers` not `brokers`

**Impact:** AttributeError when getting pipeline metrics.

**Root Cause:** Inconsistent field naming.

**Fix Required:** Change `config.broker.brokers` to `config.broker.bootstrap_servers`.

**Severity:** HIGH - Metrics endpoint will fail

---

### HIGH-001: Missing Idempotency Implementation

**Location:** Streaming pipeline

**Problem:** No actual idempotency logic found in the code reviewed. Configuration defines `idempotency_ttl_seconds` but no implementation uses it.

**Evidence:**
- `config/base.yaml` line 55: `idempotency_ttl_seconds: 86400`
- `config/streaming.yaml` line 244: `idempotency_key: "idempotency:{event_id}:{stage}"`
- No code found that checks for duplicate events before processing
- No code found that stores processed event IDs
- No code found that implements idempotency checks

**Impact:** Duplicate events will be processed multiple times, violating at-least-once semantics.

**Root Cause:** Idempotency is configured but not implemented.

**Fix Required:** Implement idempotency check in pipeline orchestrator before processing events.

**Severity:** HIGH - Data correctness issue

---

### HIGH-002: Event Schema Mismatch

**Location:** Event-time processor vs actual event structure

**Problem:** Event-time processor expects `event_timestamp` field but the orchestrator uses `timestamp`.

**Evidence:**
- `event_time.py` line 69: `if 'event_timestamp' not in event:`
- `pipeline_orchestrator.py` line 132: `timestamp = datetime.fromisoformat(event_data.get('timestamp', ...))`

**Impact:** Event-time processor will raise ValueError for events using `timestamp` instead of `event_timestamp`.

**Root Cause:** Inconsistent event field naming.

**Fix Required:** Standardize on either `event_timestamp` or `timestamp` across all components.

**Severity:** HIGH - Events will fail to process

---

### HIGH-003: Missing Offset Commit Logic

**Location:** Kafka consumer

**Problem:** Consumer has `enable_auto_commit: false` but no explicit offset commit logic in the orchestrator.

**Evidence:**
- `config/base.yaml` line 24: `enable_auto_commit: false`
- `consumer.py` has commit methods but they're not called by orchestrator
- `pipeline_orchestrator.py` processes events but never commits offsets

**Impact:** Events will be reprocessed on consumer restart, causing duplicates.

**Root Cause:** Orchestrator doesn't manage offset commits.

**Fix Required:** Add offset commit after successful event processing in orchestrator.

**Severity:** HIGH - Duplicate processing on restart

---

### MEDIUM-001: Circular Dependency Risk

**Location:** Streaming components

**Problem:** Multiple components depend on each other in a way that could cause circular imports.

**Evidence:**
- `StreamingOrchestrator` depends on all adapters
- Adapters depend on `FeatureStore`
- `FeatureStore` depends on `StreamingConfig`
- All components are initialized in `_initialize_components()` which could fail if any dependency fails

**Impact:** Hard to test components in isolation, potential initialization failures.

**Root Cause:** Tight coupling between components.

**Fix Required:** Consider dependency injection pattern to decouple components.

**Severity:** MEDIUM - Testability and maintainability

---

### MEDIUM-002: No Transaction Boundaries

**Location:** Database writes

**Problem:** No evidence of transaction management for database writes in streaming components.

**Evidence:**
- `risk_engine.py` calls `update_customer_risk_level` but no transaction context
- `warning_adapter.py` calls `update_watchlist` but no transaction context
- Multiple database writes could fail partially

**Impact:** Inconsistent database state on partial failures.

**Root Cause:** No explicit transaction management.

**Fix Required:** Wrap database writes in transaction contexts.

**Severity:** MEDIUM - Data consistency risk

---

### MEDIUM-003: Missing Error Recovery

**Location:** Pipeline orchestrator

**Problem:** Orchestrator catches exceptions but doesn't implement retry or dead-letter queue logic.

**Evidence:**
- `pipeline_orchestrator.py` line 262: `except Exception as e:`
- Only logs error and marks as failed
- No retry logic
- No DLQ integration

**Impact:** Failed events are lost.

**Root Cause:** Incomplete error handling.

**Fix Required:** Add retry logic and DLQ integration for failed events.

**Severity:** MEDIUM - Data loss risk

---

### LOW-001: Hardcoded Thresholds

**Location:** Streaming adapters

**Problem:** Severity thresholds are hardcoded in classes instead of being configurable.

**Evidence:**
- `anomaly_adapter.py` lines 64-69: `SEVERITY_THRESHOLDS` hardcoded
- `warning_adapter.py` lines 65-70: `THRESHOLDS` hardcoded

**Impact:** Cannot tune thresholds without code changes.

**Root Cause:** Configuration not externalized.

**Fix Required:** Move thresholds to configuration files.

**Severity:** LOW - Operational flexibility

---

### LOW-002: Missing Type Hints

**Location:** Various streaming components

**Problem:** Some methods lack complete type hints.

**Evidence:**
- Various methods use `Dict[str, Any]` instead of specific types
- Some return types are not specified

**Impact:** Reduced code clarity and IDE support.

**Root Cause:** Incomplete type annotations.

**Fix Required:** Add complete type hints.

**Severity:** LOW - Code quality

---

## Dependency Analysis

### Import Graph

```
StreamingConfig
  ├── BrokerConfig (MISSING FIELDS)
  ├── SchemaRegistryConfig
  ├── RedisConfig
  ├── FeatureStoreConfig
  ├── EventProcessingConfig
  └── AlertConfig

StreamingOrchestrator
  ├── FeatureStore
  ├── FeatureStoreAdapter
  ├── StreamingAnomalyAdapter
  ├── RealTimeRiskEngine
  ├── StreamingWarningAdapter
  ├── AlertEngine
  ├── DecisionAuditor
  ├── ModelRegistry
  ├── OnlineModel
  └── KafkaConsumer (BROKEN - config.kafka reference)

KafkaConsumer
  ├── StreamingConfig (BROKEN - config.kafka reference)
  └── MessageDeserializer

KafkaProducer
  ├── StreamingConfig (BROKEN - config.kafka reference)
  └── MessageSerializer

StreamProcessor
  ├── EventTimeProcessor
  ├── WatermarkManager
  ├── LateEventHandler
  ├── StateManager
  └── WindowOperator
```

### Orphan Modules

No orphan modules identified - all streaming modules appear to be referenced.

### Unused Classes

No unused classes identified at this time.

### Dead Code

No obvious dead code identified, but some methods may not be called:
- `BatchKafkaConsumer` - defined but not used
- `AsyncKafkaProducer` - defined but not used

---

## Configuration Issues

### YAML Structure Mismatches

| Component | Expected Field | Actual Field | Status |
|-----------|---------------|-------------|--------|
| BrokerConfig | kafka | broker | MISMATCH |
| BrokerConfig | brokers | bootstrap_servers | MISMATCH |
| Consumer | config.kafka | config.broker | MISMATCH |
| Producer | config.kafka | config.broker | MISMATCH |

### Missing Configuration Fields

The following fields are referenced in code but not defined in config:
- `client_id`
- `auto_commit_interval_ms`
- `fetch_min_bytes`
- `fetch_max_wait_ms`
- `acks`
- `compression_type`
- `linger_ms`
- `batch_size`
- `max_in_flight`
- `enable_idempotence`
- `message_timeout_ms`
- `queue_buffering_max_messages`
- `queue_buffering_max_kbytes`

---

## Component Integration Issues

### Orchestrator Integration

**Issue:** Orchestrator initializes all components but doesn't handle initialization failures gracefully.

**Impact:** If one component fails to initialize, the entire pipeline fails to start.

**Recommendation:** Add graceful degradation and health checks per component.

### Kafka Integration

**Issue:** Consumer/producer configuration is broken due to field name mismatches.

**Impact:** Kafka integration is non-functional.

**Recommendation:** Fix configuration structure immediately.

### Redis Integration

**Issue:** Redis connection is created but connection pool configuration is not used.

**Impact:** May not handle high load efficiently.

**Recommendation:** Verify connection pool configuration is applied.

---

## Architecture Strengths

1. **Modular Design:** Components are well-separated into modules
2. **Adapter Pattern:** Streaming adapters reuse batch algorithms
3. **Event-Time Processing:** Proper event-time semantics with watermarks
4. **Late Event Handling:** Multiple strategies for late events
5. **Window Operations:** Support for tumbling, sliding, and session windows
6. **Feature Versioning:** Feature store supports versioning
7. **Audit Trail:** Decision auditor for regulatory compliance

---

## Recommendations

### Immediate Actions (P0)

1. Fix configuration structure mismatch (broker vs kafka)
2. Add missing fields to BrokerConfig dataclass
3. Fix orchestrator metrics reference
4. Implement idempotency checks
5. Standardize event field naming (event_timestamp vs timestamp)

### Short-term Actions (P1)

6. Add offset commit logic to orchestrator
7. Add transaction management for database writes
8. Implement retry logic and DLQ integration
9. Add graceful component initialization

### Medium-term Actions (P2)

10. Implement dependency injection for better testability
11. Externalize hardcoded thresholds to configuration
12. Add comprehensive error recovery
13. Add connection pooling verification for Redis

### Long-term Actions (P3)

14. Add complete type hints
15. Remove or document unused classes
16. Add integration tests for component interactions

---

## Summary

**Total Issues Found:** 13
- CRITICAL: 3
- HIGH: 3
- MEDIUM: 3
- LOW: 2
- INFO: 2

**Overall Assessment:** The streaming architecture has good modular design and proper event-time semantics, but critical configuration issues prevent the system from starting. The most urgent issues are configuration mismatches that must be fixed before any testing can proceed.
