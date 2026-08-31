# Oracle Cloud Infrastructure - Compartment Module
# Capstone Project: Enterprise DevOps Observability Platform

variable "name" {
  description = "Compartment name"
  type        = string
}

variable "description" {
  description = "Compartment description"
  type        = string
  default     = "DevOps Platform Compartment"
}

variable "parent_id" {
  description = "Parent compartment OCID"
  type        = string
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}

resource "oci_identity_compartment" "this" {
  name        = var.name
  description = var.description
  parent_id   = var.parent_id
  freeform_tags = var.tags
}

output "id" {
  value = oci_identity_compartment.this.id
}

output "name" {
  value = oci_identity_compartment.this.name
}
