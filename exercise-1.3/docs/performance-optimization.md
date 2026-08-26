# Performance Optimization Recommendations

**Exercise 1.3** | Version: 1.0 | Last Updated: August 2026

---

## Executive Summary

This document identifies optimization opportunities across the CI/CD pipeline, application infrastructure, and deployment processes. Implementing these recommendations can reduce pipeline duration by 40-60% and infrastructure costs by 25-35%.

---

## 1. Pipeline Performance Optimization

### Current State Analysis

| Stage | Current Duration | Bottleneck |
|-------|------------------|------------|
| Lint & Scan | 3-4 min | Trivy full filesystem scan |
| Backend Tests | 5-7 min | DB setup, no parallelization |
| Frontend Tests | 4-6 min | Full npm install |
| Docker Build | 8-12 min | No layer caching |
| Terraform Validate | 3-5 min | Full init on every run |
| Deploy Staging | 5-8 min | Sequential services |
| **Total** | **28-42 min** | |

### Optimization 1: Parallelize Independent Stages

**Impact:** -8 minutes (20% reduction)

```yaml
# Current: Sequential
jobs:
  lint-and-scan:
  test-backend:
    needs: [lint-and-scan]  # Waits unnecessarily
  test-frontend:
    needs: [lint-and-scan]  # Waits unnecessarily

# Optimized: Parallel where possible
jobs:
  lint-and-scan:
  test-backend:  # Runs immediately
  test-frontend:  # Runs immediately
  terraform-validate:  # Runs immediately
```

### Optimization 2: Docker Layer Caching

**Impact:** -5 minutes (15% reduction)

```yaml
# In build job
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push backend image
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    push: true
    tags: ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY_BACKEND }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Alternative: AWS ECR Cache**
```yaml
- name: Build with ECR cache
  run: |
    # Pull previous image as cache
    docker pull $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest || true
    
    docker build \
      --cache-from $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest \
      --build-arg BUILDKIT_INLINE_CACHE=1 \
      -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG .
```

### Optimization 3: Dependency Caching

**Impact:** -3 minutes (10% reduction)

```yaml
# Backend: Cache pip dependencies
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

# Frontend: Cache npm
- name: Cache npm
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('frontend/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Optimization 4: Incremental Terraform

**Impact:** -2 minutes (5% reduction)

```yaml
- name: Terraform Plan (targeted)
  run: |
    cd exercise-1.2
    # Only validate changed modules
    CHANGED_FILES=$(git diff --name-only HEAD~1 -- exercise-1.2/)
    
    if echo "$CHANGED_FILES" | grep -q "modules/alb"; then
      terraform plan -target=module.alb_primary
    else
      terraform plan
    fi
```

---

## 2. Infrastructure Cost Optimization

### Current Resource Allocation

| Resource | Configuration | Monthly Cost (est.) |
|----------|---------------|---------------------|
| EC2 (ASG) | t3.large x 2 | $120 |
| RDS | db.t3.large Multi-AZ | $180 |
| ALB | Application LB | $25 |
| NAT Gateway | Single AZ | $45 |
| CloudWatch | Logs + Metrics | $30 |
| **Total** | | **~$400/month** |

### Recommendation 1: Right-Size Instances

**Impact:** -30% compute cost

```hcl
# Before
instance_type = "t3.large"  # 2 vCPU, 8GB

# After (check actual utilization first)
instance_type = "t3.medium"  # 2 vCPU, 4GB (if memory usage < 50%)
```

**Verification:**
```bash
# Check EC2 utilization over 30 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxx \
  --start-time $(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average Maximum
```

### Recommendation 2: Reserved Instances / Savings Plans

**Impact:** -40% on EC2, -30% on RDS

```bash
# Compute Savings Plan (1-year, no upfront)
aws savingsplans describe-savings-plans-offering \
  --offering-type Ec2Instance \
  --payment-option NoUpfront \
  --term-duration-seconds 31536000

# RDS Reserved Instance
aws rds describe-reserved-db-instances-offerings \
  --db-instance-class db.t3.large \
  --duration 1yr \
  --product-description mysql
```

### Recommendation 3: NAT Gateway Optimization

**Impact:** -40% networking cost

```hcl
# Current: NAT Gateway in each AZ
resource "aws_nat_gateway" "az1" { ... }
resource "aws_nat_gateway" "az2" { ... }  # $45/month extra

# Optimized: Single NAT Gateway (for non-prod)
resource "aws_nat_gateway" "main" {
  count         = var.environment == "prod" ? 2 : 1
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = var.public_subnet_ids[count.index]
}
```

### Recommendation 4: Scheduled Scaling

**Impact:** -20% on compute (dev/staging)

```hcl
# Scale down non-prod outside business hours
resource "aws_autoscaling_schedule" "scale_down_evening" {
  scheduled_action_name  = "scale-down-evening"
  min_size              = 0
  max_size              = 1
  desired_capacity      = 0
  recurrence            = "0 20 * * 1-5"  # 8 PM weekdays
  
  autoscaling_group_name = aws_autoscaling_group.staging.name
}

resource "aws_autoscaling_schedule" "scale_up_morning" {
  scheduled_action_name  = "scale-up-morning"
  min_size              = 1
  max_size              = 3
  desired_capacity      = 1
  recurrence            = "0 8 * * 1-5"  # 8 AM weekdays
  
  autoscaling_group_name = aws_autoscaling_group.staging.name
}
```

---

## 3. Application Performance Optimization

### Database Connection Pooling

**Current:** New connection per request  
**Optimized:** Connection pool with PgBouncer

```hcl
# Add to docker-compose.yml
services:
  pgbouncer:
    image: edoburu/pgbouncer:1.21.0
    environment:
      DATABASE_URL: postgresql://app:app@postgres:5432/appdb
      POOL_MODE: transaction
      DEFAULT_POOL_SIZE: 20
      MAX_CLIENT_CONN: 100
    ports:
      - "5432:5432"
    depends_on:
      postgres:
        condition: service_healthy
```

### Redis Caching Layer

```hcl
# Add to docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

**Application integration:**
```python
# backend/app.py
import redis
from flask import Flask

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route("/api/hello")
def hello():
    cached = cache.get("hello_response")
    if cached:
        return jsonify(json.loads(cached))
    
    response = {"message": "Hello from the Flask API", "ts": time.time()}
    cache.setex("hello_response", 60, json.dumps(response))
    return jsonify(response)
```

### Response Compression

```python
# backend/app.py
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Enables gzip compression

# Or via Nginx
```

```nginx
# frontend/nginx.conf
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml;
```

---

## 4. Monitoring & Observability Optimization

### Prometheus Query Optimization

```yaml
# Before: Expensive range query
- expr: rate(http_requests_total[5m])

# After: Pre-aggregated recording rule
groups:
  - name: http_aggregates
    rules:
      - record: http_request_rate:5m
        expr: rate(http_requests_total[5m])
      
      - record: http_error_rate:5m
        expr: rate(http_requests_total{status=~"5.."}[5m])
```

### Log Retention Optimization

```hcl
# Current: 90 days retention for all logs
resource "aws_cloudwatch_log_group" "app" {
  retention_in_days = 90
}

# Optimized: Tiered retention
resource "aws_cloudwatch_log_group" "app" {
  retention_in_days = var.environment == "prod" ? 90 : 30
}

# Archive old logs to S3
resource "aws_cloudwatch_log_subscription_filter" "archive" {
  name            = "archive-old-logs"
  log_group_name  = aws_cloudwatch_log_group.app.name
  filter_pattern  = ""
  destination_arn = aws_kinesis_firehose_delivery_stream.archive.arn
}
```

### Alert Fatigue Reduction

```yaml
# Before: Too many alerts
groups:
  - name: noisy
    rules:
      - alert: HighCPU
        expr: cpu > 80  # Fires constantly
      - alert: HighMemory
        expr: memory > 85  # Fires constantly

# After: Meaningful alerts with proper thresholds and duration
groups:
  - name: actionable
    rules:
      - alert: SustainedHighCPU
        expr: avg_over_time(cpu[5m]) > 85
        for: 15m  # Only fires after sustained period
        labels:
          severity: warning
        
      - alert: CriticalMemory
        expr: memory > 95
        for: 5m
        labels:
          severity: critical
```

---

## 5. Implementation Roadmap

| Phase | Timeline | Actions | Expected Impact |
|-------|----------|---------|-----------------|
| **Quick Wins** | Week 1 | Dependency caching, parallel jobs | -8 min pipeline |
| **Infrastructure** | Week 2-3 | Right-sizing, Savings Plans | -30% cost |
| **Application** | Week 3-4 | Caching layer, compression | -50% latency |
| **Monitoring** | Week 4-5 | Recording rules, alert tuning | -60% alert noise |
| **Optimization** | Week 6-8 | Scheduled scaling, log tiering | -25% total cost |

---

## Metrics & Success Criteria

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Pipeline Duration | 35 min | 15 min | GitHub Actions analytics |
| Monthly Cost | $400 | $280 | AWS Cost Explorer |
| P95 Latency | 450ms | 200ms | Grafana dashboard |
| Alert Volume | 50/day | 10/day | Alertmanager stats |
| Deployment Frequency | 2/week | Daily | GitHub releases |

---

## Appendix: Cost Estimation Tools

```bash
# AWS Pricing API
aws pricing get-products \
  --service-code AmazonEC2 \
  --filters "InstanceType=t3.large" "Location=US East (N. Virginia)"

# Terraform cost estimation
pip install tfcost
tfcost breakdown

# Infracost (CI integration)
infracost breakdown --path exercise-1.2
```
