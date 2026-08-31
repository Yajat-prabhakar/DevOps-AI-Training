# Oracle Cloud Infrastructure - VCN Module
# Capstone Project: Enterprise DevOps Observability Platform

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "vcn_name" {
  description = "VCN name"
  type        = string
}

variable "vcn_cidr" {
  description = "VCN CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "dns_label" {
  description = "DNS label"
  type        = string
  default     = "devopsplatform"
}

# VCN
resource "oci_core_vcn" "this" {
  compartment_id = var.compartment_id
  display_name   = var.vcn_name
  cidr_blocks    = [var.vcn_cidr]
  dns_label      = var.dns_label
}

# Internet Gateway
resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-igw"
  enabled        = true
}

# NAT Gateway
resource "oci_core_nat_gateway" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-nat"
}

# Route Table - Public
resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.this.id
  }
}

# Route Table - Private
resource "oci_core_route_table" "private" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_nat_gateway.this.id
  }
}

# Security List - Public
resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-public-sl"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "all"
    source   = var.vcn_cidr
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

# Security List - Private
resource "oci_core_security_list" "private" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "${var.vcn_name}-private-sl"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "all"
    source   = var.vcn_cidr
  }
}

# Subnet - Public (Load Balancer)
resource "oci_core_subnet" "public" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.this.id
  display_name        = "${var.vcn_name}-public-subnet"
  cidr_block          = cidrsubnet(var.vcn_cidr, 8, 1)
  route_table_id      = oci_core_route_table.public.id
  security_list_ids   = [oci_core_security_list.public.id]
  dns_label           = "public"
}

# Subnet - Private (OKE Nodes)
resource "oci_core_subnet" "private" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.this.id
  display_name        = "${var.vcn_name}-private-subnet"
  cidr_block          = cidrsubnet(var.vcn_cidr, 8, 2)
  route_table_id      = oci_core_route_table.private.id
  security_list_ids   = [oci_core_security_list.private.id]
  dns_label           = "private"
}

# Subnet - Private (Database)
resource "oci_core_subnet" "database" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.this.id
  display_name        = "${var.vcn_name}-database-subnet"
  cidr_block          = cidrsubnet(var.vcn_cidr, 8, 3)
  route_table_id      = oci_core_route_table.private.id
  security_list_ids   = [oci_core_security_list.private.id]
  dns_label           = "database"
}

output "vcn_id" {
  value = oci_core_vcn.this.id
}

output "public_subnet_id" {
  value = oci_core_subnet.public.id
}

output "private_subnet_id" {
  value = oci_core_subnet.private.id
}

output "database_subnet_id" {
  value = oci_core_subnet.database.id
}
