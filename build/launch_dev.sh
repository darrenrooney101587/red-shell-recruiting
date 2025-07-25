docker-compose -f docker-compose.dev.yml down --remove-orphans -v
read -p "Run docker system prune to clean up old networks? [y/N]: " confirm && \
[ "$confirm" = "y" ] && docker system prune --force
docker-compose -f docker-compose.dev.yml --env-file .env up  --build -d
