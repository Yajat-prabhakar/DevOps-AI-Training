# CI/CD Pipeline Troubleshooting Guide

**Exercise 1.3** | Version: 1.0 | Last Updated: August 2026

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Common Failures & Fixes](#common-failures--fixes)
3. [Stage-Specific Troubleshooting](#stage-specific-troubleshooting)
4. [Infrastructure Issues](#infrastructure-issues)
5. [Debug Commands Reference](#debug-commands-reference)

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CI/CD PIPELINE FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │  Lint &   │───▶│  Test    │───▶│  Test    │───▶│  Build   │                 │
│  │  Scan     │    │ Backend  │    │ Frontend │    │  Docker  │                 │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘                 │
│                                                              │                  │
│                                                              ▼                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │  Deploy   │◀──│Integration│◀──│  Deploy  │◀──│Terraform │                 │
│  │Production │    │  Tests   │    │ Staging  │    │ Validate │                 │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Pipeline Duration:** ~15-25 minutes (full run)  
**Trigger Conditions:** Push to `main`/`develop`, PRs to `main`, manual dispatch

---

## Common Failures & Fixes

### 1. AWS Credentials Error

**Symptoms:**
```
Error: Unable to locate credentials
Error: role-to-assume: AccessDenied
```

**Root Cause:** OIDC federation misconfigured or secret missing.

**Fix:**
```bash
# Verify GitHub OIDC provider exists in AWS
aws iam list-open-id-connect-providers

# Verify the role trust policy allows your repo
aws iam get-role --role-name YourRoleName --query 'Role.AssumeRolePolicyDocument'

# Required trust policy condition:
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:ref:refs/heads/main"
    }
  }
}
```

**Prevention:** Store `AWS_ROLE_ARN` in GitHub repository secrets.

---

### 2. Docker Build Fails

**Symptoms:**
```
error: failed to solve: dockerfile parse error
ERROR: executor failed running
```

**Root Cause:** Invalid Dockerfile syntax or missing build context.

**Fix:**
```bash
# Test Docker build locally
cd backend
docker build -t test-backend .

# Common issues:
# 1. Missing .dockerignore (large context causes timeout)
# 2. Multi-stage build syntax errors
# 3. COPY paths incorrect

# Validate Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile
```

---

### 3. ECR Push Rejected

**Symptoms:**
```
name unknown: The repository with name 'xxx' does not exist
unauthorized: authentication required
```

**Fix:**
```bash
# Ensure ECR repositories exist
aws ecr describe-repositories --repository-names app-backend app-frontend

# Create if missing
aws ecr create-repository --repository-name app-backend
aws ecr create-repository --repository-name app-frontend

# Set lifecycle policy to prevent unbounded storage growth
aws ecr put-lifecycle-policy \
  --repository-name app-backend \
  --lifecycle-policy-text '{"rules":[{"rulePriority":1,"selection":{"tagStatus":"untagged","countType":"sinceImagePushed","countUnit":"days","countNumber":7},"action":{"type":"expire"}}]}'
```

---

### 4. Terraform Init/Apply Fails

**Symptoms:**
```
Error: Backend configuration changed
Error: Resource already exists
Error: Error acquiring the state lock
```

**Fix:**
```bash
# State lock issue
aws dynamodb delete-item \
  --table-name terraform-lock \
  --key '{"LockID":{"S":"your-state-key"}}'

# Backend mismatch - reinitialize
terraform init -migrate-state

# Resource exists outside Terraform
terraform import aws_instance.example i-1234567890abcdef0
```

---

### 5. ECS Service Deployment Stuck

**Symptoms:**
```
service failed to stabilize: 1/2 tasks running
task stopped: Essential container exited with code 1
```

**Fix:**
```bash
# Check stopped tasks for errors
aws ecs describe-services \
  --cluster production-cluster \
  --services backend-service \
  --query 'services[0].events[:10]'

# View stopped task logs
aws logs get-log-events \
  --log-group-name /ecs/backend \
  --log-stream-name <stream-name>

# Common causes:
# 1. Health check failures (increase interval/timeout)
# 2. Memory limits too low (increase task memory)
# 3. Environment variables missing
# 4. Database connection string incorrect
```

---

## Stage-Specific Troubleshooting

### Stage: Lint & Scan

| Error | Cause | Fix |
|-------|-------|-----|
| `hadolint: DL3008` | Pin versions in apt-get | Use `apt-get install -y package=version` |
| `yamllint: syntax error` | Invalid YAML | Check indentation (2 spaces) |
| `Trivy: CRITICAL vulnerability` | Package has CVE | Update package or add `.trivyignore` |

**Trivy false positive suppression:**
```yaml
# .trivyignore
CVE-2024-XXXXX  # No risk in container context
```

---

### Stage: Backend Tests

| Error | Cause | Fix |
|-------|-------|-----|
| `psycopg2.OperationalError` | DB not reachable | Check service container health |
| `ModuleNotFoundError` | Missing dependency | Verify `requirements.txt` |
| `Connection refused` | Port conflict | Check `ports` mapping |

**Test locally with service containers:**
```bash
# Run PostgreSQL container for local testing
docker run -d --name test-db \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  postgres:16-alpine

# Run tests
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/testdb \
  pytest --cov=. -v

# Cleanup
docker rm -f test-db
```

---

### Stage: Frontend Tests

| Error | Cause | Fix |
|-------|-------|-----|
| `npm ERR! peer dep` | Version mismatch | Use `npm install --legacy-peer-deps` |
| `Out of memory` | Large bundle | Increase Node memory: `NODE_OPTIONS=--max_old_space_size=4096` |
| `TypeScript error` | Type mismatch | Run `tsc --noEmit` to identify |

---

### Stage: Terraform Validation

| Error | Cause | Fix |
|-------|-------|-----|
| `Error: Backend config changed` | Different backend config | Re-run `terraform init` |
| `Error: Provider config not present` | Missing provider alias | Check `providers.tf` aliases |
| `Error: Cycle in resource deps` | Circular dependency | Refactor resource references |

**Check for drift:**
```bash
terraform plan -detailed-exitcode
# Exit code 2 = changes detected (drift)
```

---

## Infrastructure Issues

### RDS Connection Failures

**Symptoms:** Backend health check returns `db: unreachable`

**Diagnosis:**
```bash
# Check security group rules
aws ec2 describe-security-groups \
  --group-ids $(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=prod-db-sg" \
    --query 'SecurityGroups[0].GroupId' --output text) \
  --query 'SecurityGroups[0].IpPermissions'

# Test connectivity from EC2
aws ssm start-session --target i-1234567890abcdef0
nc -zv <rds-endpoint> 5432
```

**Common Fixes:**
1. DB subnet group missing private subnets
2. Security group ingress rule missing app SG reference
3. RDS in different VPC than app tier
4. `publicly_accessible = true` but should be `false`

---

### ALB Target Group Unhealthy

**Diagnosis:**
```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/xxx

# Check ALB access logs
aws s3 ls s3://alb-logs-bucket/AWSLogs/ACCOUNT/elasticloadbalancing/ --recursive
```

**Fix:**
```hcl
# Ensure health check matches app endpoint
health_check {
  path                = "/api/health"
  healthy_threshold   = 2
  unhealthy_threshold = 3
  timeout             = 5
  interval            = 30
  matcher             = "200"
}
```

---

## Debug Commands Reference

### Quick Diagnostics

```bash
# Pipeline status
gh run list --workflow=ci-cd.yml --limit=5

# Detailed run logs
gh run view <run-id> --log

# Download artifacts
gh run download <run-id> --name tfplan-staging

# Re-run failed jobs
gh run rerun <run-id> --failed

# Cancel running pipeline
gh run cancel <run-id>
```

### AWS Debugging

```bash
# ECR image list
aws ecr describe-images --repository-name app-backend --query 'sort_by(imageDetails,&imagePushedAt)[-5:]'

# ECS service events (last 10)
aws ecs describe-services --cluster prod-cluster --services backend-service \
  --query 'services[0].events[:10].{time:createdAt,message:message}'

# ECS task logs
aws logs tail /ecs/backend --since 1h --follow

# RDS slow query log
aws rds describe-db-log-files --db-instance-identifier prod-db \
  --query 'DescribeDBLogFiles[?LogFileName.contains(@,`slowquery`)]'

# ALB access logs analysis
aws logs start-query \
  --log-group-name /aws/application-lb/access-logs \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, elb.status_code, target.status_code | filter elb.status_code = 502'
```

### Local Debugging

```bash
# Test pipeline locally with act
act -j test-backend --secret-file .secrets

# Build and run locally
docker compose -f docker-compose.prod.yml up --build

# Check container logs
docker compose logs -f backend

# Enter running container
docker compose exec backend /bin/sh

# Check environment variables
docker compose exec backend env | grep DATABASE
```

---

## Escalation Path

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Production down | 15 minutes | On-call + Engineering Lead |
| Staging broken | 2 hours | DevOps team |
| Flaky test | 1 week | Engineering team |
| Minor lint warning | Next sprint | Assigned developer |

---

## Appendix: Useful Links

- [GitHub Actions Troubleshooting](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
- [AWS ECS Troubleshooting](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/troubleshooting.html)
- [Terraform State Management](https://developer.hashicorp.com/terraform/language/state)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
