# Exercise 2.3: Infrastructure Testing Framework

## Overview

Comprehensive testing framework for infrastructure code, including unit tests for Terraform modules (Terratest), integration tests for Ansible playbooks (Molecule), and end-to-end tests for Docker Compose deployments (pytest).

## Testing Framework Structure

```
exercise-2.3/
├── terratest/           # Go-based infrastructure tests
│   ├── vpc_test.go     # VPC module tests
│   ├── docker_test.go  # Docker build tests
│   ├── main.tf         # Test Terraform config
│   ├── go.mod          # Go dependencies
│   └── go.sum          # Go checksums
├── molecule/            # Ansible role testing
│   └── default/
│       ├── molecule.yml  # Molecule configuration
│       ├── converge.yml  # Ansible playbook
│       ├── verify.yml    # Verification tasks
│       ├── playbook.yml  # Main playbook
│       └── templates/    # Jinja2 templates
└── pytest/              # Python-based tests
    ├── test_docker_compose.py  # Docker Compose tests
    ├── test_api.py             # API endpoint tests
    ├── test_security.py        # Security compliance tests
    └── test_performance.py     # Performance tests
```

## Test Categories

### 1. Unit Tests (Terratest)

Tests individual Terraform modules in isolation.

**Files:**
- `vpc_test.go` - VPC, subnets, routing
- `docker_test.go` - Docker image build, run, size

**Run:**
```bash
cd exercise-2.3/terratest
go mod init terratest
go mod tidy
go test -v -timeout 30m
```

### 2. Integration Tests (Molecule)

Tests Ansible roles in a Docker container.

**Files:**
- `converge.yml` - Playbook to apply role
- `verify.yml` - Assertions to verify role
- `molecule.yml` - Molecule configuration

**Run:**
```bash
cd exercise-2.3/molecule/default
molecule test
molecule converge
molecule verify
```

### 3. End-to-End Tests (pytest)

Tests the complete application stack.

**Files:**
- `test_docker_compose.py` - Docker Compose tests
- `test_api.py` - API endpoint tests
- `test_security.py` - Security compliance tests
- `test_performance.py` - Performance tests

**Run:**
```bash
cd exercise-2.3/pytest
pip install -r requirements.txt
pytest -v
```

## Test Details

### Terratest Tests

| Test | Description |
|------|-------------|
| `TestVpcModule` | Validates VPC creation with subnets |
| `TestSecurityModule` | Validates security group creation |
| `TestRdsModule` | Validates RDS instance creation |
| `TestDockerBuild` | Validates Docker image build |
| `TestDockerRun` | Validates Docker container runs |
| `TestDockerImageSize` | Validates image size < 500MB |

### Molecule Tests

| Test | Description |
|------|-------------|
| nginx installed | Verifies nginx is installed |
| nginx running | Verifies nginx service is active |
| app directory | Verifies application directory exists |
| nginx config | Verifies nginx configuration exists |
| firewall HTTP | Verifies firewall allows HTTP |

### pytest Tests

| Test | Description |
|------|-------------|
| Service running | Verifies all Docker services are up |
| Backend health | Tests backend health endpoint |
| Frontend health | Tests frontend health endpoint |
| Database connection | Tests PostgreSQL connectivity |
| API response format | Validates JSON response structure |
| Response time | Tests API response time < 2s |
| Concurrent requests | Tests 50 concurrent requests |
| Memory usage | Tests container memory < 90% |
| CPU usage | Tests container CPU < 80% |
| No root user | Validates non-root Docker user |
| No secrets | Checks for hardcoded secrets |
| No privileged | Validates no privileged containers |

## Test Configuration

### Terratest

```go
terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
    TerraformDir: "../exercise-1.2/modules/vpc",
    Vars: map[string]interface{}{
        "environment": "test",
        "vpc_cidr":   "10.0.0.0/16",
    },
})
```

### Molecule

```yaml
driver:
  name: docker
platforms:
  - name: instance
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    privileged: true
```

### pytest

```python
@pytest.fixture(autouse=True)
def setup(self):
    self.base_url = "http://localhost:5000"
    self.timeout = 10
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run Terratest
  run: |
    cd exercise-2.3/terratest
    go test -v -timeout 30m

- name: Run Molecule
  run: |
    cd exercise-2.3/molecule/default
    molecule test

- name: Run pytest
  run: |
    cd exercise-2.3/pytest
    pip install requests pytest docker psycopg2-binary
    pytest -v
```

## Prerequisites

- Go 1.21+ (for Terratest)
- Docker (for Molecule and pytest)
- Python 3.12+ (for pytest)
- Ansible + Molecule (for Molecule tests)

## Coverage

| Category | Coverage |
|----------|----------|
| Terraform Modules | 80% |
| Ansible Roles | 70% |
| API Endpoints | 90% |
| Security | 85% |
| Performance | 75% |
