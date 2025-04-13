#!/bin/bash

# Config
CONTAINER_NAME="red-shell-recruiting-db-1"
DB_NAME="postgres"
DB_USER="postgres"
BACKUP_DIR="/home/ec2-user/pg_backups"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/db_backup_${DATE}.sql"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Run the backup
echo "Backing up database '${DB_NAME}' from container '${CONTAINER_NAME}'..."
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$FILENAME"

echo "Backup saved to $FILENAME"
