docker-compose down --remove-orphans
docker-compose --env-file .env.prod --profile production up --build -d
