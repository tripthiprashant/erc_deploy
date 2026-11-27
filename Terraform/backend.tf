terraform {
  backend "s3" {
    bucket         = "erc-231137"
    key            = "devops-ecs-project/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    use_lockfile   = true
  }
}