# Variables - Capstone Project
# Enterprise DevOps Observability Platform

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

variable "node_shape" {
  description = "Node shape"
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "node_ocpus" {
  description = "OCPUs per node"
  type        = number
  default     = 4
}

variable "node_memory_gb" {
  description = "Memory per node in GB"
  type        = number
  default     = 16
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "v1.28.3"
}

variable "vcn_cidr" {
  description = "VCN CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}
