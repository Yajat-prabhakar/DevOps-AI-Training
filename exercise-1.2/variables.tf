variable "environment" {
  type        = string
  description = "Environment name: dev, staging, or prod"
  default     = "staging"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project" {
  type        = string
  description = "Project name, used in tags and cost allocation"
  default     = "exercise-1-2"
}

variable "owner" {
  type        = string
  description = "Team or person accountable for cost/ops of these resources"
  default     = "devops-training"
}

variable "primary_region" {
  type        = string
  description = "AWS region for primary deployment"
  default     = "us-east-1"
}

variable "secondary_region" {
  type        = string
  description = "AWS region for secondary (DR) deployment"
  default     = "eu-west-1"
}

variable "primary_vpc_cidr" {
  type        = string
  description = "CIDR block for primary region VPC"
  default     = "10.10.0.0/16"
}

variable "secondary_vpc_cidr" {
  type        = string
  description = "CIDR block for secondary region VPC"
  default     = "10.20.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones to use per region"
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 4
    error_message = "AZ count must be between 2 and 4."
  }
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for app instances. t3.* is burstable/cheap for training workloads — size up deliberately for sustained CPU."
  default     = "t3.micro"
}

variable "app_port" {
  type        = number
  description = "Port the application listens on"
  default     = 5000
}

variable "docker_image" {
  type        = string
  description = "Docker image to deploy (e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com/app-backend:latest)"
  default     = "nginx:alpine"
}

variable "certificate_arn" {
  type        = string
  description = "ARN of ACM certificate for HTTPS on ALB. Leave empty for HTTP-only."
  default     = ""
}

variable "asg_min_size" {
  type        = number
  description = "Minimum number of instances in ASG"
  default     = 2
}

variable "asg_max_size" {
  type        = number
  description = "Maximum number of instances in ASG"
  default     = 6
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t3.medium"
}
