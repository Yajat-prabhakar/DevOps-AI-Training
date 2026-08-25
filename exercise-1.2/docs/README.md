# Exercise 1.2 — Multi-Region AWS Infrastructure (Terraform)

Scalable web application infrastructure across two AWS regions
(`us-east-1` primary, `eu-west-1` secondary), built with modular Terraform:
ALB + Auto Scaling Group for the app tier, Multi-AZ RDS Postgres, and
least-privilege security groups / IAM.

> Screenshot placeholders are marked `📸 [SCREENSHOT: ...]` below — swap
> each one for an actual image (`![alt](./screenshots/filename.png)`) once
> you've run the commands and captured the consoles/CLI output.

## Architecture

```
                    ┌─────────────────────── us-east-1 (primary) ───────────────────────┐
                    │                                                                     │
  Internet ────────►│   ALB (public subnets) ──► ASG (private subnets, 2 AZ, 2–6) ──►    │
                    │                                                    │                │
                    │                                       RDS Postgres Multi-AZ         │
                    │                                       (private subnets)              │
                    └─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────── eu-west-1 (secondary) ─────────────────────┐
                    │   ALB (public subnets) ──► [app tier — extend per README notes]    │
                    └─────────────────────────────────────────────────────────────────────┘
```

## Layout

```
.
├── main.tf                  # wires modules for primary + secondary region
├── variables.tf / locals.tf / outputs.tf
├── providers.tf              # pinned versions, aws.primary / aws.secondary aliases
├── backend.tf                 # S3 + DynamoDB remote state (fill in bucket/table names)
├── environments/us-east-1/    # staging.tfvars, prod.tfvars — same code, different sizing
├── modules/
│   ├── vpc/         # VPC, public+private subnets, IGW, per-AZ NAT gateways
│   ├── security/     # ALB / app / DB security groups, least-privilege chained
│   ├── alb/            # Application Load Balancer, target group, health check
│   ├── asg/             # Launch template, Auto Scaling Group, target-tracking policies
│   ├── rds/              # Multi-AZ Postgres, Secrets Manager password, enhanced monitoring
│   └── iam/                # Instance role scoped to one secret + CloudWatch + SSM
└── docs/
    ├── README.md (this file)
    └── cost-optimization.md
```

## Prerequisites

1. AWS CLI configured with credentials that can create VPC/EC2/RDS/IAM
   resources.
2. An S3 bucket + DynamoDB table for remote state — create these once,
   then fill in `backend.tf`:
   ```bash
   aws s3api create-bucket --bucket <your-bucket> --region us-east-1
   aws s3api put-bucket-versioning --bucket <your-bucket> \
     --versioning-configuration Status=Enabled
   aws dynamodb create-table --table-name <your-lock-table> \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

## Running it

```bash
terraform init
terraform validate
terraform plan -var-file=environments/us-east-1/staging.tfvars
```

📸 `[SCREENSHOT: terraform init output — providers downloaded, backend initialized]`

📸 `[SCREENSHOT: terraform validate — "Success! The configuration is valid."]`

📸 `[SCREENSHOT: terraform plan — resource count summary at the bottom, e.g. "Plan: 42 to add, 0 to change, 0 to destroy"]`

To actually provision (will incur AWS costs — NAT Gateways, RDS, EC2 run
continuously):

```bash
terraform apply -var-file=environments/us-east-1/staging.tfvars
```

📸 `[SCREENSHOT: terraform apply completing, outputs section showing primary_alb_dns_name / primary_db_endpoint]`

📸 `[SCREENSHOT: AWS Console — VPC showing public/private subnets across 2 AZs]`

📸 `[SCREENSHOT: AWS Console — EC2 Auto Scaling Group, desired/min/max capacity]`

📸 `[SCREENSHOT: AWS Console — RDS instance detail, Multi-AZ = Yes]`

📸 `[SCREENSHOT: AWS Console — Target Group health checks passing (healthy targets)]`

Tear down when done to stop billing:

```bash
terraform destroy -var-file=environments/us-east-1/staging.tfvars
```

## Multi-region design notes

The secondary region (`eu-west-1`) deploys its own VPC, security groups,
and ALB via the `aws.secondary` provider alias — proving the multi-region
requirement — but does **not** duplicate the ASG/RDS stack. Two reasons:

1. **RDS isn't naturally multi-master.** A second *independent* Postgres
   primary in `eu-west-1` would mean two sources of truth for the same
   data. The correct pattern is an RDS **cross-region read replica**
   promoted only on failover, which is a deliberate, documented decision —
   not something to default into silently.
2. Scoping it this way keeps the exercise's resource count (and AWS bill)
   reasonable while still demonstrating provider aliasing, cross-region
   module reuse, and the ALB/VPC pattern in a second region.

To extend to full active-active: add an `rds` module call in `main.tf`
using `replicate_source_db` pointed at `module.rds_primary`, plus `asg`/
`iam` module calls under `aws.secondary`, and put both regional ALBs
behind Route 53 latency-based or failover routing.

## Security group chain

`alb` (0.0.0.0/0:80/443) → `app` (only from `alb` SG, port 5000) → `db`
(only from `app` SG, port 5432) — nothing but the ALB is reachable from the
internet, and the DB is reachable from nothing but the app tier.

📸 `[SCREENSHOT: AWS Console — Security Groups, inbound rules showing source = another SG rather than a CIDR, for app-sg and db-sg]`

See `docs/cost-optimization.md` for the tagging and sizing rationale.
