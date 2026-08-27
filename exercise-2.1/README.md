# Exercise 2.1: Enterprise CI/CD Pipeline

## Overview

Enhanced GitHub Actions CI/CD pipeline with enterprise-grade features including matrix builds, SAST/DAST security scanning, Docker build caching, automated rollback, and Slack notifications.

## Pipeline Architecture

```
push/PR ──> lint-and-scan ──> test-backend (matrix) ──┐
                        ├─> test-frontend (matrix) ──┤
                        └─> terraform-validate ───────┤
                                                      ▼
                                              build (cached)
                                                      │
                                              deploy-staging
                                                      │
                                         [auto-rollback on failure]
                                                      │
                                           integration-tests
                                                      │
                                          deploy-production (manual approval)
                                                      │
                                         [auto-rollback on failure]
                                                      │
                                               notify (Slack)
```

## Pipeline Stages

### Stage 1: Code Quality & Security (SAST)
- **CodeQL Analysis**: Static Application Security Testing for Python and JavaScript
- **Trivy Scanner**: Vulnerability scanning for filesystem and Docker images
- **Hadolint**: Dockerfile best practices validation
- **YAML Lint**: Workflow file validation

### Stage 2: Backend Tests (Matrix)
- **Matrix Strategy**: Python 3.11 and 3.12
- **Linting**: flake8 with configurable rules
- **Security**: bandit static analysis
- **Coverage**: pytest with XML/terminal reports
- **Caching**: pip dependency caching

### Stage 3: Frontend Tests (Matrix)
- **Matrix Strategy**: Node.js 18, 20, and 22
- **Linting**: ESLint for TypeScript
- **Build**: Vite production build
- **Caching**: npm dependency caching
- **Artifacts**: Build output for downstream jobs

### Stage 4: Docker Build (Cached)
- **Buildx**: Multi-platform build support
- **Layer Caching**: GitHub Actions cache backend
- **Metadata**: OCI image labels (commit, timestamp, branch)
- **Image Scanning**: Trivy SARIF upload to GitHub Security

### Stage 5: Infrastructure Validation
- **Format Check**: terraform fmt validation
- **Init/Validate**: Terraform configuration validation
- **Plan**: Staging environment plan with artifact upload

### Stage 6: Staging Deployment
- **Infrastructure**: Terraform apply
- **Application**: ECS service update (backend + frontend)
- **Health Check**: Smoke tests against staging URL
- **Auto-Rollback**: Automatic rollback on health check failure

### Stage 7: Integration Tests
- **API Tests**: Automated integration test suite
- **Coverage**: Runs against deployed staging environment

### Stage 8: Production Deployment
- **Manual Approval**: GitHub environment protection rules
- **Infrastructure**: Terraform apply for production
- **Application**: ECS service update
- **Health Check**: Production smoke tests
- **Auto-Rollback**: Automatic rollback on failure

### Stage 9: Notifications
- **Slack Integration**: Webhook-based notifications
- **Status Reporting**: Success/failure/warning states
- **Rich Messages**: Commit, actor, branch, and run link

## Matrix Build Configuration

### Backend (Python)
```yaml
matrix:
  python-version: ['3.11', '3.12']
  fail-fast: false
```

### Frontend (Node.js)
```yaml
matrix:
  node-version: ['18', '20', '22']
  fail-fast: false
```

## Security Features

| Feature | Tool | Purpose |
|---------|------|---------|
| SAST | CodeQL | Static code analysis |
| Vulnerability Scan | Trivy | Dependency/container scanning |
| Dockerfile Lint | Hadolint | Best practices validation |
| Image Scan | Trivy | Container vulnerability scan |
| Bandit | Python | Security static analysis |

## Automated Rollback

The pipeline includes automatic rollback for both staging and production:

1. **Detection**: Smoke test fails after deployment
2. **Rollback**: Previous task definition restored
3. **Verification**: Wait for services to stabilize
4. **Notification**: Slack alert sent

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `AWS_ROLE_ARN` | AWS IAM role for OIDC federation |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |

## Usage

### Automatic Trigger
- Push to `main` or `develop` branch
- Pull request to `main`

### Manual Trigger
```bash
gh workflow run ci-cd.yml -f environment=staging
gh workflow run ci-cd.yml -f environment=production
```

### Manual Rollback
```bash
gh workflow run rollback.yml -f environment=production -f service=all -f reason="Critical bug"
```

## Artifacts

| Artifact | Description |
|----------|-------------|
| `bandit-results-py*` | Security scan results per Python version |
| `coverage-report-py*` | Test coverage reports per Python version |
| `frontend-build-node*` | Frontend build output per Node version |
| `tfplan-staging` | Terraform plan for staging |

## Job Summaries

Each deployment generates a GitHub Step Summary with:
- Pipeline status
- Commit SHA
- Deployed by
- Timestamp
- Link to run
