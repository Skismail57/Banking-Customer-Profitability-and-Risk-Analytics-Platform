# Anomaly Detection Audit

**Generated:** 2026-09-08
**Repository:** Banking Customer Profitability and Risk Analytics Platform

## Executive Summary

This audit examines the streaming anomaly detection implementation, including algorithm adaptation, state management, detection methods, and integration with batch anomaly detection.

## Streaming Anomaly Adapter

### StreamingAnomalyAdapter Class

**Location:** `src/streaming/anomaly/anomaly_adapter.py`

**Implementation Review:**

**Core Functionality:**
- Adapts batch AnomalyDetector for streaming
- Maintains streaming statistics in Redis
- Supports amount, frequency, and velocity anomaly detection
- Uses IQR and Z-score methods
- Provides severity classification
- State persistence via Redis

**Detection Methods:**
- `detect_amount_anomaly()` - Amount outlier detection
- `detect_frequency_anomaly()` - Transaction frequency anomalies
- `detect_velocity_anomaly()` - Rapid transaction detection

**Assessment:** ✅ EXCELLENT
- Proper adapter pattern
- Algorithm reuse from batch
- Streaming state management
- Multiple detection methods
- Severity classification
- Redis state persistence

**Issues:** None identified

---

## Batch Anomaly Detection

### AnomalyDetector Class

**Location:** `src/transaction_analytics/anomaly.py`

**Implementation Review:**

**Detection Methods:**
- `detect_amount_anomalies()` - Amount outliers (IQR, Z-score, Isolation Forest)
- `detect_frequency_anomalies()` - Transaction frequency per customer
- `detect_pattern_anomalies()` - Unusual transaction patterns

**Algorithms:**
- IQR (Interquartile Range)
- Z-score
- Isolation Forest (mentioned but not implemented in reviewed code)

**Assessment:** ✅ GOOD
- Multiple detection methods
- Statistical algorithms
- Customer-level analysis
- Pattern detection

**Issues:** None identified

---

## Algorithm Adaptation

### Streaming Statistics

**Implementation:**
- Welford's algorithm for online mean/variance calculation
- Incremental quantile calculation (keeps last 1000 values)
- State stored in Redis with TTL
- Per-customer statistics

**Assessment:** ✅ EXCELLENT
- Proper online algorithm (Welford's)
- Quantile approximation
- State persistence
- TTL management

**Issues:** None identified

---

### Algorithm Parity

**Comparison:**

| Aspect | Batch | Streaming | Status |
|--------|-------|-----------|--------|
| IQR Method | ✅ Full dataset | ✅ Streaming approximation | ✅ Aligned |
| Z-score Method | ✅ Full dataset | ✅ Streaming approximation | ✅ Aligned |
| Isolation Forest | ✅ Mentioned | ❌ Not implemented | ⚠️ Missing |
| Pattern Detection | ✅ Implemented | ❌ Not implemented | ⚠️ Missing |

**Assessment:** ⚠️ PARTIAL
- IQR and Z-score adapted correctly
- Isolation Forest not adapted for streaming
- Pattern detection not adapted for streaming

**Issues:**

### ANOM-001 Missing Isolation Forest in Streaming

**Problem:** Isolation Forest method is mentioned in batch but not implemented in streaming.

**Evidence:**
- Batch mentions `isolation_forest` method
- Streaming only implements `iqr` and `zscore`
- Isolation Forest requires historical context

**Impact:** Cannot use advanced ML-based anomaly detection in streaming.

**Recommendation:** Implement streaming-compatible Isolation Forest or note limitation.

**Severity:** LOW

---

### ANOM-002 Missing Pattern Detection in Streaming

**Problem:** Pattern detection is implemented in batch but not in streaming.

**Evidence:**
- Batch has `detect_pattern_anomalies()` method
- Streaming has no pattern detection
- Pattern detection requires historical context

**Impact:** Cannot detect complex transaction patterns in streaming.

**Recommendation:** Implement streaming pattern detection or note limitation.

**Severity:** LOW

---

## State Management

### Redis State Storage

**Key Patterns:**
- `anomaly_stats:{customer_key}:{anomaly_type}` - Statistics
- `anomaly_velocity:{customer_key}` - Velocity history

**State Data:**
- Count, sum, sum_sq, mean, std, min, max, q1, q3, values
- Velocity timestamps (last 100)

**TTL:** Uses `idempotency_ttl_seconds` from config

**Assessment:** ✅ GOOD
- Proper key structure
- Comprehensive state
- TTL management
- Velocity history tracking

**Issues:** None identified

---

### State Initialization

**Implementation:**
- Empty statistics initialized on first access
- Welford's algorithm handles first value
- Quantiles calculated after 4+ values

**Assessment:** ✅ GOOD
- Proper initialization
- Handles cold start
- Minimum sample requirements

**Issues:** None identified

---

## Detection Methods

### Amount Anomaly Detection

**Implementation:**
- IQR method: Q1 - threshold*IQR, Q3 + threshold*IQR
- Z-score method: abs(value - mean) / std > threshold
- Anomaly score based on distance from bounds
- Severity classification based on score

**Assessment:** ✅ EXCELLENT
- Proper statistical methods
- Score calculation
- Severity classification
- Context data included

**Issues:** None identified

---

### Frequency Anomaly Detection

**Implementation:**
- Tracks transaction count
- Compares to mean + threshold*std
- Simplified for streaming (no window calculation)
- Uses historical mean/std

**Assessment:** ⚠️ SIMPLIFIED
- No actual window calculation in streaming
- Uses simplified threshold check
- May not match batch behavior exactly

**Issues:**

### ANOM-003 Simplified Frequency Detection

**Problem:** Streaming frequency detection is simplified compared to batch.

**Evidence:**
- Batch calculates frequency per time window
- Streaming only tracks count and compares to threshold
- No actual time window calculation in streaming

**Impact:** May not detect true frequency anomalies accurately.

**Recommendation:** Implement proper time-window frequency calculation in streaming.

**Severity:** MEDIUM

---

### Velocity Anomaly Detection

**Implementation:**
- Tracks recent transaction timestamps
- Counts transactions in time window
- Compares to max threshold
- Keeps last 100 timestamps

**Assessment:** ✅ GOOD
- Proper window calculation
- Velocity tracking
- Threshold comparison
- History management

**Issues:** None identified

---

## Severity Classification

### Severity Thresholds

**Implementation:**
- Critical: >= 0.95
- High: >= 0.90
- Medium: >= 0.80
- Low: >= 0.70

**Assessment:** ✅ GOOD
- Clear severity levels
- Configurable thresholds
- Score-based classification

**Issues:**

### ANOM-004 Hardcoded Severity Thresholds

**Problem:** Severity thresholds are hardcoded in the class.

**Evidence:**
- `SEVERITY_THRESHOLDS` hardcoded in class
- Not configurable via config file
- Not per-customer configurable

**Impact:** Cannot tune thresholds without code changes.

**Recommendation:** Move thresholds to configuration.

**Severity:** LOW

---

## Integration with Orchestrator

### Orchestrator Integration

**Location:** `src/streaming/orchestrator/pipeline_orchestrator.py`

**Implementation:**
- `_detect_anomalies()` method calls StreamingAnomalyAdapter
- Called for transaction events only
- Results stored in context
- Used for alert generation

**Assessment:** ✅ GOOD
- Proper integration
- Event-type filtering
- Context storage
- Alert integration

**Issues:** None identified

---

## Fairness Considerations

### Documented Fairness

**Implementation:**
- Fairness considerations documented in docstring
- Recommendations for per-segment thresholds
- Recommendations for demographic monitoring

**Assessment:** ✅ DOCUMENTED
- Fairness awareness
- Documentation present
- Recommendations provided

**Issues:**

### ANOM-005 No Per-Segment Thresholds

**Problem:** No per-customer-segment threshold implementation.

**Evidence:**
- Single threshold for all customers
- No segment-based calibration
- No demographic-based thresholds

**Impact:** May have bias across customer segments.

**Recommendation:** Implement per-segment thresholds.

**Severity:** MEDIUM

---

## Performance

### Performance Considerations

**Implementation:**
- Incremental statistics (Welford's algorithm)
- Limited value history (last 1000)
- Redis for state persistence
- No batch processing

**Assessment:** ✅ EFFICIENT
- Online algorithms
- Memory-efficient
- Fast Redis operations
- Suitable for streaming

**Issues:** None identified

---

## Error Handling

### Error Handling

**Implementation:**
- Try-catch blocks in state operations
- Logging for errors
- Returns None on no anomaly
- No retry logic

**Assessment:** ⚠️ BASIC
- Basic error handling
- No retry logic
- No fallback mechanism

**Issues:**

### ANOM-006 No Retry Logic for Redis

**Problem:** No retry logic for Redis state operations.

**Evidence:**
- Direct Redis calls
- No retry on failure
- No exponential backoff

**Impact:** Transient Redis failures cause state loss.

**Recommendation:** Implement retry logic for Redis operations.

**Severity:** LOW

---

## Summary

**Total Issues Found:** 6
- MEDIUM: 2
- LOW: 4

**Overall Assessment:** The streaming anomaly detection implementation is excellent with proper algorithm adaptation, state management, and integration. The main gaps are in missing advanced methods (Isolation Forest, pattern detection) and simplified frequency detection. Fairness considerations are documented but not implemented.

## Recommendations

### Short-term Actions (P1)

1. Implement proper time-window frequency calculation in streaming (ANOM-003)
2. Implement per-segment thresholds (ANOM-005)

### Medium-term Actions (P2)

3. Move severity thresholds to configuration (ANOM-004)
4. Implement retry logic for Redis operations (ANOM-006)

### Long-term Actions (P3)

5. Document Isolation Forest limitation or implement streaming-compatible version (ANOM-001)
6. Document pattern detection limitation or implement streaming version (ANOM-002)
