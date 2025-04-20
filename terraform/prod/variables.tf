variable "instance_name" {
  default = "red-shell-prod"
}

variable "ami_id" {
  description = "red-shell-prod-baseline-ami"
  default     = "ami-0040f336065e0e50b"
}

variable "key_name" {
  default = "red-shell-recruiting-dev"
}

variable "eip_allocation_id" {
  description = "Elastic IP allocation ID to reuse"
  default     = "eipalloc-09592bf7d01c5e4ba"
}
