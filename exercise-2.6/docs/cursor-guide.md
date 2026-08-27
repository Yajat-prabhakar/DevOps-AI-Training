# Using Cursor for Code Quality Analysis

## Code Quality Analysis Workflow

### Step 1: Repository-Wide Analysis

```
Cmd/Ctrl + L: "Analyze the entire codebase for code quality issues.
Focus on:
1. Naming conventions
2. Documentation completeness
3. Security vulnerabilities
4. Best practice violations
5. Code duplication"
```

### Step 2: Terraform Quality Check

```
Cmd/Ctrl + L: @folder:exercise-1.2
"Review this Terraform codebase for quality issues:
1. Variables without descriptions
2. Outputs without descriptions
3. Missing validation rules
4. Deprecated attributes
5. Security issues"
```

### Step 3: Kubernetes Quality Check

```
Cmd/Ctrl + L: @folder:exercise-2.2
"Review these Kubernetes manifests for quality issues:
1. Missing resource limits
2. Missing health probes
3. Security contexts
4. Network policies
5. Label consistency"
```

### Step 4: CI/CD Quality Check

```
Cmd/Ctrl + L: @file:.github/workflows/ci-cd.yml
"Review this GitHub Actions workflow for quality:
1. Job dependencies
2. Caching strategy
3. Security scanning
4. Error handling
5. Notification setup"
```

## Automated Quality Checks

### Using Cursor with Linters

```bash
# Terraform
terraform fmt -check -recursive
terraform validate
tflint --config .tflint.hcl

# Kubernetes
kubeval deployment.yaml
kube-linter lint deployment.yaml

# Docker
hadolint Dockerfile
docker scan app-backend:latest
```

### Cursor Commands for Quality

| Command | Action |
|---------|--------|
| `Cmd/Ctrl + L` | Open AI Chat |
| `Cmd/Ctrl + K` | Edit with AI |
| `Cmd/Ctrl + Shift + P` | Command Palette |
| `Cmd/Ctrl + P` | Quick Open |

## Quality Metrics

### Before Improvements

| Category | Score | Issues |
|----------|-------|--------|
| Documentation | 7/10 | Missing descriptions |
| Security | 8/10 | HTTP-only ALB |
| Best Practices | 7.5/10 | Duplicated code |
| Testing | 6/10 | No automated tests |

### After Improvements

| Category | Score | Changes |
|----------|-------|---------|
| Documentation | 9/10 | Added all descriptions |
| Security | 9.5/10 | HTTPS, TLS 1.3 |
| Best Practices | 9/10 | Refactored code |
| Testing | 8/10 | Added test frameworks |

## Example Quality Analysis Session

```
You: @folder:exercise-1.2 Analyze this Terraform codebase for quality issues.

Cursor: I've analyzed the codebase and found 15 issues:

Critical (2):
1. Placeholder backend values in backend.tf
2. Placeholder Docker image in ASG user_data

High (5):
3. Missing variable descriptions in 6 modules
4. Unused vpc_cidr variable in security module
5. Deprecated domain attribute in EIP
6. No HTTPS support on ALB
7. Duplicated app_port variable in 3 modules

Medium (5):
8. Missing output descriptions
9. No validation rules on variables
10. Verbose ternary for deletion_protection
11. No .gitignore file
12. Hardcoded az_count = 2

Low (3):
13. Missing inline comments
14. Inconsistent tag style
15. No versions.tf file

Would you like me to fix these issues?
```

## Best Practices

1. **Run Quality Checks Regularly**
   ```bash
   # Add to CI pipeline
   terraform fmt -check -recursive
   tflint --config .tflint.hcl
   kubeval *.yaml
   ```

2. **Use Pre-commit Hooks**
   ```yaml
   repos:
     - repo: https://github.com/antonbabenko/pre-commit-terraform
       hooks:
         - id: terraform_fmt
         - id: terraform_validate
         - id: terraform_tflint
   ```

3. **Document Everything**
   - Add descriptions to all variables
   - Add descriptions to all outputs
   - Add inline comments for complex logic
   - Update README with changes

4. **Review with Cursor**
   - Use `Cmd/Ctrl + L` for code review
   - Ask for improvement suggestions
   - Generate documentation

## Resources

- [Terraform Best Practices](https://www.terraform-best-practices.com)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/overview/best-practices/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-using-github-actions)
