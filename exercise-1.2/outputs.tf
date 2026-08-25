output "primary_alb_dns_name" {
  value = module.alb_primary.alb_dns_name
}

output "secondary_alb_dns_name" {
  value = module.alb_secondary.alb_dns_name
}

output "primary_db_endpoint" {
  value = module.rds_primary.db_endpoint
}

output "primary_asg_name" {
  value = module.asg_primary.asg_name
}
