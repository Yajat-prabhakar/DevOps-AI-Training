# Multi-System Log Correlation Analysis

**Exercise 1.4** | Incident Date: August 26, 2026 | Severity: P2 (Major)

---

## Executive Summary

**Duration:** 12 minutes (10:09:00 - 10:11:01 UTC)  
**Impact:** Complete API unavailability for ~12 minutes  
**Affected Systems:** Backend API, Frontend (indirectly)  
**Root Cause:** PostgreSQL connection limit exceeded due to long-running transactions  
**Resolution:** Automatic connection recovery mechanism triggered  

---

## Incident Timeline

| Time (UTC) | Event | System | Confidence | Evidence |
|------------|-------|--------|------------|----------|
| 10:07:30 | Order processing begins | Backend | 100% | `backend-app.log:2026-08-26 10:07:30.978` |
| 10:07:35 | First batch completes (5.1s) | PostgreSQL | 100% | `postgresql.log:2026-08-26 10:07:35.123` |
| 10:08:00 | Connections begin accumulating | PostgreSQL | 95% | Connection count rising in logs |
| 10:08:15 | Second order batch starts | Backend | 100% | `backend-app.log:2026-08-26 10:08:15.445` |
| 10:08:30 | Third order batch starts | Backend | 100% | `backend-app.log:2026-08-26 10:08:30.434` |
| 10:08:45 | Fourth order batch starts | Backend | 100% | `backend-app.log:2026-08-26 10:08:45.423` |
| **10:09:00** | **Connection limit hit** | **PostgreSQL** | **100%** | `postgresql.log:FATAL: too many connections for role "app"` |
| 10:09:00 | Connection pool exhausted | Backend | 100% | `backend-app.log:CRITICAL: Max retries exceeded` |
| 10:09:00 - 10:10:59 | 503 errors returned | Nginx | 100% | `nginx-access.log:503` responses |
| 10:11:00 | Recovery mechanism triggered | Backend | 100% | `backend-app.log:Closing stale connections: 15 terminated` |
| 10:11:01 | Service restored | All | 100% | `backend-app.log:Database connection restored` |

---

## Cascading Failure Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FAILURE CASCADE DIAGRAM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                                                           │
│  │ Order        │                                                           │
│  │ Processing   │                                                           │
│  │ Trigger      │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────┐    ┌──────────────┐                                       │
│  │ Long-running │───▶│ Connection   │                                       │
│  │ Transactions │    │ Pool Filling │                                       │
│  │ (5s each)    │    │              │                                       │
│  └──────────────┘    └──────┬───────┘                                       │
│                             │                                               │
│                             ▼                                               │
│                      ┌──────────────┐                                       │
│                      │ Connection   │                                       │
│                      │ Limit (20)   │                                       │
│                      │ Reached      │                                       │
│                      └──────┬───────┘                                       │
│                             │                                               │
│              ┌──────────────┼──────────────┐                                │
│              ▼              ▼              ▼                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ New          │  │ Backend API  │  │ Frontend     │                      │
│  │ Connections  │  │ Returns      │  │ Shows Error  │                      │
│  │ Rejected     │  │ 503 Errors   │  │ Page         │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Log Correlation Analysis

### Phase 1: Normal Operation (10:00:00 - 10:07:29)

**PostgreSQL Logs:**
- Connections received: 15 total
- All connections authorized successfully
- Query duration: ~5ms average
- No errors or warnings

**Backend Logs:**
- Health checks passing every 30s
- All API requests returning 200 OK
- Connection pool: healthy (active < 10)

**Nginx Logs:**
- All requests returning 200
- Average response time: < 100ms

**Correlation:** All systems operating within normal parameters.

---

### Phase 2: Order Processing Surge (10:07:30 - 10:08:59)

**PostgreSQL Logs:**
- 4 order processing transactions initiated
- Each transaction: ~5.1 seconds (SELECT FOR UPDATE)
- Connections not being released after completion
- Connection count: 15 → 20 (at limit)

**Backend Logs:**
- 4 batch processing requests received
- Each batch processing 5 orders
- Connection pool utilization: 100% by 10:08:59

**Correlation:** Order processing holding connections open longer than expected. The `SELECT ... FOR UPDATE` pattern creates row-level locks that prevent connection release.

---

### Phase 3: Connection Exhaustion (10:09:00 - 10:10:59)

**PostgreSQL Logs:**
```
10:09:00.002 UTC [58] FATAL:  too many connections for role "app"
10:09:00.003 UTC [59] FATAL:  too many connections for role "app"
... (42 similar errors)
```

**Backend Logs:**
```
10:09:00.412 [ERROR] api: Database connection failed: too many connections for role "app"
10:09:00.413 [ERROR] api: Connection pool exhausted: active=20, idle=0, waiting=5
10:09:07.420 [CRITICAL] api: Max retries exceeded. Service degraded.
```

**Nginx Logs:**
```
10:09:00 "GET /api/hello HTTP/1.1" 503 82
10:09:01 "GET /api/hello HTTP/1.1" 503 82
... (96 similar 503 responses)
```

**Correlation:**
- PostgreSQL rejecting new connections at 10:09:00
- Backend immediately failing health checks
- Nginx returning 503 to all client requests
- **Cascading failure complete**

---

### Phase 4: Recovery (10:11:00 - 10:11:01)

**Backend Logs:**
```
10:11:00.534 [INFO] api: Attempting database connection recovery...
10:11:00.535 [INFO] api: Closing stale connections: 15 connections terminated
10:11:01.536 [INFO] api: Database connection restored
```

**PostgreSQL Logs:**
```
10:12:00.000 UTC [45] LOG:  disconnection: session time: 0:11:44.877
10:12:00.001 UTC [46] LOG:  disconnection: session time: 0:10:59.545
... (15 total disconnections)
```

**Correlation:**
- Backend detected stale connections and terminated them
- PostgreSQL accepted new connections
- Service restored in < 2 seconds

---

## Root Cause Analysis

### Primary Cause
**Connection limit misconfiguration:** The PostgreSQL role `app` has a connection limit of 20, but the application's connection pool is configured with `max=20`. This creates zero headroom for burst traffic.

### Contributing Factors

| Factor | Impact | Confidence |
|--------|--------|------------|
| Long-running transactions (5s each) | High | 100% |
| No connection timeout/idle cleanup | Medium | 90% |
| Order processing doesn't release connections | High | 95% |
| No circuit breaker pattern | Medium | 85% |

### Evidence Chain

1. **PostgreSQL connection limit** = 20 (verified in logs)
2. **Backend pool size** = 20 (from application config)
3. **Order processing** holds connections for ~5 seconds each
4. **4 concurrent batches** × 5 connections each = 20 connections
5. **No connection release** between batches

---

## Impact Assessment

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Error Rate | 100% (for 12 min) | < 1% | Breached |
| P95 Latency | > 30s (503 timeout) | < 500ms | Breached |
| Affected Users | ~150 requests | N/A | - |
| Data Loss | None | None | OK |
| Downstream Services | None | N/A | OK |

---

## Monitoring Improvements Recommended

### 1. Connection Pool Monitoring (Critical)

```yaml
# prometheus.yml - Add to scrape config
- job_name: 'postgresql'
  static_configs:
    - targets: ['postgres:5432']
  metrics_path: /metrics

# Alert: Connection pool exhaustion
- alert: PostgreSQLConnectionPoolExhausted
  expr: pg_stat_activity_count{role="app"} > 18
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "PostgreSQL connection pool nearly exhausted"
    description: "{{ $value }} connections active (limit: 20)"
```

### 2. API Error Rate Alert

```yaml
- alert: HighAPIErrorRate
  expr: rate(http_requests_total{status=~"5.."}[1m]) > 0.05
  for: 30s
  labels:
    severity: critical
  annotations:
    summary: "High API error rate detected"
    description: "{{ $value | humanizePercentage }} of requests returning errors"
```

### 3. Connection Leak Detection

```yaml
# Alert on connections not being released
- alert: PotentialConnectionLeak
  expr: pg_stat_activity_count{state="idle in transaction"} > 5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Potential connection leak detected"
    description: "{{ $value }} connections idle in transaction"
```

### 4. Application-Level Monitoring

```python
# Add to Flask app
from prometheus_client import Gauge, Counter

db_pool_active = Gauge('db_pool_active', 'Active database connections')
db_pool_idle = Gauge('db_pool_idle', 'Idle database connections')
db_pool_waiting = Gauge('db_pool_waiting', 'Waiting for connection')
db_errors = Counter('db_errors_total', 'Total database errors', ['error_type'])

# Update in health check
@app.route("/api/health")
def health():
    db_pool_active.set(pool._active)
    db_pool_idle.set(pool._idle)
    db_pool_waiting.set(pool._waiting)
    ...
```

### 5. Circuit Breaker Implementation

```python
# Add circuit breaker pattern
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def get_db_connection():
    return psycopg2.connect(DB_DSN)

# This will automatically fail-fast when DB is unavailable
```

---

## Remediation Checklist

| # | Action | Owner | Priority | Status |
|---|--------|-------|----------|--------|
| 1 | Increase PostgreSQL connection limit to 50 | DBA | High | Pending |
| 2 | Reduce backend pool max to 15 (with 5 headroom) | Dev | High | Pending |
| 3 | Add connection idle timeout (30s) | Dev | High | Pending |
| 4 | Implement circuit breaker pattern | Dev | Medium | Pending |
| 5 | Add connection pool metrics to Prometheus | DevOps | High | Pending |
| 6 | Create Grafana dashboard for DB connections | DevOps | Medium | Pending |
| 7 | Optimize order processing queries | Dev | Medium | Pending |
| 8 | Add query timeout (10s max) | Dev | Medium | Pending |

---

## Lessons Learned

1. **Connection pool size must be < database connection limit** - Always leave headroom
2. **Long-running transactions need explicit timeouts** - 5s is too long for web requests
3. **Monitor connection state, not just count** - "idle in transaction" indicates leaks
4. **Circuit breakers prevent cascading failures** - Fail fast, recover gracefully
5. **Test with realistic load** - This only occurs under sustained traffic

---

## Appendix: Raw Log Files

- `logs/postgresql.log` - Database server logs
- `logs/backend-app.log` - Application server logs
- `logs/nginx-access.log` - Web server access logs

### Log Search Commands

```bash
# Find all connection errors
grep -i "too many connections" logs/postgresql.log

# Find all 503 errors
grep " 503 " logs/nginx-access.log | wc -l

# Find recovery events
grep -i "recovery\|restored" logs/backend-app.log

# Timeline of errors
grep -E "ERROR|CRITICAL|FATAL" logs/backend-app.log | head -20
```
