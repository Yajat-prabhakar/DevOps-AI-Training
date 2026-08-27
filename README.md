# DevOps AI Training Program

## Overview

Complete DevOps training program covering infrastructure automation, CI/CD pipelines, security, monitoring, and AI-assisted development.

## Phase 1: DevOps Fundamentals (Weeks 1-3)

### Exercise 1.1: Multi-Service Docker Environment
- Flask backend + React frontend + PostgreSQL
- Docker Compose with environment overrides (dev/staging/prod)
- Health checks, networking, secrets management
- **Location:** `exercise-1.1/`

### Exercise 1.2: Multi-Region AWS Infrastructure
- Terraform modules: VPC, Security, ALB, ASG, RDS, IAM
- Multi-region deployment (us-east-1, eu-west-1)
- Production-ready with HTTPS, IMDSv2, SSM
- **Location:** `exercise-1.2/`

### Exercise 1.3: CI/CD Pipeline Documentation
- GitHub Actions pipeline (8 stages)
- Troubleshooting guides, SOPs, onboarding docs
- Performance optimization, security checklist
- **Location:** `exercise-1.3/`

### Exercise 1.4: Log Correlation & Incident Analysis
- Simulated PostgreSQL, backend, Nginx logs
- Root cause analysis of connection pool exhaustion
- **Location:** `exercise-1.4/`

### Exercise 1.5: Security Hardening & Compliance
- Vulnerable vs hardened IAM policies
- Kubernetes RBAC assessment
- Network security, compliance reports (SOC 2, ISO 27001)
- **Location:** `exercise-1.5/`

### Exercise 1.6: Incident Response & Post-Mortem
- Slack conversation reconstruction
- Incident response playbook
- Post-mortem documentation
- **Location:** `exercise-1.6/`

## Phase 2: AI Coding Assistants for Infrastructure (Weeks 4-7)

### Exercise 2.1: Enterprise CI/CD Pipeline
- Matrix builds (Python 3.11/3.12, Node.js 18/20/22)
- SAST scanning (CodeQL, Trivy, Hadolint)
- Docker build caching with GHA
- Automated rollback on failure
- Slack notifications
- **Location:** `exercise-2.1/`

### Exercise 2.2: Kubernetes Application Deployment
- Production-ready K8s manifests (Namespace, ConfigMap, Secret, Deployment, Service, Ingress)
- Helm chart with templating and values
- NetworkPolicies (default-deny, allow frontend→backend, backend→db)
- HPA autoscaling (CPU/memory based)
- Prometheus monitoring and alerting
- Kustomize overlays (staging/production)
- **Location:** `exercise-2.2/`

### Exercise 2.3: Infrastructure Testing Framework
- Terratest for Terraform modules (Go)
- Molecule for Ansible playbooks
- pytest for Docker Compose and API testing
- Security compliance tests
- Performance benchmarking
- **Location:** `exercise-2.3/`

### Exercise 2.4: Legacy Infrastructure Modernization
- Terraform code analysis and issue identification
- Critical fixes: HTTPS, placeholder values, Docker image
- Code quality improvements (descriptions, validation, cleanup)
- Migration documentation
- **Location:** `exercise-2.4/` (docs), `exercise-1.2/` (code changes)

### Exercise 2.5: Multi-Service Debugging Challenge
- 10 intentionally broken Kubernetes manifests
- Categories: Image, Resources, Networking, Probes, Secrets, Scheduling, Config, RBAC, Storage, Dependencies
- Fixed versions with explanations
- Debugging guide
- **Location:** `exercise-2.5/`

### Exercise 2.6: Code Quality Enhancement
- Coding standards (Terraform, K8s, Docker, CI/CD)
- Code quality metrics and assessment
- Automated quality checks documentation
- Team guidelines
- **Location:** `exercise-2.6/`

## Repository Structure

```
DevOps-AI-Training/
├── .github/workflows/
│   ├── ci-cd.yml          # Main CI/CD pipeline (9 stages)
│   └── rollback.yml       # Manual rollback workflow
├── exercise-1.1/          # Docker environment
├── exercise-1.2/          # Terraform infrastructure
├── exercise-1.3/          # CI/CD documentation
├── exercise-1.4/          # Log analysis
├── exercise-1.5/          # Security hardening
├── exercise-1.6/          # Incident response
├── exercise-2.1/          # Enterprise CI/CD
├── exercise-2.2/          # Kubernetes deployment
├── exercise-2.3/          # Testing framework
├── exercise-2.4/          # Infrastructure modernization
├── exercise-2.5/          # Debugging challenge
└── exercise-2.6/          # Code quality standards
```

## CI/CD Pipeline Status

| Stage | Job | Status |
|-------|-----|--------|
| 1 | Code Quality & Security (SAST) | ✅ Passing |
| 2 | Backend Tests (Python 3.11, 3.12) | ✅ Passing |
| 3 | Frontend Tests (Node 18, 20, 22) | ✅ Passing |
| 4 | Build Docker Images | ❌ Needs AWS credentials |
| 5 | Terraform Validation | ✅ Passing |
| 6 | Deploy to Staging | ⏸️ Needs AWS credentials |
| 7 | Integration Tests | ⏸️ Depends on deploy |
| 8 | Deploy to Production | ⏸️ Needs approval + AWS |
| 9 | Send Notifications | ✅ Passing |

## Tools Used

- **AI Assistants:** opencode, Cursor
- **Infrastructure:** Terraform, AWS (VPC, ECS, RDS, ALB, ASG, IAM)
- **Containers:** Docker, Docker Compose, Kubernetes, Helm
- **CI/CD:** GitHub Actions, Trivy, CodeQL, Hadolint
- **Monitoring:** Prometheus, Grafana
- **Testing:** pytest, Terratest, Molecule

## Getting Started

1. Clone the repository
2. Review the exercise README files
3. Follow the documentation in each exercise directory
4. Use Cursor for AI-assisted development

## Author

Yajat Prabhakar

## License

DevOps AI Training Program
