#!/bin/bash
# Install required packages
sudo yum update -y
sudo yum install -y docker git python3 libxcrypt-compat

# Create docker group if missing
if ! getent group docker > /dev/null; then
  sudo groupadd docker
fi

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

# Ensure project directory exists and clone if missing
if [ ! -d "/home/ec2-user/red-shell-recruiting" ]; then
  cd /home/ec2-user
  sudo -u ec2-user git clone https://github.com/darrenrooney101587/red-shell-recruiting red-shell-recruiting
  sudo chown -R ec2-user:docker red-shell-recruiting
fi

cd /home/ec2-user/red-shell-recruiting

# Pull latest changes
sudo -u ec2-user git pull

# Parametrize docker-compose command based on DEPLOY_ENV
DEPLOY_ENV="${DEPLOY_ENV:-prod}"
if [ "$DEPLOY_ENV" = "prod" ]; then
  sudo -u ec2-user docker-compose -f docker-compose.prod.yml --env-file .env.prod --profile production up --build -d
else
  sudo -u ec2-user docker-compose -f docker-compose.local.yml  --env-file .env up -d
fi
