variable "environment" {
  type        = string
  description = "Environment name: dev, staging, or prod"
  default     = "staging"
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
  type    = string
  default = "us-east-1"
}

variable "secondary_region" {
  type    = string
  default = "eu-west-1"
}

variable "primary_vpc_cidr" {
  type    = string
  default = "10.10.0.0/16"
}

variable "secondary_vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for app instances. t3.* is burstable/cheap for training workloads — size up deliberately for sustained CPU."
  default     = "t3.micro"
}

variable "asg_min_size" {
  type    = number
  default = 2
}

variable "asg_max_size" {
  type    = number
  default = 6
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.medium"
}
