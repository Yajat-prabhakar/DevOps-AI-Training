# Network Security Group Assessment

**Exercise 1.5** | Date: August 26, 2026

---

## Current Security Group Configuration

### Production ALB Security Group

```hcl
resource "aws_security_group" "alb" {
  name        = "prod-alb-sg"
  description = "ALB Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Production App Security Group

```hcl
resource "aws_security_group" "app" {
  name        = "prod-app-sg"
  description = "App Tier Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "App port from ALB"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Production Database Security Group

```hcl
resource "aws_security_group" "db" {
  name        = "prod-db-sg"
  description = "Database Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from App tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

---

## Security Findings

| # | Severity | Security Group | Finding | Risk |
|---|----------|----------------|---------|------|
| 1 | ⚠️ Medium | ALB | HTTP (80) allowed from 0.0.0.0/0 | Unencrypted traffic, downgrade attacks |
| 2 | ✅ Low | ALB | HTTPS (443) allowed from 0.0.0.0/0 | Expected for public ALB |
| 3 | 🔴 High | App | Unrestricted egress (0.0.0.0/0) | Data exfiltration, C2 communication |
| 4 | 🔴 High | DB | Unrestricted egress (0.0.0.0/0) | Data exfiltration, C2 communication |
| 5 | ⚠️ Medium | ALB | No WAF integration | No OWASP protection |
| 6 | ⚠️ Medium | App | No rate limiting | DDoS vulnerability |
| 7 | ✅ Good | App | Only accessible from ALB | Correct tier isolation |
| 8 | ✅ Good | DB | Only accessible from App tier | Correct tier isolation |

---

## Hardened Security Group Configuration

```hcl
# ALB Security Group - Hardened
resource "aws_security_group" "alb" {
  name        = "prod-alb-sg-hardened"
  description = "Hardened ALB Security Group"
  vpc_id      = var.vpc_id

  # HTTPS only - redirect HTTP to HTTPS
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP redirect (will be handled by ALB listener rule)
  ingress {
    description = "HTTP redirect to HTTPS"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound to App tier only
  egress {
    description     = "To App tier"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = merge(var.tags, { Name = "prod-alb-sg-hardened" })
}

# App Security Group - Hardened
resource "aws_security_group" "app" {
  name        = "prod-app-sg-hardened"
  description = "Hardened App Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "From ALB only"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Outbound to DB only
  egress {
    description     = "To Database tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.db.id]
  }

  # Outbound to HTTPS for dependencies
  egress {
    description = "HTTPS to package repositories"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound DNS
  egress {
    description = "DNS resolution"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound NTP
  egress {
    description = "NTP time sync"
    from_port   = 123
    to_port     = 123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "prod-app-sg-hardened" })
}

# Database Security Group - Hardened (no egress)
resource "aws_security_group" "db" {
  name        = "prod-db-sg-hardened"
  description = "Hardened Database Security Group - No Egress"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from App tier only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # No egress rule - database should never initiate outbound connections

  tags = merge(var.tags, { Name = "prod-db-sg-hardened" })
}
```

---

## VPC Flow Log Configuration

```hcl
# Enable VPC Flow Logs for all security groups
resource "aws_flow_log" "vpc_flow_log" {
  vpc_id                   = var.vpc_id
  traffic_type             = "ALL"
  log_destination_type     = "cloud-watch-logs"
  log_destination          = aws_cloudwatch_log_group.flow_log.arn
  iam_role_arn             = aws_iam_role.flow_log.arn
  max_aggregation_interval = 60

  tags = merge(var.tags, { Name = "${var.environment}-vpc-flow-log" })
}

resource "aws_cloudwatch_log_group" "flow_log" {
  name              = "/aws/vpc/flow-log/${var.environment}"
  retention_in_days = 90
}

# Alert on suspicious flow log patterns
resource "aws_cloudwatch_metric_alarm" "unusual_outbound" {
  alarm_name          = "${var.environment}-unusual-outbound-traffic"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "PacketsOut"
  namespace           = "AWS/VPC"
  period              = 300
  statistic           = "Sum"
  threshold           = 1000000
  alarm_description   = "Unusual outbound traffic detected"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    VpcId = var.vpc_id
  }
}
```

---

## WAF Configuration

```hcl
# AWS WAF Web ACL for ALB
resource "aws_wafv2_web_acl" "alb_waf" {
  name        = "${var.environment}-alb-waf"
  description = "WAF rules for production ALB"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting
  rule {
    name     = "RateLimit"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection Protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Known Bad Inputs
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "KnownBadInputs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-alb-waf"
    sampled_requests_enabled   = true
  }

  tags = var.tags
}

# Associate WAF with ALB
resource "aws_wafv2_web_acl_association" "alb_waf_assoc" {
  resource_arn = var.alb_arn
  web_acl_arn  = aws_wafv2_web_acl.alb_waf.arn
}
```

---

## Compliance Mapping

| Control | AWS Implementation | Status |
|---------|-------------------|--------|
| VPC isolation | VPC + Subnets | ✅ Implemented |
| Security groups | Tiered architecture | ✅ Implemented |
| Network ACLs | Default + custom | ⚠️ Partial |
| VPC Flow Logs | CloudWatch Logs | ⚠️ Needs setup |
| WAF | AWS WAF v2 | ⚠️ Needs setup |
| DDoS protection | AWS Shield Standard | ✅ Enabled |
| Private subnets | RDS + EC2 in private | ✅ Implemented |
| NAT Gateway | Outbound internet | ✅ Implemented |
| VPC endpoints | S3, DynamoDB | ⚠️ Partial |
| Transit Gateway | Multi-VPC | ❌ Not implemented |

---

## Recommendations

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| High | Restrict egress on App/DB security groups | Data exfiltration prevention | Low |
| High | Enable WAF on ALB | OWASP protection | Medium |
| High | Enable VPC Flow Logs | Network monitoring | Low |
| Medium | Implement NACLs | Defense in depth | Medium |
| Medium | Add VPC endpoints | Reduce internet exposure | Medium |
| Low | Implement Transit Gateway | Multi-VPC management | High |
