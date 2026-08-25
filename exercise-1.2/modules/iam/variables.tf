variable "environment" {
  type = string
}

variable "db_secret_arn" {
  type        = string
  description = "ARN of the Secrets Manager secret holding the DB password, scoped narrowly rather than granting secretsmanager:* on *"
}

variable "tags" {
  type    = map(string)
  default = {}
}
