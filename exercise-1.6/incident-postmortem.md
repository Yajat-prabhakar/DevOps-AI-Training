# Incident Post-Mortem: Database Connection Pool Exhaustion

**Incident ID:** INC-2026-0826-001  
**Severity:** P2 (Major)  
**Date:** August 26, 2026  
**Duration:** 12 minutes (10:09:00 - 10:11:01 UTC)  
**Author:** DevOps Team  
**Status:** Draft

---

## Executive Summary

On August 26, 2026, the production API service experienced a 12-minute outage due to database connection pool exhaustion. The incident was triggered by concurrent order processing jobs that held database connections for extended periods, exhausting the connection limit. Service was automatically restored when the application's connection recovery mechanism terminated stale connections.

**Business Impact:**
- **Duration:** 12 minutes
- **Affected Users:** ~150 requests returned 503 errors
- **Revenue Impact:** Minimal (internal tool)
- **Data Loss:** None
- **SLA Impact:** Within monthly SLA (99.9% uptime)

---

## Timeline (All times in UTC)

| Time | Event | Source |
|------|-------|--------|
| 10:00:00 | Normal operations, all services healthy | System |
| 10:07:30 | Order processing batch jobs initiated | Backend logs |
| 10:07:35 | First batch completes (5 orders, 5.1s) | PostgreSQL logs |
| 10:08:00 | Connections begin accumulating (15→20) | PostgreSQL logs |
| 10:08:15 | Second batch starts, new connections opened | Backend logs |
| 10:08:30 | Third batch starts, connections at limit | Backend logs |
| 10:08:45 | Fourth batch starts, no connections available | Backend logs |
| **10:09:00** | **PostgreSQL rejects connections: "too many connections for role"** | **PostgreSQL logs** |
| 10:09:00 | Backend connection pool exhausted, retries begin | Backend logs |
| 10:09:07 | Max retries exceeded, service degraded | Backend logs |
| 10:09:07 - 10:10:59 | All API requests return 503 Service Unavailable | Nginx logs |
| 10:11:00 | Connection recovery mechanism triggers | Backend logs |
| 10:11:00 | 15 stale connections terminated | Backend logs |
| **10:11:01** | **Service restored, all requests return 200 OK** | **Backend logs** |

---

## Root Cause Analysis

### Primary Cause

**Database connection limit misconfiguration:** The PostgreSQL role `app` has a connection limit of 20, but the application's connection pool is configured with `max=20`. This creates zero headroom for concurrent operations.

### Contributing Factors

1. **Long-running transactions:** Order processing holds connections for ~5 seconds each with `SELECT ... FOR UPDATE`
2. **No connection timeout:** Idle connections not released automatically
3. **No circuit breaker:** Application continues retrying even when DB is unreachable
4. **Insufficient monitoring:** No alerts on connection pool utilization

### Evidence Chain

```
Order Processing (4 batches × 5 connections = 20)
         │
         ▼
PostgreSQL Connection Limit (20)
         │
         ▼
Connection Pool Exhausted (active=20, idle=0)
         │
         ▼
New Connections Rejected (FATAL: too many connections)
         │
         ▼
API Returns 503 (health check fails)
         │
         ▼
Users See Errors (150 requests affected)
```

---

## Impact Assessment

### Direct Impact

| Metric | Value | Normal | Degraded |
|--------|-------|--------|----------|
| Request Success Rate | 0% | 100% | 0% |
| Average Response Time | >30s (timeout) | 45ms | N/A |
| Error Rate | 100% | <0.1% | 100% |
| Affected Requests | ~150 | N/A | N/A |
| Affected Users | ~50 unique | N/A | N/A |

### Indirect Impact

- **Customer Trust:** Minor impact (internal tool)
- **Engineering Time:** ~2 hours investigation
- **On-call Response:** No escalation required (auto-recovered)
- **Downstream Services:** None affected

---

## What Went Well

1. **Automatic recovery:** The application's connection recovery mechanism worked as designed
2. **Clear logging:** All systems provided detailed logs for analysis
3. **No data loss:** Database transactions remained consistent
4. **Quick diagnosis:** Root cause identified within 30 minutes of incident

---

## What Went Wrong

1. **Connection limit too low:** 20 connections insufficient for expected load
2. **No connection pool monitoring:** Alert would have detected buildup
3. **No circuit breaker:** Application should fail fast when DB unavailable
4. **No load testing:** Issue not caught in staging
5. **No connection timeout:** Stale connections held indefinitely

---

## Action Items

| # | Action | Owner | Priority | Due Date | Status |
|---|--------|-------|----------|----------|--------|
| 1 | Increase PostgreSQL connection limit to 50 | DBA | High | Aug 28 | Pending |
| 2 | Reduce backend pool max to 15 | Dev | High | Aug 28 | Pending |
| 3 | Add connection idle timeout (30s) | Dev | High | Aug 30 | Pending |
| 4 | Implement circuit breaker pattern | Dev | Medium | Sep 5 | Pending |
| 5 | Add connection pool metrics to Prometheus | DevOps | High | Aug 30 | Pending |
| 6 | Create Grafana dashboard for DB connections | DevOps | Medium | Sep 1 | Pending |
| 7 | Optimize order processing queries | Dev | Medium | Sep 10 | Pending |
| 8 | Add query timeout (10s max) | Dev | Medium | Sep 5 | Pending |
| 9 | Load test with realistic traffic | QA | Medium | Sep 15 | Pending |
| 10 | Update incident response runbook | DevOps | Low | Sep 10 | Pending |

---

## Lessons Learned

1. **Connection pool size must be < database connection limit** - Always leave headroom for burst traffic
2. **Monitor connection state, not just count** - "idle in transaction" indicates potential leaks
3. **Implement circuit breakers** - Fail fast when dependent services are unavailable
4. **Test with realistic load** - This issue only occurs under sustained concurrent traffic
5. **Connection limits need headroom** - Plan for 20% above expected peak

---

## Technical Deep Dive

### The Bug

```python
# backend/app.py - Current implementation (problematic)
DB_POOL_CONFIG = {
    "min": 5,
    "max": 20,  # Matches PostgreSQL limit exactly
    "timeout": 30,  # No idle timeout
}

# Order processing holds connections for 5+ seconds
@app.route("/api/orders/process")
def process_orders():
    conn = get_conn()  # Acquires connection
    try:
        # Long-running transaction
        cursor.execute("SELECT * FROM orders WHERE status = 'pending' FOR UPDATE")
        time.sleep(5)  # Simulates processing
        cursor.execute("UPDATE orders SET status = 'processing' WHERE id IN (%s)", ids)
        conn.commit()
    finally:
        conn.close()  # Connection returned too slowly
```

### The Fix

```python
# backend/app.py - Fixed implementation
DB_POOL_CONFIG = {
    "min": 5,
    "max": 15,  # Leave headroom (15 < 20 limit)
    "timeout": 30,
    "idle_timeout": 30,  # Release idle connections
}

# Add circuit breaker
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def get_db_connection():
    return psycopg2.connect(DB_DSN, connect_timeout=3)

# Add query timeout
@app.route("/api/orders/process")
def process_orders():
    with get_db_connection() as conn:
        conn.cursor().execute("SET statement_timeout = '10s'")
        # ... rest of logic
```

### Infrastructure Changes

```hcl
# Increase PostgreSQL connection limit
resource "aws_rds_cluster" "main" {
  # ... existing config
  engine_parameters {
    name  = "max_connections"
    value = "50"
  }
}

# Add CloudWatch alarm for connection pool
resource "aws_cloudwatch_metric_alarm" "db_connections" {
  alarm_name          = "prod-db-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 40  # Alert at 80% of 50
  alarm_description   = "Database connections above threshold"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

---

## Appendix

### Raw Logs

- [PostgreSQL Logs](../exercise-1.4/logs/postgresql.log)
- [Backend Application Logs](../exercise-1.4/logs/backend-app.log)
- [Nginx Access Logs](../exercise-1.4/logs/nginx-access.log)

### Monitoring Queries

```promql
# Connection pool utilization
pg_stat_activity_count{role="app"}

# Connection state breakdown
pg_stat_activity_count{state="active"}
pg_stat_activity_count{state="idle"}
pg_stat_activity_count{state="idle in transaction"}

# API error rate
rate(http_requests_total{status=~"5.."}[1m])

# Database connection errors
rate(pg_stat_database_conflicts[5m])
```

### Related Documents

- [Incident Analysis](../exercise-1.4/analysis/incident-analysis.md)
- [Performance Optimization](../exercise-1.3/docs/performance-optimization.md)
- [Troubleshooting Guide](../exercise-1.3/docs/troubleshooting-guide.md)

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Incident Commander | | | |
| Engineering Lead | | | |
| Security Lead | | | |
| Product Owner | | | |

---

*Document Version: 1.0 | Last Updated: August 26, 2026*
