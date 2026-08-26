# Security Remediation Plan

**Exercise 1.5** | Created: August 26, 2026 | Owner: Security Team

---

## Executive Summary

This remediation plan addresses all security findings identified in the security assessment. It prioritizes actions based on risk impact and implementation effort.

**Total Findings:** 24  
**Critical:** 4 | **High:** 8 | **Medium:** 9 | **Low:** 3

---

## Remediation Priority Matrix

```
                    HIGH IMPACT
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    │   MEDIUM EFFORT    │   LOW EFFORT       │
    │                    │                    │
    │  • Enable WAF      │  • Enable VPC      │
    │  • Automate IAM    │    Flow Logs       │
    │  • Incident Plan   │  • Enable MFA      │
    │                    │  • CloudTrail      │
    │                    │    validation      │
LOW ├────────────────────┼────────────────────┤ HIGH
EFFORT│                   │                    │ EFFORT
    │   HIGH EFFORT      │   MEDIUM EFFORT    │
    │                    │                    │
    │  • Transit GW      │  • Asset Inventory │
    │  • SCIM Provision  │  • Vendor Register │
    │  • Full RBAC Audit │  • Training Program│
    │                    │                    │
    └────────────────────┼────────────────────┘
                         │
                    LOW IMPACT
```

---

## Detailed Remediation Steps

### Finding 1: Overly Permissive IAM Policy

**Severity:** Critical  
**Framework:** SOC 2 CC6.1, ISO A.9.1.1  
**Risk:** Privilege escalation, data exfiltration

**Current State:**
```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

**Remediation:**

1. **Audit current usage** (1 day)
   ```bash
   # Check IAM Access Analyzer for unused permissions
   aws accessanalyzer list-findings --analyzer-arn <arn> \
     --filter '{"contains":{"field":"resource","value":"*"}}'
   
   # Analyze CloudTrail for actual API calls
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances \
     --max-results 100
   ```

2. **Create scoped policy** (2 days)
   - Review `policies/iam-policy-hardened.json`
   - Implement resource-level restrictions
   - Add condition keys for region, transport, time

3. **Test in staging** (1 day)
   ```bash
   # Simulate policy effects
   aws iam simulate-principal-policy \
     --policy-source-arn arn:iam::ACCOUNT:role/prod-app-role \
     --action-names s3:GetObject ec2:RunInstances \
     --resource-arns "arn:aws:s3:::app-production-data/*"
   ```

4. **Deploy to production** (1 day)
   - Use Terraform to update IAM policy
   - Monitor CloudTrail for denied API calls
   - Rollback plan ready

**Owner:** Security Team  
**Timeline:** 5 days  
**Status:** Pending

---

### Finding 2: Unrestricted Security Group Egress

**Severity:** High  
**Framework:** SOC 2 CC6.5, ISO A.13.1.1  
**Risk:** Data exfiltration, C2 communication

**Remediation:**

1. **Document current outbound dependencies** (1 day)
   ```bash
   # Capture current outbound traffic
   aws ec2 describe-network-interfaces \
     --filters "Name=group-id,Values=sg-xxx" \
     --query 'NetworkInterfaces[*].PrivateIpAddresses[*].Association'
   
   # Check VPC Flow Logs for outbound destinations
   aws logs filter-log-events \
     --log-group-name /aws/vpc/flow-log/prod \
     --filter-pattern "REJECT" \
     --start-time $(date -d '7 days ago' +%s)000
   ```

2. **Create restrictive egress rules** (2 days)
   - Allow HTTPS (443) to 0.0.0.0/0 for package updates
   - Allow DNS (53) to VPC resolver
   - Allow NTP (123) to AWS time sync
   - Allow PostgreSQL (5432) to DB tier only
   - Deny all other outbound

3. **Test connectivity** (1 day)
   ```bash
   # Verify application still works
   docker compose up --build
   curl http://localhost:5000/api/health
   
   # Verify package installation works
   docker compose exec backend pip install requests
   ```

4. **Deploy and monitor** (1 day)
   - Deploy to staging first
   - Monitor for 24 hours
   - Deploy to production

**Owner:** DevOps Team  
**Timeline:** 5 days  
**Status:** Pending

---

### Finding 3: No WAF on ALB

**Severity:** High  
**Framework:** SOC 2 CC7.1, ISO A.14.2.8  
**Risk:** OWASP Top 10 attacks, DDoS

**Remediation:**

1. **Enable AWS WAF v2** (1 day)
   ```bash
   # Create WAF Web ACL
   aws wafv2 create-web-acl \
     --name prod-alb-waf \
     --scope REGIONAL \
     --default-action Allow={} \
     --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=prod-waf
   ```

2. **Add managed rule groups** (1 day)
   - AWSManagedRulesCommonRuleSet
   - AWSManagedRulesSQLiRuleSet
   - AWSManagedRulesKnownBadInputsRuleSet
   - AWSManagedRulesPHPRuleSet (if applicable)

3. **Add rate limiting** (1 day)
   ```bash
   # Add rate-based rule
   aws wafv2 update-web-acl \
     --name prod-alb-waf \
     --scope REGIONAL \
     --rules '[{
       "Name": "RateLimit",
       "Priority": 1,
       "Statement": {
         "RateBasedStatement": {
           "Limit": 2000,
           "AggregateKeyType": "IP"
         }
       },
       "VisibilityConfig": {
         "SampledRequestsEnabled": true,
         "CloudWatchMetricsEnabled": true,
         "MetricName": "RateLimit"
       },
       "Action": {"Block": {}}
     }]'
   ```

4. **Associate with ALB** (1 hour)
   ```bash
   aws wafv2 associate-web-acl \
     --web-acl-arn <waf-arn> \
     --resource-arn <alb-arn>
   ```

**Owner:** DevOps Team  
**Timeline:** 3 days  
**Status:** Pending

---

### Finding 4: No Incident Response Plan

**Severity:** High  
**Framework:** SOC 2 CC7.3, ISO A.16.1.1  
**Risk:** Delayed incident response, increased damage

**Remediation:**

1. **Create incident response plan** (3 days)
   - Incident classification matrix
   - Response team roles and responsibilities
   - Communication templates
   - Escalation procedures
   - Evidence collection procedures

2. **Test with tabletop exercise** (1 day)
   - Simulate database compromise scenario
   - Test communication channels
   - Validate runbooks

3. **Integrate with monitoring** (1 day)
   - Connect Prometheus alerts to PagerDuty
   - Create Slack channel for incidents
   - Set up incident tracking

**Owner:** Security Team  
**Timeline:** 5 days  
**Status:** Pending

---

### Finding 5: Manual Access Revocation

**Severity:** High  
**Framework:** SOC 2 CC6.3, ISO A.9.2.5  
**Risk:** Orphaned accounts, delayed offboarding

**Remediation:**

1. **Implement SCIM provisioning** (2 weeks)
   ```bash
   # Enable SCIM in AWS IAM Identity Center
   aws sso-admin create-instance-access-control-attachment \
     --instance-arn <sso-arn> \
     --permission-set-arn <permission-set-arn> \
     --target-id <target-id>
   ```

2. **Integrate with HR system** (1 week)
   - Connect to HRIS for employee lifecycle events
   - Automate onboarding/offboarding

3. **Implement access reviews** (1 week)
   - Monthly access reviews
   - Quarterly privilege reviews

**Owner:** IT Team  
**Timeline:** 4 weeks  
**Status:** Pending

---

### Finding 6: No VPC Flow Logs

**Severity:** Medium  
**Framework:** SOC 2 CC4.1, ISO A.12.4.1  
**Risk:** Limited visibility into network traffic

**Remediation:**

```hcl
# Add to Terraform
resource "aws_flow_log" "main" {
  vpc_id                   = var.vpc_id
  traffic_type             = "ALL"
  log_destination_type     = "cloud-watch-logs"
  log_destination          = aws_cloudwatch_log_group.flow_log.arn
  iam_role_arn             = aws_iam_role.flow_log.arn
  max_aggregation_interval = 60
}

resource "aws_cloudwatch_log_group" "flow_log" {
  name              = "/aws/vpc/flow-log/${var.environment}"
  retention_in_days = 90
}

resource "aws_iam_role" "flow_log" {
  name = "${var.environment}-vpc-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "flow_log" {
  name = "${var.environment}-vpc-flow-log-policy"
  role = aws_iam_role.flow_log.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ]
      Resource = "*"
    }]
  })
}
```

**Owner:** DevOps Team  
**Timeline:** 2 days  
**Status:** Pending

---

### Finding 7: No Asset Inventory

**Severity:** Medium  
**Framework:** ISO A.8.1.1  
**Risk:** Unknown assets, incomplete risk assessment

**Remediation:**

1. **Enable AWS Config** (1 day)
   ```bash
   aws configservice put-configuration-recorder \
     --configuration-recorder name=main,roleARN=arn:aws:iam::ACCOUNT:role/aws-config-role \
     --recording-group allSupported=true,includeGlobalResourceTypes=true
   ```

2. **Create asset database** (1 week)
   - Import AWS Config data
   - Add CMDB integration
   - Assign asset owners

3. **Implement asset lifecycle** (1 week)
   - Tagging standards
   - Ownership assignment
   - Decommission procedures

**Owner:** IT Team  
**Timeline:** 2 weeks  
**Status:** Pending

---

## Tracking

| # | Finding | Severity | Owner | Timeline | Status |
|---|---------|----------|-------|----------|--------|
| 1 | Overly permissive IAM | Critical | Security | 5 days | Pending |
| 2 | Unrestricted egress | High | DevOps | 5 days | Pending |
| 3 | No WAF | High | DevOps | 3 days | Pending |
| 4 | No incident response | High | Security | 5 days | Pending |
| 5 | Manual access revocation | High | IT | 4 weeks | Pending |
| 6 | No VPC Flow Logs | Medium | DevOps | 2 days | Pending |
| 7 | No asset inventory | Medium | IT | 2 weeks | Pending |

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Security findings | 24 | < 5 | Monthly scan |
| Mean time to remediate | N/A | 7 days | Ticket system |
| IAM policy coverage | Wildcard | 100% scoped | IAM Access Analyzer |
| WAF blocked requests | 0 | > 99% malicious | WAF metrics |
| Incident response time | Unknown | < 30 min | PagerDuty |
| Access review completion | 0% | 100% quarterly | IAM reports |
