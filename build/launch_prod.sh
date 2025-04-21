docker-compose -f docker-compose.prod.yaml down --remove-orphans
docker-compose --env-file .env.prod --profile production up --build -d
