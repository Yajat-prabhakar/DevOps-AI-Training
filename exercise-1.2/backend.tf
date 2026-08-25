# Remote state, versioned + encrypted S3 bucket with a DynamoDB lock table.
# Bucket/table must exist before `terraform init` — create them once by hand
# or via a small bootstrap config, since state can't manage its own backend.
terraform {
  backend "s3" {
    bucket         = "REPLACE_ME-tfstate-devops-training"
    key            = "exercise-1.2/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "REPLACE_ME-tf-locks"
    encrypt        = true
  }
}
