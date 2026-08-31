#!/usr/bin/env python3
"""
Self-Healing Infrastructure - Capstone Project
Enterprise DevOps Observability Platform

This module provides AI-powered self-healing capabilities for the infrastructure.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class HealingAction(Enum):
    RESTART_POD = "restart_pod"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    REBOOT_NODE = "reboot_node"
    FAILOVER = "failover"
    NOTIFY = "notify"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    value: float
    threshold: float
    timestamp: datetime
    details: Dict


@dataclass
class HealingPlan:
    action: HealingAction
    target: str
    parameters: Dict
    priority: int
    estimated_impact: str
    rollback_plan: str


class SelfHealingEngine:
    """AI-powered self-healing infrastructure engine."""

    def __init__(self):
        self.health_checks: List[HealthCheck] = []
        self.healing_history: List[Dict] = []
        self.active_healings: List[HealingPlan] = []

    def check_pod_health(self, pod_name: str, restart_count: int,
                         memory_usage: float, cpu_usage: float) -> HealthCheck:
        """Check pod health and determine if healing is needed."""
        status = HealthStatus.HEALTHY
        value = 0

        if restart_count > 5:
            status = HealthStatus.CRITICAL
            value = restart_count
        elif restart_count > 3:
            status = HealthStatus.UNHEALTHY
            value = restart_count
        elif memory_usage > 90:
            status = HealthStatus.UNHEALTHY
            value = memory_usage
        elif memory_usage > 80:
            status = HealthStatus.DEGRADED
            value = memory_usage
        elif cpu_usage > 90:
            status = HealthStatus.DEGRADED
            value = cpu_usage

        check = HealthCheck(
            name=f"pod:{pod_name}",
            status=status,
            value=value,
            threshold=5,
            timestamp=datetime.now(),
            details={
                "restart_count": restart_count,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage
            }
        )

        self.health_checks.append(check)
        return check

    def check_deployment_health(self, deployment_name: str,
                                desired_replicas: int,
                                available_replicas: int) -> HealthCheck:
        """Check deployment health."""
        availability = (available_replicas / desired_replicas * 100) if desired_replicas > 0 else 0
        status = HealthStatus.HEALTHY

        if availability < 50:
            status = HealthStatus.CRITICAL
        elif availability < 80:
            status = HealthStatus.UNHEALTHY
        elif availability < 100:
            status = HealthStatus.DEGRADED

        check = HealthCheck(
            name=f"deployment:{deployment_name}",
            status=status,
            value=availability,
            threshold=100,
            timestamp=datetime.now(),
            details={
                "desired_replicas": desired_replicas,
                "available_replicas": available_replicas
            }
        )

        self.health_checks.append(check)
        return check

    def check_node_health(self, node_name: str,
                          cpu_usage: float,
                          memory_usage: float,
                          disk_usage: float) -> HealthCheck:
        """Check node health."""
        status = HealthStatus.HEALTHY
        value = max(cpu_usage, memory_usage, disk_usage)

        if value > 95:
            status = HealthStatus.CRITICAL
        elif value > 90:
            status = HealthStatus.UNHEALTHY
        elif value > 80:
            status = HealthStatus.DEGRADED

        check = HealthCheck(
            name=f"node:{node_name}",
            status=status,
            value=value,
            threshold=90,
            timestamp=datetime.now(),
            details={
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage
            }
        )

        self.health_checks.append(check)
        return check

    def create_healing_plan(self, health_check: HealthCheck) -> Optional[HealingPlan]:
        """Create a healing plan based on health check."""
        if health_check.status == HealthStatus.HEALTHY:
            return None

        parts = health_check.name.split(":")
        resource_type = parts[0]
        resource_name = parts[1]

        if resource_type == "pod":
            if health_check.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                return HealingPlan(
                    action=HealingAction.RESTART_POD,
                    target=resource_name,
                    parameters={"force": True},
                    priority=1,
                    estimated_impact="Pod will be restarted, brief downtime",
                    rollback_plan="No rollback needed for pod restart"
                )
            elif health_check.status == HealthStatus.DEGRADED:
                return HealingPlan(
                    action=HealingAction.SCALE_UP,
                    target=resource_name,
                    parameters={"replicas": 1},
                    priority=2,
                    estimated_impact="Additional pod will be added",
                    rollback_plan="Scale down after issue is resolved"
                )

        elif resource_type == "deployment":
            if health_check.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                return HealingPlan(
                    action=HealingAction.ROLLBACK_DEPLOYMENT,
                    target=resource_name,
                    parameters={"revision": "previous"},
                    priority=1,
                    estimated_impact="Deployment will be rolled back to previous version",
                    rollback_plan="Redeploy new version after fixing issues"
                )
            elif health_check.status == HealthStatus.DEGRADED:
                return HealingPlan(
                    action=HealingAction.SCALE_UP,
                    target=resource_name,
                    parameters={"replicas": 2},
                    priority=2,
                    estimated_impact="Additional replicas will be added",
                    rollback_plan="Scale down after issue is resolved"
                )

        elif resource_type == "node":
            if health_check.status == HealthStatus.CRITICAL:
                return HealingPlan(
                    action=HealingAction.FAILOVER,
                    target=resource_name,
                    parameters={"drain": True, "cordon": True},
                    priority=1,
                    estimated_impact="Workloads will be moved to other nodes",
                    rollback_plan="Uncordon and rejoin node after fix"
                )
            elif health_check.status == HealthStatus.UNHEALTHY:
                return HealingPlan(
                    action=HealingAction.REBOOT_NODE,
                    target=resource_name,
                    parameters={"graceful": True},
                    priority=2,
                    estimated_impact="Node will be rebooted",
                    rollback_plan="No rollback needed"
                )

        return None

    def execute_healing_plan(self, plan: HealingPlan) -> Dict:
        """Execute a healing plan."""
        result = {
            "plan": plan.__dict__,
            "start_time": datetime.now().isoformat(),
            "status": "executing",
            "actions_taken": []
        }

        print(f"Executing healing plan: {plan.action.value} on {plan.target}")

        if plan.action == HealingAction.RESTART_POD:
            result["actions_taken"].append(f"Restarting pod {plan.target}")
            print(f"  -> Restarting pod {plan.target}")

        elif plan.action == HealingAction.SCALE_UP:
            result["actions_taken"].append(f"Scaling up {plan.target}")
            print(f"  -> Scaling up {plan.target}")

        elif plan.action == HealingAction.ROLLBACK_DEPLOYMENT:
            result["actions_taken"].append(f"Rolling back deployment {plan.target}")
            print(f"  -> Rolling back deployment {plan.target}")

        elif plan.action == HealingAction.REBOOT_NODE:
            result["actions_taken"].append(f"Rebooting node {plan.target}")
            print(f"  -> Rebooting node {plan.target}")

        elif plan.action == HealingAction.FAILOVER:
            result["actions_taken"].append(f"Failing over from node {plan.target}")
            print(f"  -> Failing over from node {plan.target}")

        result["status"] = "completed"
        result["end_time"] = datetime.now().isoformat()

        self.healing_history.append(result)
        return result

    def get_healing_recommendations(self) -> List[Dict]:
        """Get healing recommendations based on current health checks."""
        recommendations = []

        for check in self.health_checks:
            if check.status != HealthStatus.HEALTHY:
                plan = self.create_healing_plan(check)
                if plan:
                    recommendations.append({
                        "health_check": check.__dict__,
                        "healing_plan": plan.__dict__,
                        "priority": plan.priority
                    })

        recommendations.sort(key=lambda x: x["priority"])
        return recommendations

    def generate_report(self) -> Dict:
        """Generate a comprehensive healing report."""
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }

        for check in self.health_checks:
            status_counts[check.status] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.health_checks),
            "status_breakdown": {s.value: c for s, c in status_counts.items()},
            "active_healings": len(self.active_healings),
            "completed_healings": len(self.healing_history),
            "recommendations": self.get_healing_recommendations()
        }


def main():
    """Main function to demonstrate self-healing capabilities."""
    engine = SelfHealingEngine()

    print("=== Self-Healing Infrastructure Engine ===\n")

    # Simulate pod health checks
    print("1. Checking Pod Health...")
    pod_check1 = engine.check_pod_health("api-gateway-abc123", 6, 45.2, 35.8)
    pod_check2 = engine.check_pod_health("auth-service-def456", 2, 85.3, 42.1)
    pod_check3 = engine.check_pod_health("user-service-ghi789", 0, 25.4, 15.2)
    print(f"   Pod api-gateway: {pod_check1.status.value}")
    print(f"   Pod auth-service: {pod_check2.status.value}")
    print(f"   Pod user-service: {pod_check3.status.value}\n")

    # Simulate deployment health checks
    print("2. Checking Deployment Health...")
    deploy_check1 = engine.check_deployment_health("api-gateway", 5, 3)
    deploy_check2 = engine.check_deployment_health("auth-service", 3, 3)
    print(f"   Deployment api-gateway: {deploy_check1.status.value} ({deploy_check1.value:.1f}%)")
    print(f"   Deployment auth-service: {deploy_check2.status.value} ({deploy_check2.value:.1f}%)\n")

    # Simulate node health checks
    print("3. Checking Node Health...")
    node_check1 = engine.check_node_health("node-1", 92.5, 88.3, 75.2)
    node_check2 = engine.check_node_health("node-2", 45.2, 52.1, 42.8)
    print(f"   Node node-1: {node_check1.status.value}")
    print(f"   Node node-2: {node_check2.status.value}\n")

    # Create healing plans
    print("4. Creating Healing Plans...")
    for check in engine.health_checks:
        if check.status != HealthStatus.HEALTHY:
            plan = engine.create_healing_plan(check)
            if plan:
                engine.active_healings.append(plan)
                print(f"   Plan for {check.name}: {plan.action.value}")

    # Execute healing plans
    print("\n5. Executing Healing Plans...")
    for plan in engine.active_healings[:2]:  # Execute first 2 plans
        result = engine.execute_healing_plan(plan)
        print(f"   Completed: {result['status']}\n")

    # Generate report
    print("6. Generating Report...")
    report = engine.generate_report()
    print(f"   Total checks: {report['total_checks']}")
    print(f"   Status breakdown: {report['status_breakdown']}")
    print(f"   Completed healings: {report['completed_healings']}")
    print(f"   Recommendations: {len(report['recommendations'])}\n")

    # Save report
    with open("healing_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("Report saved to healing_report.json")


if __name__ == "__main__":
    main()
