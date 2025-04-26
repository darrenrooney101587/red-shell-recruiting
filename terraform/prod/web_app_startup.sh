#!/bin/bash
# Install Docker if not installed
if ! command -v docker &> /dev/null
then
  yum update -y
  amazon-linux-extras install docker -y
  systemctl start docker
  systemctl enable docker
  usermod -a -G docker ec2-user
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null
then
  curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
fi

# Move into project directory
cd /home/ec2-user/red-shell-recruiting

# Pull latest changes (optional, if you use GitHub and want auto-update)
# sudo -u ec2-user git pull

# Bring up docker-compose (production profile)
docker-compose -f docker-comopose.prod.yml --profile production up -d
