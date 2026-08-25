environment      = "prod"
project          = "exercise-1-2"
owner            = "devops-training"
primary_region   = "us-east-1"
secondary_region = "eu-west-1"

primary_vpc_cidr   = "10.10.0.0/16"
secondary_vpc_cidr = "10.20.0.0/16"

# Larger instances, wider ASG bounds, and a bigger DB class than staging —
# right-sized for expected sustained load rather than left at the same
# defaults, which is the single most common source of cloud overspend.
instance_type      = "t3.small"
asg_min_size       = 3
asg_max_size       = 10
db_instance_class  = "db.t3.large"
