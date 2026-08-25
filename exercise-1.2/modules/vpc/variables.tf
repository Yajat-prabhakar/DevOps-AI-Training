variable "region" {
  type        = string
  description = "AWS region this VPC is deployed in"
}

variable "environment" {
  type        = string
  description = "Environment name (dev/staging/prod)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones to spread subnets across"
  default     = 2
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default     = {}
}
