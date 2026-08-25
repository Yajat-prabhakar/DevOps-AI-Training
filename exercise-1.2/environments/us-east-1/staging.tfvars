environment      = "staging"
project          = "exercise-1-2"
owner            = "devops-training"
primary_region   = "us-east-1"
secondary_region = "eu-west-1"

primary_vpc_cidr   = "10.10.0.0/16"
secondary_vpc_cidr = "10.20.0.0/16"

instance_type      = "t3.micro"
asg_min_size       = 2
asg_max_size       = 6
db_instance_class  = "db.t3.medium"
