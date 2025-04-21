docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose --env-file .env.prod --profile production up --build -d
