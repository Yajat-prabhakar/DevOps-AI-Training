# Remote state, versioned + encrypted S3 bucket with a DynamoDB lock table.
# Bucket/table must exist before `terraform init` — create them once by hand
# or via a small bootstrap config, since state can't manage its own backend.
#
# SETUP REQUIRED:
#   1. Create S3 bucket: aws s3api create-bucket --bucket <PREFIX>-tfstate-devops-training --region us-east-1
#   2. Enable versioning: aws s3api put-bucket-versioning --bucket <PREFIX>-tfstate-devops-training --versioning-configuration Status=Enabled
#   3. Enable encryption: aws s3api put-bucket-encryption --bucket <PREFIX>-tfstate-devops-training --server-side-encryption-configuration '{...}'
#   4. Create DynamoDB table: aws dynamodb create-table --table-name <PREFIX>-tf-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
#   5. Replace <PREFIX> with your project name in the values below.
terraform {
  backend "s3" {
    bucket         = "devops-training-tfstate"
    key            = "exercise-1.2/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "devops-training-tf-locks"
    encrypt        = true
  }
}
