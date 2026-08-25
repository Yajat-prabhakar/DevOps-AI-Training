# Cost Optimization & Tagging Strategy — Exercise 1.2

## Tagging

Every resource gets `local.common_tags` via `default_tags` on both provider
aliases, so tags don't have to be repeated per-resource and can't drift:

| Tag | Purpose |
|---|---|
| `Project` | Groups resources for a Cost Explorer filter across environments |
| `Environment` | Separates dev/staging/prod spend |
| `Owner` | Who to page/bill when the AWS bill has a surprise |
| `ManagedBy=terraform` | Flags anything *without* this tag as manual/drifted |
| `CostCenter` | `<project>-<environment>`, ready for a Cost Explorer cost-allocation tag |

Activate `Project`, `Environment`, `Owner`, and `CostCenter` as
cost-allocation tags in Billing → Cost Allocation Tags (takes ~24h to
populate) — screenshot that dashboard once tags show real cost data.

## Instance sizing

- **staging**: `t3.micro` app instances, `db.t3.medium` — burstable
  (T-family) instances are the cheapest way to run a low, spiky-traffic
  environment, since you pay baseline and burst on CPU credits rather than
  a full vCPU reservation.
- **prod**: `t3.small` / `db.t3.large` — one size up, chosen from expected
  sustained load, not copy-pasted from staging. Re-evaluate with real
  CloudWatch CPU/memory data after a couple of weeks rather than guessing
  further.

## Autoscaling instead of static fleets

The ASG's target-tracking policies (60% CPU, 1000 req/target) mean you pay
for `desired_capacity` most of the time and only pay for burst capacity
during actual load, instead of provisioning `max_size` permanently. `min_size
= 2` keeps a spare for AZ failure; going to `min_size = 1` would save more
but drops the safety margin — a tradeoff to state explicitly, not default
into.

## Storage

- `gp3` over `gp2` for RDS: same baseline performance at lower cost per GB,
  and IOPS/throughput are provisioned independently instead of scaling with
  volume size.
- `max_allocated_storage` enables RDS storage autoscaling so you provision
  for today's data, not a guessed ceiling three years out.

## NAT Gateway cost note

This design uses one NAT Gateway per AZ (in `modules/vpc`) for
availability — each NAT Gateway has an hourly charge plus per-GB data
processing. For a lower-cost dev environment, a single shared NAT Gateway
(one AZ) is a reasonable tradeoff; call it out explicitly in a `dev.tfvars`
if you add one, rather than silently downgrading availability everywhere.

## What to screenshot for the README

1. `terraform plan` output (resource count, no errors) — proves the config
   is valid and shows exactly what would be created.
2. AWS Cost Explorer filtered by the `Project` tag, once resources exist.
3. The target-tracking scaling policy and a scaling event in the EC2 →
   Auto Scaling console.
4. RDS console showing Multi-AZ = Yes and encrypted storage.
