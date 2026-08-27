module "vpc" {
  source = "../../exercise-1.2/modules/vpc"

  environment         = "test"
  project            = "test-project"
  vpc_cidr           = "10.0.0.0/16"
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]
  availability_zones  = ["us-east-1a", "us-east-1b"]
}

module "security" {
  source = "../../exercise-1.2/modules/security"

  environment = "test"
  project    = "test-project"
  vpc_id     = module.vpc.vpc_id
  vpc_cidr   = "10.0.0.0/16"
}

module "alb" {
  source = "../../exercise-1.2/modules/alb"

  environment        = "test"
  project           = "test-project"
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_id = module.security.alb_security_group_id
}

module "rds" {
  source = "../../exercise-1.2/modules/rds"

  environment           = "test"
  project              = "test-project"
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  security_group_id    = module.security.database_security_group_id
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  multi_az            = false
  deletion_protection = false
}
