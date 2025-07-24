provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "public_2b" {
  filter {
    name   = "tag:Name"
    values = ["red-shell-public-2b"]
  }
  availability_zone = "us-east-2b"
}

resource "aws_security_group" "red_shell_prod_sg" {
  name        = "red-shell-prod-sg"
  description = "Allow SSH, HTTP, HTTPS, PostgreSQL"
  vpc_id      = data.aws_vpc.default.id

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

resource "aws_eip_association" "eip_attach" {
  instance_id   = aws_instance.web.id
  allocation_id = var.eip_allocation_id
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
  subnet_id              = var.public_subnet_id
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

resource "aws_s3_bucket" "red_shell_recruiting_prod" {
  bucket = "red-shell-recruiting-prod"
}

resource "aws_s3_bucket_versioning" "red_shell_recruiting_prod_versioning" {
  bucket = aws_s3_bucket.red_shell_recruiting_prod.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "red_shell_recruiting_dev" {
  bucket = "red-shell-recruiting-dev"
}

resource "aws_s3_bucket_versioning" "red_shell_recruiting_dev_versioning" {
  bucket = aws_s3_bucket.red_shell_recruiting_dev.id
  versioning_configuration {
    status = "Enabled"
  }
}
