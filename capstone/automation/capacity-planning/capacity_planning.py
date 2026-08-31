#!/usr/bin/env python3
"""
Capacity Planning & Cost Optimization - Capstone Project
Enterprise DevOps Observability Platform

This module provides AI-powered capacity planning and cost optimization.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Resource(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PODS = "pods"


class ScalingRecommendation(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    OPTIMIZE = "optimize"
    MIGRATE = "migrate"
    CONSOLIDATE = "consolidate"


@dataclass
class ResourceUsage:
    resource: Resource
    current_usage: float
    average_usage: float
    peak_usage: float
    forecast_usage: float
    unit: str
    cost_per_unit: float


@dataclass
class ScalingPlan:
    resource: Resource
    recommendation: ScalingRecommendation
    current_capacity: float
    recommended_capacity: float
    estimated_savings: float
    implementation_steps: List[str]
    risk_level: str


@dataclass
class CostOptimization:
    resource: Resource
    current_cost: float
    optimized_cost: float
    savings: float
    savings_percentage: float
    optimization_method: str
    implementation_effort: str


class CapacityPlanningEngine:
    """AI-powered capacity planning and cost optimization engine."""

    def __init__(self):
        self.resource_usage: List[ResourceUsage] = []
        self.scaling_plans: List[ScalingPlan] = []
        self.cost_optimizations: List[CostOptimization] = []
        self.forecast_days = 30

    def analyze_resource_usage(self, resource: Resource,
                                current: float, average: float,
                                peak: float, unit: str,
                                cost_per_unit: float) -> ResourceUsage:
        """Analyze resource usage and generate forecast."""
        # Simple linear forecast
        trend = (peak - average) / average if average > 0 else 0
        forecast = current * (1 + trend * 0.1)  # 10% of trend per period

        usage = ResourceUsage(
            resource=resource,
            current_usage=current,
            average_usage=average,
            peak_usage=peak,
            forecast_usage=forecast,
            unit=unit,
            cost_per_unit=cost_per_unit
        )

        self.resource_usage.append(usage)
        return usage

    def generate_scaling_plan(self, usage: ResourceUsage,
                               target_utilization: float = 70.0) -> ScalingPlan:
        """Generate scaling plan based on resource usage."""
        current_capacity = usage.peak_usage
        recommended_capacity = usage.forecast_usage / (target_utilization / 100)

        if usage.forecast_usage > current_capacity * 0.9:
            recommendation = ScalingRecommendation.SCALE_UP
            estimated_savings = 0
            risk_level = "low"
        elif usage.average_usage < current_capacity * 0.3:
            recommendation = ScalingRecommendation.SCALE_DOWN
            estimated_savings = (current_capacity - recommended_capacity) * usage.cost_per_unit
            risk_level = "medium"
        else:
            recommendation = ScalingRecommendation.OPTIMIZE
            estimated_savings = current_capacity * 0.1 * usage.cost_per_unit
            risk_level = "low"

        implementation_steps = self._get_implementation_steps(
            recommendation, usage.resource
        )

        plan = ScalingPlan(
            resource=usage.resource,
            recommendation=recommendation,
            current_capacity=current_capacity,
            recommended_capacity=recommended_capacity,
            estimated_savings=estimated_savings,
            implementation_steps=implementation_steps,
            risk_level=risk_level
        )

        self.scaling_plans.append(plan)
        return plan

    def _get_implementation_steps(self, recommendation: ScalingRecommendation,
                                   resource: Resource) -> List[str]:
        """Get implementation steps for scaling recommendation."""
        steps = {
            ScalingRecommendation.SCALE_UP: [
                f"Increase {resource.value} allocation",
                "Update Terraform configuration",
                "Apply changes with Terraform",
                "Verify resource availability",
                "Update monitoring thresholds"
            ],
            ScalingRecommendation.SCALE_DOWN: [
                f"Analyze {resource.value} utilization patterns",
                "Identify underutilized resources",
                f"Reduce {resource.value} allocation",
                "Update Terraform configuration",
                "Apply changes with Terraform",
                "Monitor for performance impact"
            ],
            ScalingRecommendation.OPTIMIZE: [
                f"Profile {resource.value} usage",
                "Identify optimization opportunities",
                "Implement caching or compression",
                "Update application configuration",
                "Monitor performance improvements"
            ],
            ScalingRecommendation.MIGRATE: [
                "Evaluate target resource type",
                "Plan migration strategy",
                "Execute migration",
                "Validate functionality",
                "Decommission old resources"
            ],
            ScalingRecommendation.CONSOLIDATE: [
                "Identify consolidation opportunities",
                "Plan workload consolidation",
                "Execute consolidation",
                "Validate functionality",
                "Decommission redundant resources"
            ]
        }

        return steps.get(recommendation, ["Review and plan"])

    def analyze_costs(self) -> List[CostOptimization]:
        """Analyze costs and generate optimization recommendations."""
        optimizations = []

        for usage in self.resource_usage:
            current_cost = usage.current_usage * usage.cost_per_unit

            # Generate optimization recommendations
            if usage.resource == Resource.CPU:
                if usage.average_usage < usage.peak_usage * 0.5:
                    optimized_cost = usage.average_usage * usage.cost_per_unit * 1.2
                    method = "Right-size based on average usage with 20% buffer"
                else:
                    optimized_cost = current_cost * 0.9
                    method = "Optimize application code for better CPU efficiency"
            elif usage.resource == Resource.MEMORY:
                if usage.average_usage < usage.peak_usage * 0.6:
                    optimized_cost = usage.average_usage * usage.cost_per_unit * 1.3
                    method = "Right-size based on average usage with 30% buffer"
                else:
                    optimized_cost = current_cost * 0.85
                    method = "Implement memory caching and garbage collection tuning"
            elif usage.resource == Resource.DISK:
                if usage.average_usage < usage.peak_usage * 0.4:
                    optimized_cost = usage.average_usage * usage.cost_per_unit * 1.5
                    method = "Implement data lifecycle management"
                else:
                    optimized_cost = current_cost * 0.8
                    method = "Implement compression and archiving"
            else:
                optimized_cost = current_cost * 0.9
                method = "General optimization"

            savings = current_cost - optimized_cost
            savings_percentage = (savings / current_cost * 100) if current_cost > 0 else 0

            optimization = CostOptimization(
                resource=usage.resource,
                current_cost=current_cost,
                optimized_cost=optimized_cost,
                savings=savings,
                savings_percentage=savings_percentage,
                optimization_method=method,
                implementation_effort="medium"
            )

            optimizations.append(optimization)

        self.cost_optimizations = optimizations
        return optimizations

    def generate_capacity_forecast(self, days: int = 30) -> Dict:
        """Generate capacity forecast for specified days."""
        forecast = {
            "forecast_period_days": days,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=days)).isoformat(),
            "resources": {}
        }

        for usage in self.resource_usage:
            daily_growth = (usage.forecast_usage - usage.current_usage) / 30
            forecast["resources"][usage.resource.value] = {
                "current": usage.current_usage,
                "forecast": usage.forecast_usage,
                "daily_growth": daily_growth,
                "unit": usage.unit,
                "days_until_threshold": self._calculate_days_until_threshold(
                    usage, threshold=90
                )
            }

        return forecast

    def _calculate_days_until_threshold(self, usage: ResourceUsage,
                                         threshold: float) -> int:
        """Calculate days until resource reaches threshold."""
        if usage.forecast_usage <= usage.current_usage:
            return 365  # No growth

        daily_growth = (usage.forecast_usage - usage.current_usage) / 30
        if daily_growth <= 0:
            return 365

        remaining = threshold - usage.current_usage
        days = remaining / daily_growth
        return max(0, int(days))

    def generate_cost_report(self) -> Dict:
        """Generate comprehensive cost report."""
        total_current = sum(opt.current_cost for opt in self.cost_optimizations)
        total_optimized = sum(opt.optimized_cost for opt in self.cost_optimizations)
        total_savings = total_current - total_optimized

        return {
            "report_date": datetime.now().isoformat(),
            "total_current_cost": total_current,
            "total_optimized_cost": total_optimized,
            "total_savings": total_savings,
            "savings_percentage": (total_savings / total_current * 100) if total_current > 0 else 0,
            "by_resource": {
                opt.resource.value: {
                    "current_cost": opt.current_cost,
                    "optimized_cost": opt.optimized_cost,
                    "savings": opt.savings,
                    "savings_percentage": opt.savings_percentage,
                    "method": opt.optimization_method
                }
                for opt in self.cost_optimizations
            },
            "scaling_plans": [
                {
                    "resource": plan.resource.value,
                    "recommendation": plan.recommendation.value,
                    "current_capacity": plan.current_capacity,
                    "recommended_capacity": plan.recommended_capacity,
                    "estimated_savings": plan.estimated_savings,
                    "risk_level": plan.risk_level
                }
                for plan in self.scaling_plans
            ]
        }

    def generate_recommendations(self) -> List[Dict]:
        """Generate prioritized recommendations."""
        recommendations = []

        for plan in self.scaling_plans:
            recommendations.append({
                "type": "scaling",
                "resource": plan.resource.value,
                "recommendation": plan.recommendation.value,
                "priority": "high" if plan.risk_level == "low" else "medium",
                "estimated_savings": plan.estimated_savings,
                "steps": plan.implementation_steps
            })

        for opt in self.cost_optimizations:
            if opt.savings_percentage > 10:
                recommendations.append({
                    "type": "cost_optimization",
                    "resource": opt.resource.value,
                    "recommendation": opt.optimization_method,
                    "priority": "high" if opt.savings_percentage > 20 else "medium",
                    "estimated_savings": opt.savings,
                    "effort": opt.implementation_effort
                })

        recommendations.sort(key=lambda x: x["estimated_savings"], reverse=True)
        return recommendations


def main():
    """Main function to demonstrate capacity planning capabilities."""
    engine = CapacityPlanningEngine()

    print("=== Capacity Planning & Cost Optimization Engine ===\n")

    # Analyze resource usage
    print("1. Analyzing Resource Usage...")
    cpu_usage = engine.analyze_resource_usage(
        Resource.CPU, 45.0, 38.0, 85.0, "cores", 0.04
    )
    print(f"   CPU: {cpu_usage.current_usage} cores (avg: {cpu_usage.average_usage}, peak: {cpu_usage.peak_usage})")

    memory_usage = engine.analyze_resource_usage(
        Resource.MEMORY, 128.0, 96.0, 256.0, "GB", 0.01
    )
    print(f"   Memory: {memory_usage.current_usage} GB (avg: {memory_usage.average_usage}, peak: {memory_usage.peak_usage})")

    disk_usage = engine.analyze_resource_usage(
        Resource.DISK, 500.0, 350.0, 800.0, "GB", 0.001
    )
    print(f"   Disk: {disk_usage.current_usage} GB (avg: {disk_usage.average_usage}, peak: {disk_usage.peak_usage})")

    pods_usage = engine.analyze_resource_usage(
        Resource.PODS, 50.0, 35.0, 75.0, "pods", 0.001
    )
    print(f"   Pods: {pods_usage.current_usage} (avg: {pods_usage.average_usage}, peak: {pods_usage.peak_usage})\n")

    # Generate scaling plans
    print("2. Generating Scaling Plans...")
    for usage in engine.resource_usage:
        plan = engine.generate_scaling_plan(usage)
        print(f"   {plan.resource.value}: {plan.recommendation.value} "
              f"(Current: {plan.current_capacity:.1f}, Recommended: {plan.recommended_capacity:.1f})")

    # Analyze costs
    print("\n3. Analyzing Costs...")
    optimizations = engine.analyze_costs()
    for opt in optimizations:
        print(f"   {opt.resource.value}: ${opt.current_cost:.2f} -> ${opt.optimized_cost:.2f} "
              f"(Savings: ${opt.savings:.2f}, {opt.savings_percentage:.1f}%)")

    # Generate capacity forecast
    print("\n4. Generating Capacity Forecast...")
    forecast = engine.generate_capacity_forecast(30)
    for resource, data in forecast["resources"].items():
        print(f"   {resource}: {data['current']:.1f} -> {data['forecast']:.1f} "
              f"(Days until 90%: {data['days_until_threshold']})")

    # Generate cost report
    print("\n5. Generating Cost Report...")
    report = engine.generate_cost_report()
    print(f"   Total Current Cost: ${report['total_current_cost']:.2f}")
    print(f"   Total Optimized Cost: ${report['total_optimized_cost']:.2f}")
    print(f"   Total Savings: ${report['total_savings']:.2f} ({report['savings_percentage']:.1f}%)")

    # Generate recommendations
    print("\n6. Generating Recommendations...")
    recommendations = engine.generate_recommendations()
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. [{rec['priority'].upper()}] {rec['type']}: {rec['recommendation']}")
        print(f"      Resource: {rec['resource']}, Savings: ${rec['estimated_savings']:.2f}")

    # Save report
    with open("capacity_planning_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("\nReport saved to capacity_planning_report.json")


if __name__ == "__main__":
    main()
