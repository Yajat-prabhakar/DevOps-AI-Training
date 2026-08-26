# Standard Operating Procedures (SOPs)

**Exercise 1.3** | Version: 1.0 | Last Updated: August 2026

---

## SOP-001: Emergency Production Rollback

**Purpose:** Quickly revert production to last known good state  
**When to Use:** Service degradation, failed deployment, critical bug  
**Time to Complete:** 5-10 minutes  
**Approval Required:** On-call engineer or Team Lead

### Pre-Conditions
- [ ] Incident has been declared
- [ ] Rollback decision made and communicated in #incident channel
- [ ] Previous task definition verified as stable

### Procedure

1. **Trigger rollback via GitHub Actions**
   ```bash
   # Option A: Via GitHub CLI
   gh workflow run rollback.yml \
     -f environment=production \
     -f service=all \
     -f reason="[INCIDENT-ID] Brief description"
   
   # Option B: Via AWS CLI (if GitHub unavailable)
   aws ecs update-service \
     --cluster production-cluster \
     --service backend-service \
     --task-definition <previous-task-def-arn> \
     --force-new-deployment
   ```

2. **Monitor deployment progress**
   ```bash
   aws ecs describe-services \
     --cluster production-cluster \
     --services backend-service frontend-service \
     --query 'services[*].{service:serviceName,status:status,desired:desiredCount,running:runningCount}'
   ```

3. **Verify health**
   ```bash
   curl -s https://example.com/api/health | jq .
   # Expected: {"service": "ok", "db": "ok"}
   ```

4. **Notify stakeholders**
   - Post in #incident: "Rollback completed. Service restored."
   - Update status page if applicable

### Post-Procedure
- [ ] Root cause analysis initiated
- [ ] Incident report filed within 24 hours
- [ ] Pipeline failure analyzed and fix scheduled

---

## SOP-002: Database Secret Rotation

**Purpose:** Rotate RDS credentials without downtime  
**When to Use:** Scheduled rotation (quarterly), suspected compromise  
**Time to Complete:** 30-60 minutes  
**Approval Required:** Team Lead + Security team

### Pre-Conditions
- [ ] New secret prepared in AWS Secrets Manager
- [ ] Application supports connection string refresh
- [ ] Maintenance window scheduled (if required)

### Procedure

1. **Create new secret version**
   ```bash
   aws secretsmanager update-secret \
     --secret-id /app/production/database \
     --secret-string '{"username":"app","password":"NEW_PASSWORD"}'
   ```

2. **Verify application can read new secret**
   ```bash
   # Check instance role permissions
   aws iam simulate-principal-policy \
     --policy-source-arn arn:aws:iam::ACCOUNT:role/prod-app-instance-role \
     --action-names secretsmanager:GetSecretValue \
     --resource-arns arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:/app/production/database-*
   ```

3. **Rotate on running instances (rolling)**
   ```bash
   # For ECS: force new deployment picks up new secret
   aws ecs update-service \
     --cluster production-cluster \
     --service backend-service \
     --force-new-deployment
   
   # Wait for stabilization
   aws ecs wait services-stable \
     --cluster production-cluster \
     --services backend-service
   ```

4. **Verify database connectivity**
   ```bash
   curl -s https://example.com/api/health
   # Confirm db status: "ok"
   
   # Check application logs for connection errors
   aws logs filter-log-events \
     --log-group-name /ecs/backend \
     --filter-pattern "ERROR" \
     --start-time $(date -d '5 minutes ago' +%s)000
   ```

5. **Deactivate old secret version**
   ```bash
   aws secretsmanager update-secret-version-stage \
     --secret-id /app/production/database \
     --version-stage AWSCURRENT \
     --move-to-version-id <new-version-id> \
     --remove-from-version-id <old-version-id>
   ```

---

## SOP-003: Blue/Green Deployment

**Purpose:** Deploy new version with zero-downtime and instant rollback  
**When to Use:** Major releases, high-risk changes  
**Time to Complete:** 45-90 minutes  
**Approval Required:** Team Lead + Product Owner

### Architecture

```
                    ┌─────────────────┐
                    │   ALB Listener  │
                    │  (Production)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
     │  Target     │ │  Target     │ │  Target     │
     │  Group:     │ │  Group:     │ │  Target:    │
     │  blue       │ │  green      │ │  canary     │
     │  (current)  │ │  (new)      │ │  (test)     │
     └─────────────┘ └─────────────┘ └─────────────┘
```

### Procedure

1. **Deploy new version to green target group**
   ```bash
   # Register new tasks in green TG
   aws ecs register-task-definition \
     --cli-input-json file://task-def-green.json
   
   # Update service to use new task definition
   aws ecs update-service \
     --cluster production-cluster \
     --service backend-service \
     --task-definition backend:GREEN \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
   ```

2. **Run validation against green**
   ```bash
   # Point test traffic to green
   curl -H "Host: test.example.com" https://alb-dns/api/health
   
   # Run integration test suite
   pytest integration/ -v --base-url=https://test.example.com
   ```

3. **Shift traffic to green**
   ```bash
   # Update ALB listener rules
   aws elbv2 modify-rule \
     --rule-arn <rule-arn> \
     --actions Type=forward,TargetGroupArn=<green-tg-arn>
   ```

4. **Monitor for 15 minutes**
   ```bash
   # Watch error rates
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ApplicationELB \
     --metric-name HTTPCode_Target_5XX_Count \
     --dimensions Name=TargetGroup,Value=targetgroup/green/xxx \
     --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 60 \
     --statistics Sum
   ```

5. **Cleanup old blue target group**
   ```bash
   # After validation period
   aws elbv2 delete-target-group \
     --target-group-arn <blue-tg-arn>
   ```

---

## SOP-004: Infrastructure Change Management

**Purpose:** Safe, auditable infrastructure modifications  
**When to Use:** Any Terraform/infrastructure change  
**Time to Complete:** Variable (depends on change scope)  
**Approval Required:** Varies by environment

### Change Categories

| Category | Examples | Approval Required |
|----------|----------|-------------------|
| **Standard** | Instance resize, tag updates | Peer review |
| **Normal** | New security group rules, SG changes | Team Lead |
| **Emergency** | Security patches, incident fixes | On-call + post-approval |

### Standard Change Process

1. **Create feature branch**
   ```bash
   git checkout -b infra/CHANGE-DESCRIPTION
   ```

2. **Make changes and validate locally**
   ```bash
   cd exercise-1.2
   terraform init
   terraform validate
   terraform fmt -check -recursive
   ```

3. **Create pull request**
   ```bash
   git add .
   git commit -m "infra: description of change"
   git push origin infra/CHANGE-DESCRIPTION
   ```

4. **Automated validation runs**
   - Terraform format check
   - Terraform validate
   - Security scanning (Trivy)

5. **Peer review and merge**
   - At least 1 approval required
   - All CI checks must pass
   - No merge conflicts

6. **Deploy via pipeline**
   - Merges to `main` trigger staging deployment
   - Production requires manual approval

### Emergency Change Process

1. **Declare emergency**
   ```bash
   # Post in #incident channel
   @on-call EMERGENCY: [Brief description]
   
   # Create incident ticket
   # Link to deployment: [pipeline-run-url]
   ```

2. **Apply directly to main** (skip PR review)
   ```bash
   # Commit directly
   git commit -am "EMERGENCY: [description]"
   git push origin main
   ```

3. **Create retroactive PR**
   ```bash
   # After incident resolved
   git checkout -b infra/emergency-fix-RETROACTIVE
   # Include documentation
   git commit -m "docs: retroactive documentation for emergency change"
   ```

4. **Complete post-incident review**
   - Within 24 hours
   - Root cause analysis
   - Process improvement items

---

## SOP-005: Monitoring & Alerting Setup

**Purpose:** Configure observability for new services  
**When to Use:** Adding new microservice or critical path  
**Time to Complete:** 2-4 hours  
**Approval Required:** Team Lead

### Prometheus Configuration

1. **Add scrape target**
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'new-service'
       metrics_path: '/metrics'
       static_configs:
         - targets: ['new-service:8080']
           labels:
             service: 'new-service'
             environment: '${ENV}'
   ```

2. **Create Grafana dashboard**
   ```json
   {
     "title": "New Service Dashboard",
     "panels": [
       {
         "title": "Request Rate",
         "type": "graph",
         "targets": [
           {
             "expr": "rate(http_requests_total{service=\"new-service\"}[5m])",
             "legendFormat": "{{method}} {{status}}"
           }
         ]
       }
     ]
   }
   ```

3. **Configure alerts**
   ```yaml
   # alertmanager.yml
   route:
     group_by: ['alertname', 'service']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 4h
     receiver: 'slack-critical'
   
   routes:
     - match:
         severity: critical
       receiver: 'pagerduty-critical'
   ```

### Alert Definitions

```yaml
# alerts.yml
groups:
  - name: new-service
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{service="new-service",status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on new-service"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service="new-service"}[5m])) > 1
        for: 10m
        labels:
          severity: warning
          
      - alert: ServiceDown
        expr: up{service="new-service"} == 0
        for: 1m
        labels:
          severity: critical
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Aug 2026 | DevOps Team | Initial SOPs |

### Review Schedule
- **Monthly:** Review SOP effectiveness and update as needed
- **Quarterly:** Full audit of all procedures
- **Post-Incident:** Update relevant SOPs after every incident
