# Oracle Cloud Infrastructure - OKE Module
# Capstone Project: Enterprise DevOps Observability Platform

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "vcn_id" {
  description = "VCN OCID"
  type        = string
}

variable "subnet_id" {
  description = "Private subnet OCID for worker nodes"
  type        = string
}

variable "cluster_name" {
  description = "OKE cluster name"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "v1.28.3"
}

variable "node_pool_name" {
  description = "Node pool name"
  type        = string
  default     = "devops-platform-pool"
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

# OKE Cluster
resource "oci_containerengine_cluster" "this" {
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = var.cluster_name
  vcn_id             = var.vcn_id

  options {
    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled               = false
    }
    kubernetes_network_config {
      pods_cidr     = "10.244.0.0/16"
      services_cidr = "10.96.0.0/16"
    }
  }

  endpoint_config {
    is_public_ip_enabled = true
    subnet_id            = var.subnet_id
  }
}

# Node Pool
resource "oci_containerengine_node_pool" "this" {
  cluster_id         = oci_containerengine_cluster.this.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = var.node_pool_name
  node_shape         = var.node_shape
  subnet_ids         = [var.subnet_id]

  node_config_details {
    size = var.node_count
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
      subnet_id           = var.subnet_id
    }
  }

  node_shape_config {
    ocpus = var.node_ocpus
    memory_in_gbs = var.node_memory_gb
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

output "cluster_id" {
  value = oci_containerengine_cluster.this.id
}

output "cluster_endpoint" {
  value = oci_containerengine_cluster.this.endpoints[0].public_endpoint
}

output "node_pool_id" {
  value = oci_containerengine_node_pool.this.id
}
