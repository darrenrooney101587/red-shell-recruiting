resource "aws_db_subnet_group" "rds_public" {
  name       = "rds-public-subnet-group"
  subnet_ids = [
    aws_subnet.rds_pvt_3.id,
    aws_subnet.rds_public_2a.id,
    aws_subnet.rds_public_2b.id,
    aws_subnet.public_2c.id
  ]

  tags = {
    Name = "rds-public-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier              = var.db_identifier
  engine                  = "postgres"
  engine_version          = "15"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  db_name                 = "postgres"
  username                = var.db_username
  password                = var.db_password
  publicly_accessible     = true
  db_subnet_group_name    = aws_db_subnet_group.rds_public.name
  vpc_security_group_ids  = [aws_security_group.red_shell_prod_sg.id]
  skip_final_snapshot     = true
  availability_zone       = "us-east-2b"
}
