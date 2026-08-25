variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "app_port" {
  type    = number
  default = 5000
}

variable "tags" {
  type    = map(string)
  default = {}
}
