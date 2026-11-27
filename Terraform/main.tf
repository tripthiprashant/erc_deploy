module "vpc" {
  source = "./modules/vpc"
  project_name        = var.project_name
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
}

module "security" {
  source = "./modules/security"
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}

module "iam" {
  source = "./modules/iam"
  project_name = var.project_name
}

module "ecr" {
  source = "./modules/ecr"
  repository_name = var.ecr_repository_name
}

module "ecs" {
  source = "./modules/ecs"
  project_name       = var.project_name
  aws_region         = var.aws_region
  ecr_repository_url = module.ecr.repository_url
  cluster_name       = "${var.project_name}-cluster"
  subnet_ids        = module.vpc.public_subnet_ids
  security_group_id = module.security.ecs_security_group_id
  execution_role_arn = module.iam.execution_role_arn
  task_cpu      = var.task_cpu
  task_memory   = var.task_memory
  desired_count = var.desired_count
  depends_on = [
    module.iam
  ]
}
