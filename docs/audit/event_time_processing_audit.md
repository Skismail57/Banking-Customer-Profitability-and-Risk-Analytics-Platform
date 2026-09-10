# Event-Time Processing Audit

**Generated:** 2026-09-08
**Repository:** Banking Customer Profitability and Risk Analytics Platform

## Executive Summary

This audit examines event-time processing implementation, including timestamp extraction, watermark calculation, late event handling, and window triggering.

## Event-Time Processing Components

### EventTimeProcessor

**Location:** `src/streaming/processor/event_time.py`

**Implementation Review:**

**Timestamp Extraction:**
- Extracts `event_timestamp` from event data
- Supports string (ISO format) and datetime objects
- Falls back to processing timestamp if event timestamp missing
- Configurable clock source (system or event)

**Assessment:** ✅ GOOD
- Robust timestamp extraction
- Multiple format support
- Fallback mechanism present

**Issues:** None identified

---

### WatermarkManager

**Location:** `src/streaming/processor/watermark.py`

**Implementation Review:**

**Watermark Calculation:**
- Per-source watermark tracking
- Global watermark as minimum of source watermarks
- Two strategies: max_minus_delay and min_timestamp
- Configurable out-of-orderness bound
- Watermark advancement logic

**Assessment:** ✅ EXCELLENT
- Proper watermark calculation
- Multi-source support
- Configurable strategies
- Out-of-orderness handling

**Issues:** None identified

---

### LateEventHandler

**Location:** `src/streaming/processor/late_events.py`

**Implementation Review:**

**Late Event Strategies:**
- DROP: Discard late events
- SIDE_OUTPUT: Send to side output for audit
- BUFFER: Buffer for potential reprocessing
- REPROCESS: Reprocess with updated state
- Configurable allowed lateness
- Configurable buffer size

**Assessment:** ✅ EXCELLENT
- Multiple strategies for different use cases
- Configurable behavior
- Side output for audit trail
- Buffer with size limits

**Issues:** None identified

---

### WindowOperator

**Location:** `src/streaming/processor/windows.py`

**Implementation Review:**

**Window Types:**
- Tumbling windows
- Sliding windows
- Session windows
- Event-time based assignment
- Watermark-based triggering

**Window Assignment:**
- Proper window boundary calculation
- Event-time alignment
- Multi-window assignment for sliding windows
- Session gap handling

**Window Triggering:**
- Watermark-based triggering
- Allowed lateness consideration
- Window result computation
- Active/completed window management

**Assessment:** ✅ EXCELLENT
- All standard window types
- Proper event-time semantics
- Late event handling in windows
- Efficient window management

**Issues:** None identified

---

## Integration with Orchestrator

### StreamProcessor Integration

**Location:** `src/streaming/processor/processor.py`

**Implementation:**
- Integrates EventTimeProcessor, WatermarkManager, LateEventHandler, WindowOperator
- Provides unified processing interface
- Manages component lifecycle
- Coordinates event flow

**Assessment:** ✅ GOOD
- Proper component integration
- Clean interface
- Lifecycle management

**Issues:** None identified

---

### Orchestrator Integration

**Location:** `src/streaming/orchestrator/pipeline_orchestrator.py`

**Implementation:**
- EventProcessor class integrates StreamProcessor with orchestrator
- Event-time handling in pipeline
- Late event handling in pipeline
- Watermark tracking in pipeline

**Assessment:** ⚠️ PARTIAL
- EventProcessor defined but not fully integrated
- Orchestrator doesn't use StreamProcessor directly
- Event-time processing not fully utilized in main pipeline

**Issues:**

### EVT-001 StreamProcessor Not Used in Main Pipeline

**Problem:** StreamProcessor with full event-time capabilities is defined but not used by the main orchestrator.

**Evidence:**
- `src/streaming/processor/processor.py` has StreamProcessor class
- `src/streaming/orchestrator/event_processor.py` has EventProcessor class
- Main orchestrator doesn't use either
- Orchestrator processes events sequentially without event-time semantics

**Impact:** Event-time processing capabilities are not utilized in the main pipeline.

**Recommendation:** Integrate StreamProcessor into main orchestrator to leverage event-time semantics.

**Severity:** MEDIUM

---

## Configuration

### Event Processing Configuration

**Location:** `config/base.yaml` and `config/environments/development.yaml`

**Settings:**
- `max_processing_time_seconds`: 60 (dev: 120)
- `idempotency_ttl_seconds`: 86400 (dev: 3600)
- `late_event_window_seconds`: 300 (dev: 600)
- `watermark_delay_seconds`: 60 (dev: 120)

**Assessment:** ✅ GOOD
- Configurable settings
- Environment-specific overrides
- Reasonable defaults

**Issues:** None identified

---

### Watermark Configuration

**Location:** `config/streaming.yaml`

**Settings:**
- `default_delay_seconds`: 60
- `max_out_of_order_seconds`: 300
- `update_interval_seconds`: 10

**Assessment:** ✅ GOOD
- Configurable watermark parameters
- Reasonable defaults
- Update interval configured

**Issues:** None identified

---

## Event-Time Semantics Verification

### Event Ordering

**Claim:** Events processed in event-time order within windows

**Actual:**
- Kafka guarantees order within partition
- Watermark ensures event-time ordering
- Windows trigger based on watermark

**Assessment:** ✅ CORRECT
- Event-time ordering achieved via watermarks
- Partition-level ordering maintained
- Window-based processing respects event-time

**Issues:** None identified

---

### Late Event Handling

**Claim:** Late events handled according to configured strategy

**Actual:**
- LateEventHandler implements multiple strategies
- Configurable allowed lateness
- Side output for audit trail

**Assessment:** ✅ CORRECT
- Late events properly detected
- Multiple handling strategies
- Configurable behavior

**Issues:** None identified

---

### Window Completeness

**Claim:** Windows complete when watermark passes window end

**Actual:**
- WindowOperator triggers windows based on watermark
- Allowed lateness considered
- Late events can still update windows within allowed lateness

**Assessment:** ✅ CORRECT
- Proper window triggering
- Allowed lateness respected
- Late event handling in windows

**Issues:** None identified

---

## Summary

**Total Issues Found:** 1
- MEDIUM: 1

**Overall Assessment:** The event-time processing implementation is excellent with proper timestamp extraction, watermark calculation, late event handling, and window operations. The main gap is that the full StreamProcessor with event-time capabilities is not integrated into the main orchestrator, so these capabilities are not fully utilized in production.

## Recommendations

### Short-term Actions (P1)

1. Integrate StreamProcessor into main orchestrator (EVT-001)

### Long-term Actions (P2)

2. Add event-time metrics to monitoring
3. Add watermark advancement alerts
4. Add late event rate monitoring
