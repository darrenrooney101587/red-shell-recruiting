docker-compose -f docker-compose.prod.yml down --remove-orphans -v
read -p "Run docker system prune to clean up old networks? [y/N]: " confirm && \
[ "$confirm" = "y" ] && docker system prune --force
docker-compose -f docker-compose.prod.yml  --env-file .env.prod --profile production up --build -d
