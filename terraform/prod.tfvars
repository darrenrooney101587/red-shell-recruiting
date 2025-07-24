aws_profile = "red-shell-recruiting-prod"
aws_region = "us-east-2"
ami_id            = "ami-02f761c2f5c9bbbe5"
eip_allocation_id = "eipalloc-09592bf7d01c5e4ba"
db_password     = "your-secure-db-password"
rds_subnet_ids  = [
  "subnet-04b5e85714dc5b310", # RDS-Pvt-subnet-3 (us-east-2b)
  "subnet-0247f4fc1d6d0dd82", # rds-public-subnet-2a (us-east-2a)
  "subnet-007fc5d7bbda40c3b", # rds-public-subnet-2b (us-east-2b)
  "subnet-0feeb254527036127"  # (us-east-2c)
]
public_subnet_id = "subnet-05e07bd38994bc4d0" # red-shell-public-2b (us-east-2b)
