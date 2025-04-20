variable "instance_name" {
  description = "The name tag for the EC2 instance"
  type        = string
  default     = "red-shell-prod"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance (must exist in us-east-2)"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name to use for EC2 instance"
  type        = string
  default     = "red-shell-recruiting-dev"
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

variable "rds_subnet_ids" {
  description = "List of subnet IDs for RDS subnet group"
  type        = list(string)
}