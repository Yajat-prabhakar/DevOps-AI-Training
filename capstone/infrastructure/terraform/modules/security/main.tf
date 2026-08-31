# Oracle Cloud Infrastructure - Security Module
# Capstone Project: Enterprise DevOps Observability Platform

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
}

# Vault for Secrets
resource "oci_kms_vault" "this" {
  compartment_id = var.compartment_id
  display_name   = "${var.project_name}-vault"
  vault_type     = "DEFAULT"
}

# Master Key
resource "oci_kms_key" "master" {
  compartment_id = var.compartment_id
  display_name   = "${var.project_name}-master-key"
  key_shape {
    algorithm = "AES"
    length    = 32
  }
  protection_domain_id = data.oci_kms_protection_domains.pd.protection_domains[0].id
  vault_id             = oci_kms_vault.this.id
}

# Dynamic Group for OKE
resource "oci_identity_dynamic_group" "oke_nodes" {
  compartment_id = var.compartment_id
  name           = "${var.project_name}-oke-nodes"
  description    = "Dynamic group for OKE nodes"
  matching_rule  = "Any {resource.type='cluster', resource.compartment.id='${var.compartment_id}'}"
}

# Dynamic Group for Functions
resource "oci_identity_dynamic_group" "functions" {
  compartment_id = var.compartment_id
  name           = "${var.project_name}-functions"
  description    = "Dynamic group for Functions"
  matching_rule  = "Any {resource.type='fnfunc', resource.compartment.id='${var.compartment_id}'}"
}

# Policy - OKE Access
resource "oci_identity_policy" "oke_access" {
  compartment_id = var.compartment_id
  name           = "${var.project_name}-oke-policy"
  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.oke_nodes.name} to manage all-resources in compartment ${var.compartment_id}",
    "Allow dynamic-group ${oci_identity_dynamic_group.functions.name} to manage all-resources in compartment ${var.compartment_id}",
  ]
}

# Audit Policy
resource "oci_identity_policy" "audit" {
  compartment_id = var.compartment_id
  name           = "${var.project_name}-audit-policy"
  statements = [
    "Allow service audit to read all-resources in compartment ${var.compartment_id}",
  ]
}

# Data Safe Policy
resource "oci_identity_policy" "data_safe" {
  compartment_id = var.compartment_id
  name           = "${var.project_name}-data-safe-policy"
  statements = [
    "Allow service datasafe to read all-resources in compartment ${var.compartment_id}",
  ]
}

data "oci_kms_protection_domains" "pd" {
  compartment_id = var.compartment_id
  vault_id       = oci_kms_vault.this.id
}

output "vault_id" {
  value = oci_kms_vault.this.id
}

output "key_id" {
  value = oci_kms_key.master.id
}

output "dynamic_group_oke" {
  value = oci_identity_dynamic_group.oke_nodes.name
}

output "dynamic_group_functions" {
  value = oci_identity_dynamic_group.functions.name
}
