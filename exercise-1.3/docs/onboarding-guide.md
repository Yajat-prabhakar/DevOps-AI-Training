# Onboarding Guide for New Team Members

**Exercise 1.3** | Version: 1.0 | Last Updated: August 2026

---

## Welcome to the DevOps Team!

This guide will help you get up to speed with our infrastructure, tools, and processes. Follow each section in order.

---

## Week 1: Environment Setup

### Day 1: Access & Accounts

**Required Access:**

| System | Purpose | Request From |
|--------|---------|--------------|
| GitHub | Code repository | Team Lead |
| AWS Console | Infrastructure | Team Lead |
| Slack | Communication | Auto-provisioned |
| PagerDuty | On-call rotation | Team Lead |
| Grafana | Monitoring | DevOps Admin |
| Grafana | Logs | DevOps Admin |

**AWS Access Setup:**

```bash
# 1. Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Configure SSO (if using Identity Center)
aws configure sso
# Follow browser login flow

# 3. Verify access
aws sts get-caller-identity
```

**GitHub SSH Setup:**

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your-email@company.com"

# 2. Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and add to GitHub > Settings > SSH Keys

# 4. Test connection
ssh -T git@github.com
```

### Day 2-3: Clone & Explore

```bash
# 1. Clone the repository
git clone git@github.com:your-org/devops-training.git
cd devops-training

# 2. Explore the structure
tree -L 2
├── exercise-1.1/          # Docker Compose stack
│   ├── backend/           # Flask API
│   ├── frontend/          # React app
│   ├── postgres/          # Database init
│   └── docker-compose*.yml
├── exercise-1.2/          # Terraform infrastructure
│   ├── modules/           # VPC, Security, RDS, IAM, ALB, ASG
│   ├── environments/      # Staging/Production configs
│   └── *.tf               # Root configuration
├── exercise-1.3/          # CI/CD & Documentation (you are here)
│   ├── .github/workflows/ # Pipeline definitions
│   └── docs/              # This documentation
└── README.md
```

### Day 4-5: Local Development

```bash
# 1. Start the application stack
docker compose up --build

# 2. Verify services
docker compose ps
# Should show: postgres, backend, frontend - all healthy

# 3. Test endpoints
curl http://localhost:5000/api/health
# Expected: {"service": "ok", "db": "ok"}

curl http://localhost:5000/api/hello
# Expected: {"message": "Hello from the Flask API", "ts": ...}

# 4. Access frontend
open http://localhost:3000

# 5. View logs
docker compose logs -f backend
docker compose logs -f postgres
```

---

## Week 2: Infrastructure Deep Dive

### Terraform Overview

**Key Files:**

| File | Purpose | Key Resources |
|------|---------|---------------|
| `main.tf` | Primary infrastructure | VPC, Security, RDS, ALB, ASG |
| `providers.tf` | AWS provider config | Multi-region setup |
| `variables.tf` | Input variables | Environment, instance types |
| `outputs.tf` | Output values | Endpoints, IDs |
| `backend.tf` | State management | S3 + DynamoDB lock |

**Module Structure:**

```
modules/
├── vpc/           # VPC, subnets, routing
├── security/      # Security groups
├── rds/           # Database (PostgreSQL)
├── iam/           # IAM roles/policies
├── alb/           # Application Load Balancer
└── asg/           # Auto Scaling Group
```

**Common Commands:**

```bash
cd exercise-1.2

# Initialize (first time)
terraform init

# Plan changes
terraform plan -var-file=environments/us-east-1/staging.tfvars

# Apply changes
terraform apply -var-file=environments/us-east-1/staging.tfvars

# View current state
terraform state list
terraform state show module.vpc_primary

# Destroy (be careful!)
terraform destroy -var-file=environments/us-east-1/staging.tfvars
```

### CI/CD Pipeline

**Pipeline Stages:**

```
┌─────────────────────────────────────────────────────────┐
│  1. Lint & Scan    → Code quality, security scanning   │
│  2. Test Backend   → Python tests, coverage            │
│  3. Test Frontend  → TypeScript, build verification    │
│  4. Build          → Docker images, push to ECR        │
│  5. Terraform      → Infrastructure validation         │
│  6. Deploy Staging → ECS deployment, smoke tests       │
│  7. Integration    → E2E tests against staging         │
│  8. Deploy Prod    → Production deployment (manual)    │
└─────────────────────────────────────────────────────────┘
```

**Key Workflow Files:**

```bash
.github/workflows/
├── ci-cd.yml        # Main pipeline
├── rollback.yml     # Emergency rollback
```

**Manual Pipeline Commands:**

```bash
# Trigger pipeline manually
gh workflow run ci-cd.yml -f environment=staging

# Check run status
gh run list --workflow=ci-cd.yml --limit=5

# View run logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed
```

---

## Week 3: Monitoring & Observability

### Prometheus Metrics

**Accessing Prometheus:**

```bash
# Port forward to local
kubectl port-forward svc/prometheus 9090:9090

# Or access via Grafana
open http://localhost:3000 → Explore → Prometheus
```

**Key Metrics:**

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `http_requests_total` | Total HTTP requests | - |
| `http_request_duration_seconds` | Request latency | P95 > 1s |
| `http_requests_total{status=~"5.."}` | Error rate | > 5% |
| `up` | Service availability | == 0 |
| `node_cpu_seconds_total` | CPU usage | > 85% |
| `node_memory_MemAvailable_bytes` | Free memory | < 15% |

**Useful Queries:**

```promql
# Request rate by status code
rate(http_requests_total[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Top 5 slowest endpoints
topk(5, rate(http_request_duration_seconds_sum[5m]))
```

### Grafana Dashboards

**Default Dashboards:**

| Dashboard | URL Path | Purpose |
|-----------|----------|---------|
| Main | `/d/main` | Overview of all services |
| Backend API | `/d/backend` | Flask API metrics |
| PostgreSQL | `/d/postgres` | Database performance |
| Infrastructure | `/d/infra` | EC2, RDS, ALB metrics |

**Creating Alerts:**

```bash
# Via UI
1. Go to Alerting → New Alert Rule
2. Set query: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
3. Set evaluation: For 5 minutes
4. Configure notification channel (Slack/PagerDuty)
```

### Log Management

**Viewing Logs:**

```bash
# CloudWatch Logs
aws logs tail /ecs/backend --since 1h --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /ecs/backend \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Grafana Loki (if configured)
# Grafana → Explore → Loki → {app="backend"} |= "ERROR"
```

---

## Common Tasks

### Task: Deploy a Change

```bash
# 1. Create feature branch
git checkout -b feature/my-change

# 2. Make changes
vim exercise-1.2/variables.tf

# 3. Validate locally
cd exercise-1.2
terraform fmt -check
terraform validate

# 4. Commit and push
git add .
git commit -m "feat: description of change"
git push origin feature/my-change

# 5. Create PR
gh pr create --title "feat: description" --body "Changes summary"

# 6. After approval, merge
gh pr merge --squash
```

### Task: Debug a Failed Deployment

```bash
# 1. Check pipeline status
gh run list --workflow=ci-cd.yml --limit=3

# 2. View failed job logs
gh run view <run-id> --job <job-id> --log

# 3. Check ECS service status
aws ecs describe-services \
  --cluster production-cluster \
  --services backend-service \
  --query 'services[0].{status:status,events:events[:5]}'

# 4. View stopped task logs
aws logs get-log-events \
  --log-group-name /ecs/backend \
  --log-stream-name <stopped-task-stream>
```

### Task: Rotate Secrets

```bash
# 1. Generate new password
NEW_PASS=$(openssl rand -base64 32)

# 2. Update Secrets Manager
aws secretsmanager update-secret \
  --secret-id /app/production/database \
  --secret-string "{\"username\":\"app\",\"password\":\"$NEW_PASS\"}"

# 3. Force redeployment
aws ecs update-service \
  --cluster production-cluster \
  --service backend-service \
  --force-new-deployment

# 4. Verify
curl https://example.com/api/health
```

---

## Key Contacts

| Role | Name | Slack | PagerDuty |
|------|------|-------|-----------|
| Team Lead | [Name] | @teamlead | On-call |
| Senior DevOps | [Name] | @senior-devops | Secondary |
| Security | [Name] | @security | Security on-call |
| Database | [Name] | @dba | DB on-call |

---

## Resources

### Internal Documentation

- [Troubleshooting Guide](./troubleshooting-guide.md)
- [Standard Operating Procedures](./standard-operating-procedures.md)
- [Performance Optimization](./performance-optimization.md)
- [Security Checklist](./security-checklist.md)

### External Learning

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/)

---

## Your First Week Checklist

- [ ] AWS access configured and verified
- [ ] GitHub SSH key added
- [ ] Repository cloned
- [ ] Docker Compose stack running locally
- [ ] Terraform init completed (staging)
- [ ] Pipeline triggered manually
- [ ] Grafana dashboard accessed
- [ ] Met the team in Slack
- [ ] Read this onboarding guide completely
- [ ] Completed first task (assigned by Team Lead)

---

## Questions?

- **Slack:** #devops-team
- **Documentation:** This folder
- **Emergency:** #incident channel + PagerDuty

Welcome aboard! 🚀
