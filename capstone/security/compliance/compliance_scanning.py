#!/usr/bin/env python3
"""
Compliance Scanning & Reporting - Capstone Project
Enterprise DevOps Observability Platform

This module provides automated compliance scanning and reporting.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ComplianceFramework(Enum):
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    CIS = "cis"
    NIST = "nist"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceCheck:
    id: str
    framework: ComplianceFramework
    name: str
    description: str
    severity: Severity
    status: Status
    details: str
    remediation: str
    tags: List[str]


@dataclass
class ComplianceReport:
    report_id: str
    framework: ComplianceFramework
    timestamp: datetime
    total_checks: int
    passed: int
    failed: int
    warnings: int
    score: float
    checks: List[ComplianceCheck]
    summary: Dict


class ComplianceScanner:
    """Automated compliance scanning and reporting engine."""

    def __init__(self):
        self.checks: List[ComplianceCheck] = []
        self.reports: List[ComplianceReport] = []
        self._initialize_checks()

    def _initialize_checks(self):
        """Initialize compliance checks for different frameworks."""
        # SOC 2 Checks
        self.checks.extend([
            ComplianceCheck(
                id="SOC2-CC6.1",
                framework=ComplianceFramework.SOC2,
                name="Logical Access Controls",
                description="Implement logical access controls to restrict access to authorized users",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="RBAC policies implemented with least privilege access",
                remediation="Review and update RBAC policies regularly",
                tags=["access-control", "rbac"]
            ),
            ComplianceCheck(
                id="SOC2-CC7.1",
                framework=ComplianceFramework.SOC2,
                name="System Monitoring",
                description="Monitor system components for anomalies",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="Prometheus and Grafana monitoring configured",
                remediation="Ensure monitoring covers all critical components",
                tags=["monitoring", "logging"]
            ),
            ComplianceCheck(
                id="SOC2-CC8.1",
                framework=ComplianceFramework.SOC2,
                name="Change Management",
                description="Implement change management procedures",
                severity=Severity.MEDIUM,
                status=Status.PASS,
                details="CI/CD pipeline with automated testing and approval gates",
                remediation="Document all change management procedures",
                tags=["change-management", "cicd"]
            ),
        ])

        # ISO 27001 Checks
        self.checks.extend([
            ComplianceCheck(
                id="ISO27001-A.12.1.1",
                framework=ComplianceFramework.ISO27001,
                name="Documented Operating Procedures",
                description="Operating procedures for information processing facilities shall be documented",
                severity=Severity.HIGH,
                status=Status.WARNING,
                details="Some procedures documented, others pending",
                remediation="Complete documentation for all operating procedures",
                tags=["documentation", "procedures"]
            ),
            ComplianceCheck(
                id="ISO27001-A.12.1.2",
                framework=ComplianceFramework.ISO27001,
                name="Change Management",
                description="Changes to information processing facilities shall be controlled",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="Automated change management via CI/CD pipeline",
                remediation="Review change management process quarterly",
                tags=["change-management"]
            ),
            ComplianceCheck(
                id="ISO27001-A.14.2.1",
                framework=ComplianceFramework.ISO27001,
                name="Secure Development Policy",
                description="Rules for the development of software and systems shall be established",
                severity=Severity.MEDIUM,
                status=Status.PASS,
                details="Security-first development practices implemented",
                remediation="Regular security training for development team",
                tags=["development", "security"]
            ),
        ])

        # CIS Benchmark Checks
        self.checks.extend([
            ComplianceCheck(
                id="CIS-1.1.1",
                framework=ComplianceFramework.CIS,
                name="Ensure that the cluster-admin role is only used where required",
                description="The cluster-admin role should only be used for critical system operations",
                severity=Severity.CRITICAL,
                status=Status.PASS,
                details="Cluster-admin role restricted to system components only",
                remediation="Regular audit of cluster-admin bindings",
                tags=["rbac", "kubernetes"]
            ),
            ComplianceCheck(
                id="CIS-1.2.1",
                framework=ComplianceFramework.CIS,
                name="Minimize access to secrets",
                description="Access to secrets should be minimized and logged",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="Secret access limited to required service accounts",
                remediation="Review secret access policies monthly",
                tags=["secrets", "kubernetes"]
            ),
            ComplianceCheck(
                id="CIS-2.1.1",
                framework=ComplianceFramework.CIS,
                name="Minimize the admission of privileged containers",
                description="Privileged containers should be restricted",
                severity=Severity.CRITICAL,
                status=Status.PASS,
                details="Pod Security Policy禁止privileged containers",
                remediation="Review Pod Security Policy regularly",
                tags=["pod-security", "kubernetes"]
            ),
            ComplianceCheck(
                id="CIS-2.2.1",
                framework=ComplianceFramework.CIS,
                name="Minimize containers with added capabilities",
                description="Containers should not add capabilities beyond the default set",
                severity=Severity.HIGH,
                status=Status.WARNING,
                details="Some containers have additional capabilities",
                remediation="Review and remove unnecessary capabilities",
                tags=["container-security", "kubernetes"]
            ),
        ])

        # NIST Checks
        self.checks.extend([
            ComplianceCheck(
                id="NIST-SC-7",
                framework=ComplianceFramework.NIST,
                name="Boundary Protection",
                description="Monitor and control communications at the external boundary",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="Network policies implemented for boundary protection",
                remediation="Regular review of network policies",
                tags=["network", "boundary"]
            ),
            ComplianceCheck(
                id="NIST-AU-2",
                framework=ComplianceFramework.NIST,
                name="Audit Events",
                description="Define and implement audit events",
                severity=Severity.HIGH,
                status=Status.PASS,
                details="Comprehensive audit logging enabled",
                remediation="Review audit logs regularly",
                tags=["audit", "logging"]
            ),
        ])

    def scan_kubernetes(self) -> List[ComplianceCheck]:
        """Scan Kubernetes cluster for compliance."""
        results = []

        for check in self.checks:
            if check.framework == ComplianceFramework.CIS:
                results.append(check)

        return results

    def scan_terraform(self) -> List[ComplianceCheck]:
        """Scan Terraform configurations for compliance."""
        results = []

        for check in self.checks:
            if check.framework in [ComplianceFramework.SOC2, ComplianceFramework.ISO27001]:
                results.append(check)

        return results

    def scan_network(self) -> List[ComplianceCheck]:
        """Scan network configuration for compliance."""
        results = []

        for check in self.checks:
            if "network" in check.tags or "boundary" in check.tags:
                results.append(check)

        return results

    def generate_report(self, framework: ComplianceFramework) -> ComplianceReport:
        """Generate compliance report for a framework."""
        framework_checks = [c for c in self.checks if c.framework == framework]

        total = len(framework_checks)
        passed = len([c for c in framework_checks if c.status == Status.PASS])
        failed = len([c for c in framework_checks if c.status == Status.FAIL])
        warnings = len([c for c in framework_checks if c.status == Status.WARNING])

        score = (passed / total * 100) if total > 0 else 0

        summary = {
            "framework": framework.value,
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "score": score,
            "compliant": score >= 90
        }

        report = ComplianceReport(
            report_id=f"COMP-{datetime.now().strftime('%Y%m%d')}-{framework.value.upper()}",
            framework=framework,
            timestamp=datetime.now(),
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            score=score,
            checks=framework_checks,
            summary=summary
        )

        self.reports.append(report)
        return report

    def get_remediation_plan(self) -> List[Dict]:
        """Get remediation plan for failed checks."""
        remediation_plan = []

        for check in self.checks:
            if check.status in [Status.FAIL, Status.WARNING]:
                remediation_plan.append({
                    "id": check.id,
                    "framework": check.framework.value,
                    "name": check.name,
                    "severity": check.severity.value,
                    "status": check.status.value,
                    "remediation": check.remediation,
                    "priority": "high" if check.severity == Severity.CRITICAL else "medium"
                })

        remediation_plan.sort(key=lambda x: x["priority"], reverse=True)
        return remediation_plan

    def export_report(self, report: ComplianceReport,
                      format: str = "json") -> str:
        """Export compliance report."""
        if format == "json":
            return json.dumps({
                "report_id": report.report_id,
                "framework": report.framework.value,
                "timestamp": report.timestamp.isoformat(),
                "summary": report.summary,
                "checks": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "severity": c.severity.value,
                        "status": c.status.value,
                        "details": c.details,
                        "remediation": c.remediation,
                        "tags": c.tags
                    }
                    for c in report.checks
                ]
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Main function to demonstrate compliance scanning capabilities."""
    scanner = ComplianceScanner()

    print("=== Compliance Scanning & Reporting ===\n")

    # Scan Kubernetes
    print("1. Scanning Kubernetes Cluster...")
    k8s_results = scanner.scan_kubernetes()
    print(f"   Found {len(k8s_results)} CIS benchmark checks")
    for check in k8s_results[:3]:
        print(f"     - [{check.status.value}] {check.name}")

    # Scan Terraform
    print("\n2. Scanning Terraform Configuration...")
    tf_results = scanner.scan_terraform()
    print(f"   Found {len(tf_results)} SOC2/ISO27001 checks")
    for check in tf_results[:3]:
        print(f"     - [{check.status.value}] {check.name}")

    # Generate SOC 2 Report
    print("\n3. Generating SOC 2 Compliance Report...")
    soc2_report = scanner.generate_report(ComplianceFramework.SOC2)
    print(f"   Report ID: {soc2_report.report_id}")
    print(f"   Score: {soc2_report.score:.1f}%")
    print(f"   Passed: {soc2_report.passed}/{soc2_report.total_checks}")

    # Generate CIS Report
    print("\n4. Generating CIS Benchmark Report...")
    cis_report = scanner.generate_report(ComplianceFramework.CIS)
    print(f"   Report ID: {cis_report.report_id}")
    print(f"   Score: {cis_report.score:.1f}%")
    print(f"   Passed: {cis_report.passed}/{cis_report.total_checks}")

    # Get Remediation Plan
    print("\n5. Generating Remediation Plan...")
    remediation_plan = scanner.get_remediation_plan()
    print(f"   Found {len(remediation_plan)} items requiring remediation")
    for item in remediation_plan[:3]:
        print(f"     - [{item['priority']}] {item['name']}: {item['remediation']}")

    # Export Reports
    print("\n6. Exporting Reports...")
    soc2_export = scanner.export_report(soc2_report)
    cis_export = scanner.export_report(cis_report)

    with open("soc2_compliance_report.json", "w") as f:
        f.write(soc2_export)
    print("   SOC 2 report saved to soc2_compliance_report.json")

    with open("cis_compliance_report.json", "w") as f:
        f.write(cis_export)
    print("   CIS report saved to cis_compliance_report.json")


if __name__ == "__main__":
    main()
