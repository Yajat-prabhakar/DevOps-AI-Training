# Exercise 2.4: Legacy Infrastructure Modernization

## Overview

Modernization of the multi-region AWS Terraform infrastructure (`exercise-1.2/`) addressing critical issues, security hardening, and code quality improvements.

## Changes Made

### Critical Fixes

| Issue | Before | After |
|-------|--------|-------|
| Placeholder backend values | `REPLACE_ME-*` | `devops-training-tfstate` with setup instructions |
| Placeholder Docker image | `your-registry/app-backend:latest` | Configurable via `docker_image` variable |
| HTTP-only ALB | Port 80 only | HTTPS support with ACM certificate |

### Security Improvements

| Change | Impact |
|--------|--------|
| HTTPS listener with TLS 1.3 | Encrypted traffic in transit |
| HTTP-to-HTTPS redirect | Forces secure connections |
| `sensitive = true` on DB endpoint | Prevents accidental exposure in logs |
| Environment validation | Blocks invalid environment names |

### Code Quality

| Change | Benefit |
|--------|---------|
| Added descriptions to all variables | Better documentation, fewer `terraform validate` warnings |
| Added `az_count` variable | Configurable AZ count (was hardcoded to 2) |
| Added `app_port` variable | Single source of truth (was duplicated in 3 modules) |
| Added `docker_image` variable | Configurable deployment image |
| Added `certificate_arn` variable | Optional HTTPS support |
| Simplified `enable_deletion_protection` | Removed verbose ternary |
| Removed deprecated `domain` from EIP | Compatible with AWS provider v5+ |
| Removed unused `vpc_cidr` from security module | Dead code cleanup |
| Added `.gitignore` | Prevents accidental state/secret commits |

### Files Modified

| File | Changes |
|------|---------|
| `backend.tf` | Renamed bucket/table, added setup instructions |
| `variables.tf` | Added 5 new variables, descriptions, validation |
| `outputs.tf` | Added descriptions, marked DB endpoint sensitive |
| `main.tf` | Pass new variables to modules, removed `vpc_cidr` from security |
| `modules/alb/main.tf` | Added HTTPS listener, HTTP redirect |
| `modules/alb/variables.tf` | Added `certificate_arn` variable |
| `modules/asg/main.tf` | Use `docker_image` variable |
| `modules/asg/variables.tf` | Added `docker_image` variable |
| `modules/vpc/main.tf` | Removed deprecated `domain = "vpc"` |
| `modules/security/variables.tf` | Removed unused `vpc_cidr`, added descriptions |
| `.gitignore` | New file for Terraform exclusions |

## Migration Guide

### Prerequisites
1. Create S3 bucket for state storage
2. Create DynamoDB table for state locking
3. (Optional) Request ACM certificate for HTTPS

### Steps
1. Update `backend.tf` with your bucket/table names
2. Run `terraform init` to migrate state
3. Review plan with `terraform plan`
4. Apply changes with `terraform apply`

### Rollback
```bash
# Restore previous backend.tf
git checkout HEAD~1 -- exercise-1.2/backend.tf

# Re-init backend
terraform init -migrate-state
```

## Using Cursor for This Work

See `docs/cursor-guide.md` for detailed instructions on using Cursor AI for infrastructure modernization.
