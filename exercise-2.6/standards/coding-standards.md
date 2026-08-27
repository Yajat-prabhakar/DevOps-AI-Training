# DevOps Coding Standards

## Terraform Standards

### File Organization
```
project/
├── main.tf           # Resource definitions
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── providers.tf      # Provider configuration
├── versions.tf       # Version constraints (optional)
├── backend.tf        # Remote state configuration
├── locals.tf         # Local values
├── data.tf           # Data sources
├── modules/          # Reusable modules
│   └── <module>/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/     # Environment-specific values
    ├── dev/
    ├── staging/
    └── prod/
```

### Naming Conventions

| Resource Type | Convention | Example |
|---------------|------------|---------|
| Resources | `snake_case` | `aws_instance.web_server` |
| Variables | `snake_case` | `instance_type` |
| Outputs | `snake_case` | `instance_id` |
| Locals | `snake_case` | `common_tags` |
| Data Sources | `snake_case` | `aws_ami.latest` |
| Modules | `snake_case` | `module.vpc` |

### Variable Standards

```hcl
variable "instance_type" {
  type        = string
  description = "EC2 instance type for the web server"
  default     = "t3.micro"

  validation {
    condition     = can(regex("^t3\\.", var.instance_type))
    error_message = "Instance type must be t3 burstable."
  }
}
```

**Rules:**
1. Always include `type` and `description`
2. Add `validation` blocks for constrained values
3. Use `default` only when safe
4. Mark sensitive values with `sensitive = true`

### Output Standards

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "db_password" {
  description = "Database password"
  value       = aws_secretsmanager_secret_version.db_password.secret_string
  sensitive   = true
}
```

**Rules:**
1. Always include `description`
2. Mark secrets as `sensitive = true`
3. Use meaningful names
4. Document what each output represents

### Resource Standards

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.latest.id
  instance_type = var.instance_type

  tags = merge(var.tags, {
    Name        = "${var.environment}-web-server"
    Environment = var.environment
  })
}
```

**Rules:**
1. Use descriptive names
2. Always include `tags`
3. Use `merge()` for common tags
4. Add comments for complex resources

---

## Kubernetes Standards

### File Organization
```
k8s/
├── base/                 # Base manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── overlays/             # Environment overlays
│   ├── staging/
│   └── production/
└── helm/                 # Helm charts
    └── app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

### Naming Conventions

| Resource | Convention | Example |
|----------|------------|---------|
| Deployment | `kebab-case` | `backend-deployment` |
| Service | `kebab-case` | `backend-service` |
| ConfigMap | `kebab-case` | `app-config` |
| Secret | `kebab-case` | `app-secrets` |
| Ingress | `kebab-case` | `app-ingress` |

### Deployment Standards

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: app
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/component: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: backend
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: backend
          image: app-backend:latest
          ports:
            - containerPort: 5000
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /api/health
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 5
```

**Rules:**
1. Always include resource limits
2. Define health probes (liveness, readiness, startup)
3. Use security contexts (non-root, read-only rootfs)
4. Add proper labels
5. Use namespaces

---

## Docker Standards

### Dockerfile Best Practices

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM deps AS build
COPY . .
RUN npm run build

# Stage 3: Production
FROM nginx:1.27-alpine AS production
RUN apk add --no-cache curl
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/healthz || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

**Rules:**
1. Use multi-stage builds
2. Minimize layers
3. Use specific base image tags
4. Add HEALTHCHECK
5. Run as non-root user
6. Use .dockerignore

---

## CI/CD Standards

### Pipeline Structure

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint & Security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linters
      - name: Run security scans

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests

  build:
    name: Build
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build images

  deploy:
    name: Deploy
    needs: [build]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
```

**Rules:**
1. Run lint/test before build
2. Use matrix builds for multi-platform
3. Cache dependencies
4. Use environment protection rules
5. Add notifications

---

## Documentation Standards

### README Structure

```markdown
# Project Name

## Overview
Brief description of the project.

## Prerequisites
List of requirements.

## Installation
Step-by-step setup instructions.

## Usage
How to use the project.

## Configuration
Configuration options.

## Troubleshooting
Common issues and solutions.

## Contributing
Guidelines for contributions.

## License
License information.
```

### Inline Comments

```hcl
# One NAT gateway per AZ so an AZ outage doesn't take private egress with it
resource "aws_nat_gateway" "this" {
  count         = var.az_count
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}
```

**Rules:**
1. Explain "why", not "what"
2. Keep comments concise
3. Update comments when code changes
4. Use TODO for future work
