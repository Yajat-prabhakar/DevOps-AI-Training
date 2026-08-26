# Incident Response Playbook

**Exercise 1.6** | Version: 1.0 | Last Updated: August 2026

---

## Purpose

This playbook provides step-by-step procedures for responding to incidents in our production environment. It is designed to minimize impact, ensure rapid recovery, and capture necessary information for post-incident analysis.

---

## Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| **P1 - Critical** | Service completely down, data loss, security breach | 15 minutes | Complete outage, database corruption |
| **P2 - Major** | Significant degradation, partial outage | 30 minutes | High error rate, slow response times |
| **P3 - Minor** | Limited impact, workarounds available | 2 hours | Single feature broken, non-critical errors |
| **P4 - Low** | Minimal impact, cosmetic issues | Next business day | UI bugs, minor performance issues |

---

## Incident Response Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INCIDENT RESPONSE WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │  DETECT   │───▶│  ASSESS  │───▶│RESPOND   │───▶│RECOVER   │            │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│       │               │               │               │                    │
│       ▼               ▼               ▼               ▼                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Alert    │    │ Severity │    │ Mitigate │    │ Verify   │            │
│  │ Ack      │    │ Classify │    │ Fix      │    │ Monitor  │            │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│                                                                             │
│                                    │                                       │
│                                    ▼                                       │
│                             ┌──────────┐                                   │
│                             │ POST-    │                                   │
│                             │ INCIDENT │                                   │
│                             └──────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Detection & Acknowledgment

### Step 1.1: Alert Received

**Check monitoring dashboards:**
- Grafana: https://grafana.example.com
- CloudWatch: AWS Console → CloudWatch → Alarms
- PagerDuty: https://app.pagerduty.com

**Acknowledge the alert:**
```bash
# Via PagerDuty CLI
pd incident acknowledge --incident <incident-id>

# Via Slack
/incidents acknowledge <incident-id>
```

### Step 1.2: Initial Assessment (5 minutes)

```bash
# Quick health check
curl -s https://example.com/api/health | jq .

# Check service status
aws ecs describe-services \
  --cluster production-cluster \
  --services backend-service frontend-service \
  --query 'services[*].{service:serviceName,status:status,running:runningCount,desired:desiredCount}'

# Check recent deployments
gh run list --workflow=ci-cd.yml --limit=5 --json status,conclusion,headBranch

# Check database status
aws rds describe-db-instances \
  --db-instance-identifier prod-db \
  --query 'DBInstances[0].{status:DBInstanceStatus,engine:Engine,version:EngineVersion}'
```

### Step 1.3: Declare Incident

**Post in #incident channel:**
```
🚨 INCIDENT DECLARED

Severity: P2
Service: Backend API
Impact: 503 errors on /api/*
Started: 2026-08-26 10:09 UTC
Incident Commander: @your-name
Status: Investigating

Updates will be posted every 15 minutes.
```

---

## Phase 2: Assessment & Classification

### Step 2.1: Determine Scope

**Questions to answer:**
- Which services are affected?
- Which users/regions are impacted?
- Is there data loss or corruption?
- Is this a security incident?

**Checklists:**

| Check | Command | Expected |
|-------|---------|----------|
| API Health | `curl -s https://example.com/api/health` | 200 OK |
| Database | `aws rds describe-db-instances` | Available |
| ECS Tasks | `aws ecs list-tasks --cluster prod` | Running |
| ALB Targets | `aws elbv2 describe-target-health` | Healthy |
| Error Rate | Grafana dashboard | < 1% |

### Step 2.2: Classify Severity

Use the severity matrix to classify the incident:

```
IMPACT
  ▲
  │
  │  P1  │  P2  │  P2  │
  │──────┼──────┼──────┤
  │  P2  │  P2  │  P3  │
  │──────┼──────┼──────┤
  │  P2  │  P3  │  P3  │
  └──────────────────────▶ SCOPE
       Low   Med   High
```

---

## Phase 3: Response

### Step 3.1: Mitigation Strategies

**For Database Issues:**
```bash
# Check connection count
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average

# If connections exhausted, restart application
aws ecs update-service \
  --cluster production-cluster \
  --service backend-service \
  --force-new-deployment
```

**For Application Issues:**
```bash
# Check stopped tasks
aws ecs describe-tasks \
  --cluster production-cluster \
  --tasks $(aws ecs list-tasks --cluster production-cluster --desired-status STOPPED --query 'taskArns[:5]' --output text)

# View task logs
aws logs get-log-events \
  --log-group-name /ecs/backend \
  --log-stream-name <stream-name> \
  --limit 50
```

**For Infrastructure Issues:**
```bash
# Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn <tg-arn>

# Check security groups
aws ec2 describe-security-groups \
  --group-ids <sg-id> \
  --query 'SecurityGroups[0].IpPermissions'

# Check network ACLs
aws ec2 describe-network-acls \
  --filters Name=vpc-id,Values=<vpc-id>
```

### Step 3.2: Communication Updates

**Every 15 minutes, update #incident channel:**
```
📊 UPDATE #1 (10:15 UTC)

Status: Investigating
Impact: Continuing - 503 errors on API
Actions Taken:
- Identified database connection pool exhaustion
- Restarting application service
Next Update: 10:30 UTC
```

### Step 3.3: Escalation

**When to escalate:**
- Root cause not identified within 30 minutes
- Issue requires changes outside your authority
- Multiple services affected
- Data loss suspected

**Who to escalate to:**
- P1: Engineering Lead + VP Engineering
- P2: Engineering Lead
- P3: On-call Team Lead

---

## Phase 4: Recovery

### Step 4.1: Verify Fix

```bash
# Health check
curl -s https://example.com/api/health | jq .
# Expected: {"service": "ok", "db": "ok"}

# Error rate
# Grafana: Rate of 5xx errors should be < 0.1%

# Response time
# Grafana: P95 latency should be < 500ms

# User verification
# Check #support channel for user reports
```

### Step 4.2: Monitor for Regression

**Monitor for 30 minutes after fix:**
- Error rates
- Response times
- Resource utilization
- User reports

### Step 4.3: Close Incident

**Post in #incident channel:**
```
✅ INCIDENT RESOLVED

Incident ID: INC-2026-0826-001
Duration: 12 minutes
Resolution: Application restarted, connection pool cleared
Root Cause: Database connection limit exhausted
Status: Monitoring

Post-mortem scheduled for: 2026-08-27 10:00 UTC
```

---

## Phase 5: Post-Incident

### Step 5.1: Gather Data

```bash
# Collect all logs
mkdir -p /tmp/incident-$(date +%Y%m%d)

# Application logs
aws logs filter-log-events \
  --log-group-name /ecs/backend \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000 \
  --output file:///tmp/incident-$(date +%Y%m%d)/backend.json

# Database logs
aws rds download-db-log-file-portion \
  --db-instance-identifier prod-db \
  --log-file-name error/postgresql.log \
  --marker 0 \
  --output file:///tmp/incident-$(date +%Y%m%d)/db-error.log

# ALB access logs
aws logs filter-log-events \
  --log-group-name /aws/application-lb/access \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "503" \
  --output file:///tmp/incident-$(date +%Y%m%d)/alb-503.json
```

### Step 5.2: Create Post-Mortem

**Template:** See [incident-postmortem.md](./incident-postmortem.md)

**Schedule post-mortem meeting:**
- Within 48 hours of incident
- Invite: Incident Commander, responders, stakeholders
- Duration: 60 minutes

### Step 5.3: Track Action Items

```bash
# Create JIRA tickets for action items
# Link to incident: INC-2026-0826-001
# Assign owners and due dates
# Review in next sprint planning
```

---

## Runbooks

### Runbook: Database Connection Exhaustion

**Symptoms:**
- 503 errors on API endpoints
- "too many connections" in PostgreSQL logs
- Connection pool exhausted in application logs

**Immediate Actions:**
1. Check current connection count
2. Identify long-running queries
3. Terminate stuck connections if safe
4. Restart application if needed

**Commands:**
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE usename = 'app';

-- Find long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Terminate specific connection
SELECT pg_terminate_backend(<pid>);
```

**Prevention:**
- Set connection pool max < database connection limit
- Add connection idle timeout
- Implement circuit breaker pattern

---

### Runbook: High Error Rate

**Symptoms:**
- Error rate > 5% on Grafana
- 5xx responses in access logs
- User reports of errors

**Immediate Actions:**
1. Check application logs for errors
2. Verify database connectivity
3. Check for recent deployments
4. Review resource utilization

**Commands:**
```bash
# Check application logs
aws logs tail /ecs/backend --since 15m --filter-pattern "ERROR"

# Check for recent changes
gh run list --workflow=ci-cd.yml --limit=3

# Check resource utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=production-cluster \
  --period 60 \
  --statistics Average
```

---

### Runbook: Service Down

**Symptoms:**
- Health check failing
- All requests timing out
- ECS tasks not running

**Immediate Actions:**
1. Check ECS service status
2. Review stopped tasks
3. Check for deployment failures
4. Verify load balancer health

**Commands:**
```bash
# Check ECS service
aws ecs describe-services \
  --cluster production-cluster \
  --services backend-service

# Check stopped tasks
aws ecs list-tasks \
  --cluster production-cluster \
  --desired-status STOPPED

# Force new deployment
aws ecs update-service \
  --cluster production-cluster \
  --service backend-service \
  --force-new-deployment
```

---

## Quick Reference

### Key Contacts

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Incident Commander | [Name] | [Phone] | @name |
| On-Call Engineer | [Name] | [Phone] | @name |
| Engineering Lead | [Name] | [Phone] | @name |
| DBA | [Name] | [Phone] | @name |
| Security | [Name] | [Phone] | @name |

### Key Services

| Service | URL | Health Check |
|---------|-----|--------------|
| API | https://example.com | /api/health |
| Grafana | https://grafana.example.com | /api/health |
| PagerDuty | https://app.pagerduty.com | N/A |
| GitHub | https://github.com/org | N/A |

### Emergency Commands

```bash
# Emergency rollback
gh workflow run rollback.yml -f environment=production -f service=all -f reason="INC-XXX"

# Force ECS deployment
aws ecs update-service --cluster prod --service backend --force-new-deployment

# Restart RDS
aws rds reboot-db-instance --db-instance-identifier prod-db

# Scale up ASG
aws autoscaling set-desired-capacity --auto-scaling-group-name prod-asg --desired-capacity 5
```
