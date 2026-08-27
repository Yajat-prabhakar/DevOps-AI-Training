# Using Cursor for Infrastructure Modernization

## What is Cursor?

Cursor is an AI-powered IDE built on VS Code that provides intelligent code analysis, refactoring, and debugging capabilities. It uses AI to understand your codebase and suggest improvements.

## Setup

1. Download Cursor from https://cursor.sh
2. Import your VS Code settings: `Cursor > Import Settings from VS Code`
3. Sign in with your account for AI features

## Key Features for Infrastructure Work

### 1. Codebase Understanding

**Command:** `Cmd/Ctrl + Shift + P` → "Codebase Indexing"

Cursor indexes your entire repository, allowing you to:
- Ask questions about your infrastructure
- Understand dependencies between modules
- Find all references to a variable or resource

**Example Prompts:**
```
What are all the dependencies between Terraform modules?
Which resources use the vpc_cidr variable?
Explain the security group chaining in this codebase.
```

### 2. Intelligent Refactoring

**Command:** `Cmd/Ctrl + Shift + P` → "Refactor"

Select code and let Cursor suggest improvements:

```hcl
# Before
enable_deletion_protection = var.environment == "prod" ? true : false

# Cursor suggests:
enable_deletion_protection = var.environment == "prod"
```

### 3. Code Analysis

**Command:** `Cmd/Ctrl + L` (Chat) or `Cmd/Ctrl + K` (Edit)

Ask Cursor to analyze your code:

```
@file:main.tf Analyze this Terraform configuration and suggest improvements
@file:variables.tf Add descriptions to all variables
@folder:modules Find code duplication across modules
```

### 4. Documentation Generation

**Command:** `Cmd/Ctrl + L` → "Generate Documentation"

```
Generate a README for this Terraform module
Add inline comments explaining the security group rules
Create a migration guide for the backend changes
```

### 5. Debugging

**Command:** `Cmd/Ctrl + L` → "Debug"

```
Why might this Terraform plan fail?
What security issues do you see in this configuration?
Explain this error message: [paste error]
```

## Workflow for Infrastructure Modernization

### Step 1: Codebase Analysis
```
Cmd/Ctrl + L: "Analyze the entire exercise-1.2 directory. 
Identify all issues including:
- Security vulnerabilities
- Code duplication
- Missing documentation
- Deprecated attributes
- Best practice violations"
```

### Step 2: Prioritized Fixes
```
Cmd/Ctrl + L: "Create a prioritized list of fixes needed, 
categorized by:
- Critical (security, breaking changes)
- High (code quality, maintainability)
- Medium (documentation, naming)
- Low (cosmetic, minor improvements)"
```

### Step 3: Implement Fixes
```
Cmd/Ctrl + K: Select the code to change
"Refactor this to use a variable instead of hardcoded value"
"Add error handling to this resource"
"Improve the naming of this resource"
```

### Step 4: Generate Documentation
```
Cmd/Ctrl + L: "Generate documentation for all changes made,
including:
- Migration steps
- Rollback procedures
- Configuration options"
```

## Cursor Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + L` | Open AI Chat |
| `Cmd/Ctrl + K` | Edit with AI |
| `Cmd/Ctrl + I` | Inline AI suggestion |
| `Cmd/Ctrl + Shift + P` | Command Palette |
| `Cmd/Ctrl + P` | Quick Open |
| `Cmd/Ctrl + G` | Go to File |
| `Cmd/Ctrl + R` | Go to Symbol |

## Best Practices

1. **Be Specific:** Include file names and context in prompts
2. **Review Changes:** Always review AI suggestions before applying
3. **Test First:** Run `terraform plan` after changes
4. **Commit Often:** Small, focused commits for each change
5. **Document Changes:** Use Cursor to generate documentation

## Example Session

```
You: @file:modules/alb/main.tf This ALB only has HTTP. Add HTTPS support.

Cursor: I'll add HTTPS support to the ALB. Here's what needs to change:
1. Add a variable for the ACM certificate ARN
2. Create an HTTPS listener on port 443
3. Modify the HTTP listener to redirect to HTTPS
4. Use TLS 1.3 policy for security

[Cursor generates the code changes]

You: Apply these changes

Cursor: [Applies the changes to the files]

You: Generate a migration guide for this change

Cursor: [Generates documentation]
```

## Resources

- [Cursor Documentation](https://docs.cursor.sh)
- [Cursor AI Features](https://cursor.sh/features)
- [Terraform Best Practices](https://www.terraform-best-practices.com)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
