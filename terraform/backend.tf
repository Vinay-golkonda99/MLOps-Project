terraform {
  backend "s3" {
    bucket         = "vinay-terraform-states"
    key            = "eks/mlops-cluster/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "terraform_locks"
    encrypt        = true
  }
}
