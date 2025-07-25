variable "instance_name" {
  description = "The name tag for the EC2 instance"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance (must exist in us-east-2)"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name to use for EC2 instance"
  type        = string
}

variable "eip_allocation_id" {
  description = "Elastic IP allocation ID to attach to the EC2 instance"
  type        = string
}

variable "db_identifier" {
  description = "RDS instance identifier"
  type        = string
  default     = "client-database-1"
}

variable "db_username" {
  description = "Master username for the RDS instance"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for the RDS instance"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  type    = string
  default = "us-east-2"
}

variable "aws_profile" {
  type = string
}

variable "route53_zone_name" {
  description = "The domain name for the Route53 hosted zone (e.g., redshellrecruiting.com or dev.redshellrecruiting.com)"
  type        = string
}

variable "deploy_env" {
  description = "Deployment environment (dev or prod)"
  type        = string
  default     = "prod"
}
