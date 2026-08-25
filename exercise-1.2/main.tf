module "vpc_primary" {
  source = "./modules/vpc"
  providers = {
    aws = aws.primary
  }

  region      = var.primary_region
  environment = var.environment
  vpc_cidr    = var.primary_vpc_cidr
  az_count    = 2
  tags        = local.common_tags
}

module "security_primary" {
  source = "./modules/security"
  providers = {
    aws = aws.primary
  }

  environment = var.environment
  vpc_id      = module.vpc_primary.vpc_id
  vpc_cidr    = var.primary_vpc_cidr
  tags        = local.common_tags
}

module "rds_primary" {
  source = "./modules/rds"
  providers = {
    aws = aws.primary
  }

  environment            = var.environment
  private_subnet_ids     = module.vpc_primary.private_subnet_ids
  db_sg_id               = module.security_primary.db_sg_id
  instance_class         = var.db_instance_class
  multi_az               = true
  backup_retention_days  = 7
  deletion_protection    = var.environment == "prod"
  tags                   = local.common_tags
}

module "iam_primary" {
  source = "./modules/iam"
  providers = {
    aws = aws.primary
  }

  environment   = var.environment
  db_secret_arn = module.rds_primary.db_secret_arn
  tags          = local.common_tags
}

module "alb_primary" {
  source = "./modules/alb"
  providers = {
    aws = aws.primary
  }

  environment       = var.environment
  vpc_id            = module.vpc_primary.vpc_id
  public_subnet_ids = module.vpc_primary.public_subnet_ids
  alb_sg_id         = module.security_primary.alb_sg_id
  tags              = local.common_tags
}

module "asg_primary" {
  source = "./modules/asg"
  providers = {
    aws = aws.primary
  }

  environment              = var.environment
  private_subnet_ids       = module.vpc_primary.private_subnet_ids
  app_sg_id                = module.security_primary.app_sg_id
  target_group_arn         = module.alb_primary.target_group_arn
  alb_arn_suffix           = module.alb_primary.alb_arn_suffix
  target_group_arn_suffix  = module.alb_primary.target_group_arn_suffix
  iam_instance_profile     = module.iam_primary.instance_profile_name
  instance_type            = var.instance_type
  min_size                 = var.asg_min_size
  max_size                 = var.asg_max_size
  desired_capacity         = var.asg_min_size
  tags                     = local.common_tags
}


# --- Secondary region ---
# Same module set, pointed at the aws.secondary provider alias and the
# secondary CIDR/subnets, for the "multi-region deployment" requirement.
# Kept as a separate stack (not replicated RDS) since cross-region RDS needs
# a read replica, not a duplicate primary — see docs/README.md "Multi-region
# design notes" for why and how to extend this.

module "vpc_secondary" {
  source = "./modules/vpc"
  providers = {
    aws = aws.secondary
  }

  region      = var.secondary_region
  environment = var.environment
  vpc_cidr    = var.secondary_vpc_cidr
  az_count    = 2
  tags        = local.common_tags
}

module "security_secondary" {
  source = "./modules/security"
  providers = {
    aws = aws.secondary
  }

  environment = var.environment
  vpc_id      = module.vpc_secondary.vpc_id
  vpc_cidr    = var.secondary_vpc_cidr
  tags        = local.common_tags
}

module "alb_secondary" {
  source = "./modules/alb"
  providers = {
    aws = aws.secondary
  }

  environment       = var.environment
  vpc_id            = module.vpc_secondary.vpc_id
  public_subnet_ids = module.vpc_secondary.public_subnet_ids
  alb_sg_id         = module.security_secondary.alb_sg_id
  tags              = local.common_tags
}
