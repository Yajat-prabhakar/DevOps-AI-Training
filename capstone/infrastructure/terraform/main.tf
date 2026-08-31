# Oracle Cloud Infrastructure - Main Configuration
# Capstone Project: Enterprise DevOps Observability Platform

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  region           = var.region
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
}

# Variables
variable "region" {
  description = "OCI region"
  type        = string
  default     = "ap-mumbai-1"
}

variable "tenancy_ocid" {
  description = "Tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "User OCID"
  type        = string
}

variable "fingerprint" {
  description = "API fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to private key"
  type        = string
  default     = "~/.oci/oci_api_key.pem"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "devops-platform"
}

variable "alarm_email" {
  description = "Email for alarm notifications"
  type        = string
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 3
}

# Root Compartment
module "compartment" {
  source = "./modules/compartment"
  name   = "${var.project_name}-compartment"
  parent_id = var.tenancy_ocid
  tags = {
    project     = var.project_name
    environment = "production"
    managed-by  = "terraform"
  }
}

# Network
module "network" {
  source         = "./modules/network"
  compartment_id = module.compartment.id
  vcn_name       = "${var.project_name}-vcn"
  vcn_cidr       = "10.0.0.0/16"
}

# OKE Cluster
module "oke" {
  source              = "./modules/oke"
  compartment_id      = module.compartment.id
  vcn_id              = module.network.vcn_id
  subnet_id           = module.network.private_subnet_id
  cluster_name        = "${var.project_name}-cluster"
  node_count          = var.node_count
}

# Monitoring
module "monitoring" {
  source              = "./modules/monitoring"
  compartment_id      = module.compartment.id
  project_name        = var.project_name
  alarm_email         = var.alarm_email
}

# Security
module "security" {
  source              = "./modules/security"
  compartment_id      = module.compartment.id
  project_name        = var.project_name
}

# Outputs
output "compartment_id" {
  value = module.compartment.id
}

output "vcn_id" {
  value = module.network.vcn_id
}

output "public_subnet_id" {
  value = module.network.public_subnet_id
}

output "private_subnet_id" {
  value = module.network.private_subnet_id
}

output "database_subnet_id" {
  value = module.network.database_subnet_id
}

output "cluster_id" {
  value = module.oke.cluster_id
}

output "cluster_endpoint" {
  value = module.oke.cluster_endpoint
}

output "log_group_id" {
  value = module.monitoring.log_group_id
}

output "vault_id" {
  value = module.security.vault_id
}
