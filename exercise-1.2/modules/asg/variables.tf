variable "environment" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "app_sg_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "alb_arn_suffix" {
  type = string
}

variable "target_group_arn_suffix" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "min_size" {
  type    = number
  default = 2
}

variable "max_size" {
  type    = number
  default = 6
}

variable "desired_capacity" {
  type    = number
  default = 2
}

variable "iam_instance_profile" {
  type = string
}

variable "app_port" {
  type        = number
  description = "Port the application listens on"
  default     = 5000
}

variable "docker_image" {
  type        = string
  description = "Docker image to deploy (e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com/app-backend:latest)"
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default     = {}
}
