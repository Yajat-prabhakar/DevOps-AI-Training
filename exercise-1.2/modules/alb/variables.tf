variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_sg_id" {
  type = string
}

variable "app_port" {
  type    = number
  default = 5000
}

variable "health_check_path" {
  type        = string
  description = "Health check endpoint path"
  default     = "/api/health"
}

variable "certificate_arn" {
  type        = string
  description = "ARN of ACM certificate for HTTPS. Leave empty for HTTP-only."
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default     = {}
}
