variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where security groups will be created"
}

variable "app_port" {
  type        = number
  description = "Port the application listens on"
  default     = 5000
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default     = {}
}
