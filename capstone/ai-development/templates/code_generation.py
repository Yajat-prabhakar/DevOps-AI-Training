#!/usr/bin/env python3
"""
AI Code Generation Templates - Capstone Project
Enterprise DevOps Observability Platform

This module provides AI-powered code generation templates for infrastructure.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TemplateType(Enum):
    TERRAFORM = "terraform"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    CI_CD = "ci_cd"
    MONITORING = "monitoring"


@dataclass
class CodeTemplate:
    name: str
    template_type: TemplateType
    description: str
    content: str
    variables: List[str]
    tags: List[str]


class CodeGenerationEngine:
    """AI-powered code generation engine."""

    def __init__(self):
        self.templates: List[CodeTemplate] = []
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize code generation templates."""
        self.templates = [
            CodeTemplate(
                name="oci-vcn",
                template_type=TemplateType.TERRAFORM,
                description="Oracle Cloud Infrastructure VCN template",
                content='''
# Oracle Cloud Infrastructure VCN
resource "oci_core_vcn" "{{name}}" {
  compartment_id = "{{compartment_id}}"
  display_name   = "{{name}}"
  cidr_blocks    = ["{{cidr_block}}"]
  dns_label      = "{{dns_label}}"
}

resource "oci_core_internet_gateway" "{{name}}-igw" {
  compartment_id = "{{compartment_id}}"
  vcn_id         = oci_core_vcn.{{name}}.id
  display_name   = "{{name}}-igw"
  enabled        = true
}

resource "oci_core_route_table" "{{name}}-rt" {
  compartment_id = "{{compartment_id}}"
  vcn_id         = oci_core_vcn.{{name}}.id
  display_name   = "{{name}}-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.{{name}}-igw.id
  }
}
''',
                variables=["name", "compartment_id", "cidr_block", "dns_label"],
                tags=["oci", "vcn", "networking"]
            ),
            CodeTemplate(
                name="kubernetes-deployment",
                template_type=TemplateType.KUBERNETES,
                description="Kubernetes Deployment template",
                content='''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{name}}
  namespace: {{namespace}}
  labels:
    app: {{name}}
    version: {{version}}
spec:
  replicas: {{replicas}}
  selector:
    matchLabels:
      app: {{name}}
  template:
    metadata:
      labels:
        app: {{name}}
        version: {{version}}
    spec:
      containers:
        - name: {{name}}
          image: {{image}}
          ports:
            - containerPort: {{port}}
          resources:
            requests:
              memory: "{{memory_request}}"
              cpu: "{{cpu_request}}"
            limits:
              memory: "{{memory_limit}}"
              cpu: "{{cpu_limit}}"
          livenessProbe:
            httpGet:
              path: {{health_path}}
              port: {{port}}
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: {{health_path}}
              port: {{port}}
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {{name}}
  namespace: {{namespace}}
spec:
  selector:
    app: {{name}}
  ports:
    - port: {{port}}
      targetPort: {{port}}
  type: {{service_type}}
''',
                variables=["name", "namespace", "version", "replicas", "image",
                          "port", "memory_request", "cpu_request", "memory_limit",
                          "cpu_limit", "health_path", "service_type"],
                tags=["kubernetes", "deployment", "service"]
            ),
            CodeTemplate(
                name="dockerfile",
                template_type=TemplateType.DOCKER,
                description="Dockerfile template",
                content='''
# {{description}}
FROM {{base_image}} AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM {{runtime_image}}
WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE {{port}}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{{port}}{{health_path}} || exit 1

CMD ["npm", "start"]
''',
                variables=["description", "base_image", "runtime_image",
                          "port", "health_path"],
                tags=["docker", "dockerfile", "nodejs"]
            ),
            CodeTemplate(
                name="github-actions",
                template_type=TemplateType.CI_CD,
                description="GitHub Actions CI/CD pipeline template",
                content='''
name: {{pipeline_name}}
on:
  push:
    branches: [{{branch}}]
  pull_request:
    branches: [{{branch}}]

env:
  REGISTRY: ghcr.io/${{ github.repository }}
  IMAGE_NAME: {{image_name}}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4

      - name: Run Tests
        run: |
          echo "Running tests..."
          # Add test commands here

  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/{{branch}}'
    environment: {{environment}}
    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        run: |
          echo "Deploying to {{environment}}..."
          # Add deployment commands here
''',
                variables=["pipeline_name", "branch", "image_name",
                          "environment"],
                tags=["github-actions", "cicd", "docker"]
            ),
            CodeTemplate(
                name="prometheus-alert",
                template_type=TemplateType.MONITORING,
                description="Prometheus alerting rule template",
                content='''
groups:
  - name: {{group_name}}
    rules:
      - alert: {{alert_name}}
        expr: {{expression}}
        for: {{duration}}
        labels:
          severity: {{severity}}
          team: {{team}}
        annotations:
          summary: "{{summary}}"
          description: "{{description}}"
          runbook_url: "{{runbook_url}}"
''',
                variables=["group_name", "alert_name", "expression",
                          "duration", "severity", "team", "summary",
                          "description", "runbook_url"],
                tags=["prometheus", "alerting", "monitoring"]
            ),
        ]

    def get_template(self, template_type: TemplateType,
                     tags: Optional[List[str]] = None) -> List[CodeTemplate]:
        """Get templates by type and optional tags."""
        templates = [t for t in self.templates if t.template_type == template_type]

        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]

        return templates

    def generate_code(self, template_name: str,
                      variables: Dict[str, str]) -> Optional[str]:
        """Generate code from template with variables."""
        template = next(
            (t for t in self.templates if t.name == template_name),
            None
        )

        if not template:
            return None

        content = template.content
        for var_name, var_value in variables.items():
            placeholder = "{{" + var_name + "}}"
            content = content.replace(placeholder, var_value)

        return content

    def list_templates(self) -> Dict[str, List[str]]:
        """List all templates grouped by type."""
        result = {}
        for template in self.templates:
            if template.template_type.value not in result:
                result[template.template_type.value] = []
            result[template.template_type.value].append(template.name)
        return result


def main():
    """Main function to demonstrate code generation capabilities."""
    engine = CodeGenerationEngine()

    print("=== AI Code Generation Templates ===\n")

    # List templates
    print("1. Available Templates...")
    templates = engine.list_templates()
    for template_type, names in templates.items():
        print(f"   {template_type}:")
        for name in names:
            print(f"     - {name}")

    # Generate Terraform code
    print("\n2. Generating Terraform Code...")
    terraform_code = engine.generate_code(
        "oci-vcn",
        {
            "name": "devops-platform-vcn",
            "compartment_id": "ocid1.compartment.oc1..aaaa1234567890",
            "cidr_block": "10.0.0.0/16",
            "dns_label": "devopsplatform"
        }
    )
    print("   Generated OCI VCN Terraform code:")
    print("   " + "=" * 50)
    for line in terraform_code.strip().split("\n")[:10]:
        print(f"   {line}")
    print("   " + "=" * 50)

    # Generate Kubernetes code
    print("\n3. Generating Kubernetes Code...")
    k8s_code = engine.generate_code(
        "kubernetes-deployment",
        {
            "name": "api-gateway",
            "namespace": "devops-platform",
            "version": "v1",
            "replicas": "3",
            "image": "nginx:alpine",
            "port": "80",
            "memory_request": "128Mi",
            "cpu_request": "100m",
            "memory_limit": "256Mi",
            "cpu_limit": "200m",
            "health_path": "/",
            "service_type": "LoadBalancer"
        }
    )
    print("   Generated Kubernetes Deployment:")
    print("   " + "=" * 50)
    for line in k8s_code.strip().split("\n")[:15]:
        print(f"   {line}")
    print("   " + "=" * 50)

    # Generate GitHub Actions code
    print("\n4. Generating GitHub Actions Code...")
    github_code = engine.generate_code(
        "github-actions",
        {
            "pipeline_name": "CI/CD Pipeline",
            "branch": "main",
            "image_name": "api-gateway",
            "environment": "production"
        }
    )
    print("   Generated GitHub Actions Pipeline:")
    print("   " + "=" * 50)
    for line in github_code.strip().split("\n")[:15]:
        print(f"   {line}")
    print("   " + "=" * 50)

    # Generate Prometheus alert
    print("\n5. Generating Prometheus Alert...")
    alert_code = engine.generate_code(
        "prometheus-alert",
        {
            "group_name": "infrastructure_alerts",
            "alert_name": "HighCPUUsage",
            "expression": "cluster:cpu_usage_percent > 90",
            "duration": "5m",
            "severity": "critical",
            "team": "infrastructure",
            "summary": "High CPU Usage",
            "description": "CPU usage is above 90% for 5 minutes",
            "runbook_url": "https://docs.example.com/runbooks/high-cpu"
        }
    )
    print("   Generated Prometheus Alert:")
    print("   " + "=" * 50)
    for line in alert_code.strip().split("\n"):
        print(f"   {line}")
    print("   " + "=" * 50)


if __name__ == "__main__":
    main()
