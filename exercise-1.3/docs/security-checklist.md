# Security Checklist & Compliance Documentation

**Exercise 1.3** | Version: 1.0 | Last Updated: August 2026

---

## CI/CD Pipeline Security Checklist

### Pre-Commit Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | No secrets in code (API keys, passwords, tokens) | ☐ | Use `git-secrets` or `truffleHog` |
| 2 | No hardcoded endpoints with credentials | ☐ | Environment variables only |
| 3 | `.env` files in `.gitignore` | ☐ | Never commit environment files |
| 4 | Dependencies audited (`npm audit`, `pip-audit`) | ☐ | No critical/high CVEs |
| 5 | Docker images from verified publishers only | ☐ | Pin digests for production |

### Repository Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 6 | Branch protection on `main` | ☐ | Require PR reviews |
| 7 | Signed commits enabled | ☐ | GPG or SSH signing |
| 8 | CODEOWNERS file defined | ☐ | Auto-assign reviewers |
| 9 | Dependabot/Renovate enabled | ☐ | Auto-update dependencies |
| 10 | Secret scanning enabled | ☐ | GitHub Advanced Security |

### CI/CD Pipeline Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 11 | Secrets stored in GitHub Secrets, not workflow files | ☐ | `secrets.GITHUB_TOKEN` |
| 12 | OIDC federation for AWS (no long-lived keys) | ☐ | `role-to-assume` |
| 13 | Least privilege for pipeline IAM role | ☐ | Minimal permissions |
| 14 | Artifact scanning before deployment | ☐ | Trivy, Snyk, or Grype |
| 15 | Signed container images | ☐ | Cosign or Notary |

### Infrastructure Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 16 | Terraform state encrypted at rest | ☐ | S3 + DynamoDB lock |
| 17 | No public S3 buckets | ☐ | Block public access |
| 18 | RDS not publicly accessible | ☐ | Private subnets only |
| 19 | Security groups follow least privilege | ☐ | No `0.0.0.0/0` on private |
| 20 | VPC Flow Logs enabled | ☐ | Network monitoring |

### Runtime Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 21 | Container runs as non-root | ☐ | `USER` in Dockerfile |
| 22 | Read-only filesystem where possible | ☐ | `read_only: true` |
| 23 | Resource limits defined | ☐ | CPU, memory, PIDs |
| 24 | Network policies (K8s) or container networking | ☐ | Isolation between services |
| 25 | Secrets injected at runtime, not baked in | ☐ | ECS task role, not env vars |

---

## AWS IAM Policy Review

### Current IAM Configuration

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsRead",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:/app/production/database-*"
      ]
    }
  ]
}
```

### Security Findings

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | ✅ Low | Secrets policy scoped to specific ARN | No change needed |
| 2 | ⚠️ Medium | CloudWatch agent policy attached to instance role | Verify it's the managed policy only |
| 3 | ⚠️ Medium | SSM managed instance policy attached | Ensure no SSM Parameter Store write access |
| 4 | 🔴 High | No condition keys on secrets access | Add `aws:RequestedRegion` condition |
| 5 | ⚠️ Medium | No boundary policy | Add permission boundary to limit blast radius |

### Recommended IAM Improvements

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsReadScoped",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:/app/production/database-*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        },
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

---

## Security Group Audit

### Current Configuration

```hcl
# ALB Security Group - Internet Facing
ingress {
  from_port   = 80
  to_port     = 80
  cidr_blocks = ["0.0.0.0/0"]  # Open to world
}

ingress {
  from_port   = 443
  to_port     = 443
  cidr_blocks = ["0.0.0.0/0"]  # Open to world
}

# App Security Group - Internal Only
ingress {
  from_port       = 5000
  to_port         = 5000
  security_groups = [aws_security_group.alb.id]  # Good: ALB reference
}

# DB Security Group - Most Restrictive
ingress {
  from_port       = 5432
  to_port         = 5432
  security_groups = [aws_security_group.app.id]  # Good: App reference only
}
```

### Security Findings

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | ⚠️ Medium | ALB allows all HTTP (80) | Redirect to HTTPS, restrict to known IPs |
| 2 | ✅ Good | App tier only accessible from ALB | No change needed |
| 3 | ✅ Good | DB tier only accessible from App | No change needed |
| 4 | 🔴 High | No egress restriction on App/DB | Add explicit egress rules |
| 5 | ⚠️ Medium | No WAF rules on ALB | Add AWS WAF for OWASP protection |

### Recommended Security Group Updates

```hcl
# App Security Group - Restrict egress
egress {
  description = "Allow HTTPS to AWS services"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

egress {
  description = "Allow PostgreSQL to DB tier"
  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  security_groups = [aws_security_group.db.id]
}

# No other egress allowed - denies all other traffic

# DB Security Group - No egress needed
# (Remove default egress rule entirely)
```

---

## Compliance Framework Mapping

### SOC 2 Type II Controls

| Control | Description | Implementation | Status |
|---------|-------------|----------------|--------|
| CC6.1 | Logical access controls | IAM roles, security groups | ✅ Implemented |
| CC6.2 | Authentication mechanisms | Secrets Manager, OIDC | ✅ Implemented |
| CC6.3 | Access revocation | IAM cleanup on decommission | ⚠️ Manual process |
| CC7.1 | Vulnerability scanning | Trivy in pipeline | ✅ Implemented |
| CC7.2 | Incident detection | CloudWatch + Prometheus | ✅ Implemented |
| CC8.1 | Change management | GitHub PR + approval | ✅ Implemented |

### ISO 27001 Annex A

| Control | Description | Implementation | Status |
|---------|-------------|----------------|--------|
| A.9.1.2 | Access to networks | Security groups, VPC | ✅ Implemented |
| A.9.4.3 | Password management system | Secrets Manager | ✅ Implemented |
| A.12.6.1 | Technical vulnerability management | Trivy + Dependabot | ✅ Implemented |
| A.14.2.1 | Secure development policy | This document | ✅ Documented |
| A.14.2.5 | Secure system engineering | Infrastructure as Code | ✅ Implemented |
| A.17.1.1 | Information security continuity | Multi-region, backups | ⚠️ Partial |

### CIS AWS Foundations Benchmark v3.0

| Control | Description | Status | Notes |
|---------|-------------|--------|-------|
| 1.1 | Root account MFA | ✅ | Verify manually |
| 1.4 | Unused credentials disabled | ⚠️ | Audit quarterly |
| 1.8 | IAM policies attached to groups only | ✅ | Role-based |
| 2.1 | CloudTrail enabled | ✅ | Via CloudWatch agent |
| 2.7 | CloudTrail log file validation | ⚠️ | Enable in Terraform |
| 3.1 | Security groups restrict 0.0.0.0 | ⚠️ | App/DB only |
| 3.2 | No public RDS instances | ✅ | Private subnets |
| 4.1 | S3 bucket public access blocked | ✅ | Default block |

---

## Vulnerability Management Process

### Scanning Schedule

| Asset | Tool | Frequency | Owner |
|-------|------|-----------|-------|
| Source code | Snyk/Dependabot | Every commit | Developer |
| Docker images | Trivy | Every build | CI/CD |
| Infrastructure | Checkov/tfsec | Every Terraform plan | DevOps |
| Running containers | Falco | Runtime | SRE |
| AWS environment | Prowler | Weekly | Security |

### Vulnerability Response SLA

| Severity | Detection to Fix | Escalation |
|----------|------------------|------------|
| Critical (CVSS 9-10) | 24 hours | Immediate |
| High (CVSS 7-8.9) | 7 days | Weekly review |
| Medium (CVSS 4-6.9) | 30 days | Monthly review |
| Low (CVSS 0-3.9) | 90 days | Quarterly review |

### Remediation Workflow

```bash
# 1. Vulnerability detected in Trivy scan
Trivy found CRITICAL vulnerability in python:3.12
  - CVE-2024-XXXXX: Buffer overflow in libxml2

# 2. Assess impact
$ trivy image --severity CRITICAL app-backend:latest

# 3. Update base image or dependency
# Edit Dockerfile
FROM python:3.12-slim-bookworm  # Update to patched version

# 4. Rebuild and rescan
$ docker build -t app-backend:patched .
$ trivy image --severity CRITICAL app-backend:patched
Result: No vulnerabilities found

# 5. Deploy and verify
$ git commit -am "fix: patch CVE-2024-XXXXX"
$ git push origin main  # Triggers pipeline
```

---

## Secrets Management

### Approved Secrets Storage

| Secret Type | Storage Location | Rotation Schedule |
|-------------|------------------|-------------------|
| Database credentials | AWS Secrets Manager | 90 days |
| API keys | AWS Secrets Manager | 90 days |
| TLS certificates | AWS ACM | Auto-rotation |
| SSH keys | AWS Systems Manager | Manual |
| GitHub tokens | GitHub Secrets | On compromise |

### Secrets Access Pattern

```python
# ✅ CORRECT: Fetch at runtime via IAM role
import boto3
import json

def get_db_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='/app/production/database')
    return json.loads(response['SecretString'])

# ❌ INCORRECT: Hardcoded or environment variable
DATABASE_URL = "postgresql://app:password@host/db"  # Never do this
DATABASE_URL = os.environ.get("DATABASE_URL")  # Acceptable for dev only
```

### Secrets Rotation Procedure

```bash
# 1. Generate new secret
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update in Secrets Manager
aws secretsmanager update-secret \
  --secret-id /app/production/database \
  --secret-string "{\"username\":\"app\",\"password\":\"$NEW_PASSWORD\"}"

# 3. Force ECS deployment to pick up new secret
aws ecs update-service \
  --cluster production-cluster \
  --service backend-service \
  --force-new-deployment

# 4. Verify connectivity
curl https://example.com/api/health

# 5. Deactivate old secret version
```

---

## Security Audit Commands

### Quick Audit Script

```bash
#!/bin/bash
# security-audit.sh - Run weekly

echo "=== AWS Security Audit ==="

# Check for public S3 buckets
echo "--- S3 Public Access ---"
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  xargs -I {} aws s3api get-public-access-block --bucket {} 2>/dev/null || echo "Public access detected!"

# Check for unrestricted security groups
echo "--- Open Security Groups ---"
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].{GroupId:GroupId,GroupName:GroupName}' \
  --output table

# Check for unencrypted EBS volumes
echo "--- Unencrypted EBS ---"
aws ec2 describe-volumes \
  --query 'Volumes[?Encrypted==`false`].{VolumeId:VolumeId,Size:Size}' \
  --output table

# Check for IAM users (should use roles)
echo "--- IAM Users ---"
aws iam list-users --query 'Users[].UserName' --output text

echo "=== Audit Complete ==="
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Aug 2026 | Security Team | Initial checklist |
