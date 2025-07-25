provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

resource "aws_vpc" "main" {
  cidr_block     = "172.31.0.0/16"
  instance_tenancy = "default"

  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "red-shell-dev-vpc"
  }
}

resource "aws_subnet" "public_2b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.64.0/24"
  availability_zone       = "us-east-2b"
  map_public_ip_on_launch = false

  tags = {
    Name = "red-shell-public-2b"
  }
}

resource "aws_subnet" "rds_public_2b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.100.0/24"
  availability_zone       = "us-east-2b"
  map_public_ip_on_launch = true

  tags = {
    Name = "rds-public-subnet-2b"
  }
}

resource "aws_subnet" "rds_public_2a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.101.0/24"
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "rds-public-subnet-2a"
  }
}

resource "aws_subnet" "rds_pvt_3" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.49.0/25"
  availability_zone       = "us-east-2b"
  map_public_ip_on_launch = false

  tags = {
    Name = "RDS-Pvt-subnet-3"
  }
}

resource "aws_subnet" "public_2c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.32.0/20"
  availability_zone       = "us-east-2c"
  map_public_ip_on_launch = true

  tags = {
    Name = "red-shell-public-2c"
  }
}

resource "aws_security_group" "red_shell_prod_sg" {
  name        = "red-shell-sg"
  description = "Allow SSH, HTTP, HTTPS, PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eip" "web_eip" {
}

resource "aws_eip_association" "eip_attach" {
  instance_id   = aws_instance.web.id
  allocation_id = var.eip_allocation_id != "" ? var.eip_allocation_id : aws_eip.web_eip.id
}

output "instance_public_dns" {
  value = aws_instance.web.public_dns
}

output "instance_id" {
  value = aws_instance.web.id
}

resource "aws_instance" "web" {
  ami                    = var.ami_id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public_2b.id
  vpc_security_group_ids = [aws_security_group.red_shell_prod_sg.id]
  key_name               = var.key_name
  associate_public_ip_address = true

  root_block_device {
    delete_on_termination = false
  }

  user_data = file("${path.module}/web_app_startup.sh")

  tags = {
    Name = var.instance_name
  }
}

resource "aws_s3_bucket" "red_shell_recruiting" {
  bucket = "red-shell-recruiting"
}

resource "aws_s3_bucket_versioning" "red_shell_recruiting_versioning" {
  bucket = aws_s3_bucket.red_shell_recruiting.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name = "red-shell-db-credentials"
}

resource "aws_secretsmanager_secret_version" "db_credentials_version" {
  secret_id     = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
  })
}

resource "aws_iam_user" "file_uploader" {
  name = "redshell-recruiting-file-uploader"
}

resource "aws_iam_policy" "file_uploader_s3_policy" {
  name        = "redshell-recruiting-file-uploader-s3-policy"
  description = "Allow file uploader to put, get, list, and delete objects in the S3 bucket."
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowS3UploadsAndDownloads",
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Resource = [
          aws_s3_bucket.red_shell_recruiting.arn,
          "${aws_s3_bucket.red_shell_recruiting.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "file_uploader_attach" {
  user       = aws_iam_user.file_uploader.name
  policy_arn = aws_iam_policy.file_uploader_s3_policy.arn
}

resource "aws_internet_gateway" "main_gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "red-shell-dev-gateway"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "red-shell-public-rt"
  }
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main_gw.id
}

resource "aws_route_table_association" "public_2b_assoc" {
  subnet_id      = aws_subnet.public_2b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_2c_assoc" {
  subnet_id      = aws_subnet.public_2c.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "rds_public_2a_assoc" {
  subnet_id      = aws_subnet.rds_public_2a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "rds_public_2b_assoc" {
  subnet_id      = aws_subnet.rds_public_2b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_key_pair" "dev_key" {
  key_name   = var.key_name
  public_key = file("~/.ssh/red-shell-recruiting-dev.pub")
}
