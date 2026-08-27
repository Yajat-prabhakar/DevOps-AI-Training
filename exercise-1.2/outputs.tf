output "primary_alb_dns_name" {
  description = "DNS name of the primary region ALB"
  value       = module.alb_primary.alb_dns_name
}

output "secondary_alb_dns_name" {
  description = "DNS name of the secondary region ALB"
  value       = module.alb_secondary.alb_dns_name
}

output "primary_db_endpoint" {
  description = "Connection endpoint for the primary RDS instance"
  value       = module.rds_primary.db_endpoint
  sensitive   = true
}

output "primary_asg_name" {
  description = "Name of the primary Auto Scaling Group"
  value       = module.asg_primary.asg_name
}
