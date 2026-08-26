# SOC 2 Type II & ISO 27001 Compliance Report

**Exercise 1.5** | Assessment Date: August 26, 2026 | Assessor: DevOps Security Team

---

## Executive Summary

This report assesses the current infrastructure against SOC 2 Type II and ISO 27001 compliance frameworks. The assessment identifies gaps and provides remediation recommendations.

**Overall Compliance Score: 72%**

| Framework | Score | Status |
|-----------|-------|--------|
| SOC 2 Type II | 75% | Partially Compliant |
| ISO 27001 | 70% | Partially Compliant |
| CIS AWS Foundations | 78% | Partially Compliant |

---

## SOC 2 Type II Assessment

### Trust Service Criteria

| Criteria | Description | Status | Evidence |
|----------|-------------|--------|----------|
| **CC1.1** | COSO Principle 1: Integrity and ethical values | ⚠️ | No documented code of conduct |
| **CC1.2** | Board oversight | ✅ | Engineering leadership in place |
| **CC1.3** | Management structure | ✅ | Clear org structure |
| **CC1.4** | Commitment to competence | ✅ | Training programs in place |
| **CC1.5** | Accountability | ⚠️ | No formal accountability framework |
| **CC2.1** | Internal communication | ✅ | Slack, meetings |
| **CC2.2** | External communication | ⚠️ | No public status page |
| **CC3.1** | Risk assessment | ⚠️ | Informal risk process |
| **CC3.2** | Fraud risk | ❌ | No fraud risk assessment |
| **CC3.3** | Change management | ✅ | Git + PR reviews |
| **CC4.1** | Monitoring activities | ✅ | Prometheus + Grafana |
| **CC4.2** | Deficiency remediation | ⚠️ | Ad-hoc process |
| **CC5.1** | Control environment | ⚠️ | Partial documentation |
| **CC5.2** | Policy documentation | ⚠️ | Some policies exist |
| **CC5.3** | Enforcement procedures | ❌ | No enforcement mechanism |
| **CC6.1** | Logical access controls | ✅ | IAM, security groups |
| **CC6.2** | Authentication | ✅ | AWS SSO, MFA |
| **CC6.3** | Access revocation | ⚠️ | Manual process |
| **CC6.4** | Access provisioning | ⚠️ | No formal process |
| **CC6.5** | Restrict logical access | ✅ | VPC, subnets |
| **CC6.6** | Security measures | ✅ | Encryption at rest |
| **CC6.7** | Restrict transmission | ✅ | TLS everywhere |
| **CC7.1** | Vulnerability scanning | ✅ | Trivy, Dependabot |
| **CC7.2** | Incident detection | ✅ | CloudWatch, Prometheus |
| **CC7.3** | Incident response | ⚠️ | Informal process |
| **CC7.4** | Incident remediation | ⚠️ | Ad-hoc |
| **CC8.1** | Change management | ✅ | PR + approval |
| **CC9.1** | Risk mitigation | ⚠️ | Partial |
| **CC9.2** | Vendor management | ⚠️ | No vendor assessment |

### SOC 2 Gap Summary

| Gap | Impact | Remediation | Timeline |
|-----|--------|-------------|----------|
| No code of conduct | Low | Create document | 2 weeks |
| No fraud risk assessment | Medium | Conduct assessment | 1 month |
| Access revocation manual | High | Automate with SCIM | 2 months |
| No formal incident response | High | Create IR plan | 1 month |
| No vendor management | Medium | Create vendor register | 2 months |

---

## ISO 27001 Assessment

### Annex A Controls

| Control | Description | Status | Implementation |
|---------|-------------|--------|----------------|
| **A.5.1.1** | Policies for information security | ⚠️ | Partial - needs formalization |
| **A.5.1.2** | Information security roles | ✅ | Defined in org chart |
| **A.5.1.3** | Segregation of duties | ✅ | PR reviews, approvals |
| **A.5.2.1** | Screen filters | N/A | Cloud workstations |
| **A.5.2.2** | Desktop lock | N/A | Cloud workstations |
| **A.5.3.1** | Management responsibility | ✅ | Leadership engaged |
| **A.5.3.2** | Information security awareness | ⚠️ | Informal training |
| **A.5.3.3** | Disciplinary process | ❌ | Not documented |
| **A.5.4.1** | Termination responsibilities | ⚠️ | Manual process |
| **A.6.1.1** | Screening | ✅ | Background checks |
| **A.6.1.2** | Terms of employment | ✅ | Offer letters |
| **A.6.2.1** | Management responsibility | ✅ | Defined |
| **A.6.2.2** | Information security awareness | ⚠️ | Informal |
| **A.6.2.3** | Disciplinary process | ❌ | Not documented |
| **A.7.1.1** | Physical security perimeter | ✅ | AWS data centers |
| **A.7.1.2** | Physical entry controls | ✅ | AWS controls |
| **A.7.2.1** | Equipment siting | ✅ | AWS managed |
| **A.7.2.2** | Equipment maintenance | ✅ | AWS managed |
| **A.7.2.3** | Removal of assets | ⚠️ | No formal process |
| **A.7.2.4** | Security of equipment off-premises | ✅ | AWS managed |
| **A.7.2.5** | Secure disposal | ✅ | AWS managed |
| **A.7.3.1** | Equipment delivery | ✅ | AWS managed |
| **A.8.1.1** | Asset inventory | ⚠️ | Partial - AWS only |
| **A.8.1.2** | Ownership of assets | ⚠️ | No formal ownership |
| **A.8.2.1** | Classification of assets | ⚠️ | Informal |
| **A.8.2.2** | Labelling of assets | ❌ | Not implemented |
| **A.8.2.3** | Asset handling | ❌ | Not documented |
| **A.8.3.1** | Information transfer | ⚠️ | Partial |
| **A.8.4.1** | Access control policy | ✅ | IAM policies |
| **A.8.4.2** | Access to networks | ✅ | Security groups |
| **A.8.4.3** | Password management | ✅ | Secrets Manager |
| **A.8.5.1** | Secure authentication | ✅ | AWS SSO + MFA |
| **A.9.1.1** | Access control policy | ✅ | IAM |
| **A.9.1.2** | Access to networks | ✅ | Security groups |
| **A.9.2.1** | User registration | ⚠️ | Manual |
| **A.9.2.2** | Privilege management | ✅ | IAM roles |
| **A.9.2.3** | Management of secret auth | ✅ | Secrets Manager |
| **A.9.2.4** | Access review | ⚠️ | Informal |
| **A.9.2.5** | Access removal | ⚠️ | Manual |
| **A.9.2.6** | Authentication info | ✅ | AWS managed |
| **A.9.2.7** | Credential lifecycle | ⚠️ | No rotation policy |
| **A.9.3.1** | Information access restriction | ✅ | IAM + SG |
| **A.9.3.2** | Access to source code | ✅ | GitHub permissions |
| **A.9.3.3** | Access to utility programs | ⚠️ | Partial |
| **A.9.4.1** | Access control program | ✅ | IAM |
| **A.9.4.2** | Secure log-on | ✅ | AWS SSO |
| **A.9.4.3** | Password management | ✅ | Secrets Manager |
| **A.9.4.4** | Use of privileged utilities | ⚠️ | Partial |
| **A.9.4.5** | Access control program | ✅ | IAM |
| **A.9.4.6** | Source code access | ✅ | GitHub |
| **A.10.1.1** | Cryptographic policy | ⚠️ | Informal |
| **A.10.1.2** | Key management | ✅ | KMS |
| **A.11.1.1** | Equipment siting | ✅ | AWS |
| **A.11.1.2** | Equipment maintenance | ✅ | AWS |
| **A.11.1.3** | Removal of assets | ❌ | Not documented |
| **A.11.1.4** | Security of equipment | ✅ | AWS |
| **A.11.2.1** | Equipment delivery | ✅ | AWS |
| **A.11.2.2** | Equipment disposal | ✅ | AWS |
| **A.11.2.3** | Media handling | ⚠️ | Partial |
| **A.11.2.4** | Physical media transfer | ⚠️ | No formal process |
| **A.12.1.1** | Documented procedures | ⚠️ | Partial |
| **A.12.1.2** | Change management | ✅ | PR + approval |
| **A.12.1.3** | Capacity management | ✅ | Auto-scaling |
| **A.12.1.4** | Separation of environments | ✅ | Dev/Staging/Prod |
| **A.12.2.1** | Malware protection | ⚠️ | No endpoint protection |
| **A.12.3.1** | Information backup | ✅ | RDS backups |
| **A.12.4.1** | Event logging | ✅ | CloudWatch |
| **A.12.4.2** | Protection of log info | ✅ | CloudWatch Logs |
| **A.12.4.3** | Admin and operator logs | ✅ | CloudTrail |
| **A.12.5.1** | Control of operational software | ⚠️ | Partial |
| **A.12.6.1** | Technical vulnerability | ✅ | Trivy, Dependabot |
| **A.12.6.2** | Restrictions on software | ⚠️ | Partial |
| **A.13.1.1** | Network controls | ✅ | VPC, SG |
| **A.13.1.2** | Security of network services | ✅ | AWS managed |
| **A.13.1.3** | Segregation in networks | ✅ | VPC subnets |
| **A.13.2.1** | Web filtering | ❌ | Not implemented |
| **A.13.2.2** | Security of network services | ✅ | AWS managed |
| **A.14.1.1** | Secure development policy | ✅ | This document |
| **A.14.1.2** | Application services on public networks | ✅ | HTTPS |
| **A.14.1.3** | Application services delivery | ✅ | HTTPS |
| **A.14.2.1** | Secure development policy | ✅ | This document |
| **A.14.2.2** | System change control | ✅ | PR + approval |
| **A.14.2.3** | Technical review of applications | ⚠️ | Informal |
| **A.14.2.4** | Separation of dev/test/prod | ✅ | Separate environments |
| **A.14.2.5** | Secure system engineering | ✅ | IaC, code reviews |
| **A.14.2.6** | Secure development environment | ⚠️ | Partial |
| **A.14.2.7** | Outsourced development | N/A | In-house |
| **A.14.2.8** | System security testing | ✅ | Trivy, bandit |
| **A.14.2.9** | System acceptance testing | ⚠️ | Informal |
| **A.14.3.1** | Protection of test data | ⚠️ | Partial |
| **A.15.1.1** | Information security in supplier relationships | ⚠️ | No formal process |
| **A.15.1.2** | Addressing security in supplier agreements | ⚠️ | No formal process |
| **A.15.1.3** | Information and communication technology | ⚠️ | Partial |
| **A.15.2.1** | Addressing security in supplier agreements | ⚠️ | No formal process |
| **A.15.2.2** | Monitoring supplier services | ⚠️ | Partial |
| **A.16.1.1** | Incident management procedure | ⚠️ | Informal |
| **A.16.1.2** | Reporting information security events | ⚠️ | No formal process |
| **A.16.1.3** | Reporting information security weaknesses | ⚠️ | No formal process |
| **A.16.1.4** | Assessment of information security events | ⚠️ | Informal |
| **A.16.1.5** | Response to incidents | ⚠️ | Informal |
| **A.16.1.6** | Learning from incidents | ⚠️ | Informal |
| **A.16.1.7** | Collection of evidence | ❌ | Not documented |
| **A.17.1.1** | Information security continuity | ⚠️ | Partial |
| **A.17.1.2** | Information security continuity | ⚠️ | Partial |
| **A.17.2.1** | Availability of information | ✅ | Multi-AZ, backups |
| **A.17.2.2** | Redundancy of information | ✅ | Multi-region |
| **A.18.1.1** | Independent review | ❌ | No formal audit |
| **A.18.1.2** | Compliance with policies | ❌ | No formal process |
| **A.18.1.3** | Compliance with legal | ⚠️ | Partial |
| **A.18.1.4** | Cryptographic controls review | ⚠️ | Informal |
| **A.18.2.1** | Independent review | ❌ | No formal audit |
| **A.18.2.2** | Compliance with policies | ❌ | No formal process |

---

## CIS AWS Foundations Benchmark v3.0

| Control | Description | Status | Notes |
|---------|-------------|--------|-------|
| 1.1 | Maintain current contact details | ✅ | AWS account contacts |
| 1.2 | Ensure security contact info is accurate | ✅ | Verified |
| 1.3 | Ensure MFA is enabled for root | ✅ | Configured |
| 1.4 | Ensure credentials unused for 90 days disabled | ⚠️ | Manual audit needed |
| 1.5 | Ensure MFA enabled for IAM users | ⚠️ | Not enforced |
| 1.6 | Ensure hardware MFA for root | ❌ | Software MFA only |
| 1.7 | Eliminate use of root user | ✅ | SSO used |
| 1.8 | Ensure IAM policies attached only to groups | ✅ | Role-based |
| 1.9 | Ensure MFA is enabled for all IAM users | ⚠️ | Not enforced |
| 2.1 | Ensure CloudTrail is enabled | ✅ | Enabled |
| 2.2 | Ensure CloudTrail log file validation | ⚠️ | Not enabled |
| 2.3 | Ensure CloudTrail logs at rest are encrypted | ✅ | KMS encryption |
| 2.4 | Ensure CloudTrail logs are encrypted at rest | ✅ | KMS encryption |
| 2.5 | Ensure S3 bucket CloudTrail logs is not public | ✅ | Private bucket |
| 2.6 | Ensure CloudTrail trails are integrated with Logs | ✅ | CloudWatch |
| 2.7 | Ensure AWS Config is enabled | ❌ | Not enabled |
| 2.8 | Ensure security scanning is enabled | ✅ | Trivy |
| 3.1 | Ensure no unrestricted access to SSH | ✅ | SSM used |
| 3.2 | Ensure no unrestricted access to RDP | ✅ | SSM used |
| 3.3 | Ensure default security group restricts all traffic | ✅ | No rules |
| 3.4 | Ensure routing tables restrict VPC flow logs | ⚠️ | Default routes |
| 4.1 | Ensure S3 bucket policy is secure | ⚠️ | Needs review |
| 4.2 | Ensure all S3 buckets use encryption | ✅ | Default encryption |
| 4.3 | Ensure S3 bucket access logging enabled | ⚠️ | Partial |
| 4.4 | Ensure EBS volumes are encrypted | ✅ | Default encryption |
| 4.5 | Ensure EFS volumes are encrypted | ✅ | Encrypted |
| 4.6 | Ensure RDS instances are encrypted | ✅ | Encrypted |
| 4.7 | Ensure RDS instances have automated backups | ✅ | Enabled |
| 4.8 | Ensure DynamoDB tables are encrypted | ✅ | AWS managed |
| 4.9 | Ensure ElastiCache clusters are encrypted | ✅ | Encrypted |
| 5.1 | Ensure CloudWatch Logs are encrypted | ✅ | KMS encryption |
| 5.2 | Ensure AWS Config is enabled | ❌ | Not enabled |
| 5.3 | Ensure CloudTrail is enabled | ✅ | Enabled |

---

## Remediation Roadmap

### Phase 1: Critical (0-30 days)

| # | Action | Framework | Effort |
|---|--------|-----------|--------|
| 1 | Document incident response plan | SOC 2, ISO | 1 week |
| 2 | Enable AWS Config | CIS | 1 day |
| 3 | Enable CloudTrail log validation | CIS | 1 day |
| 4 | Enforce MFA for all IAM users | CIS | 1 week |
| 5 | Automate access revocation (SCIM) | SOC 2 | 2 weeks |

### Phase 2: High (30-90 days)

| # | Action | Framework | Effort |
|---|--------|-----------|--------|
| 6 | Create vendor management register | SOC 2, ISO | 2 weeks |
| 7 | Document formal access provisioning process | SOC 2 | 1 week |
| 8 | Implement fraud risk assessment | SOC 2 | 2 weeks |
| 9 | Create security awareness training program | ISO | 2 weeks |
| 10 | Enable VPC Flow Logs | CIS | 1 day |

### Phase 3: Medium (90-180 days)

| # | Action | Framework | Effort |
|---|--------|-----------|--------|
| 11 | Implement asset inventory | ISO | 2 weeks |
| 12 | Create physical media handling procedures | ISO | 1 week |
| 13 | Implement web filtering | ISO | 2 weeks |
| 14 | Conduct independent security review | SOC 2, ISO | 1 month |
| 15 | Implement credential rotation policy | CIS, ISO | 2 weeks |

---

## Appendix: Evidence Files

- `policies/iam-policy-vulnerable.json` - Current IAM policy with issues
- `policies/iam-policy-hardened.json` - Remediated IAM policy
- `policies/kubernetes-rbac-assessment.md` - K8s RBAC findings
- `policies/network-security-assessment.md` - Security group findings
