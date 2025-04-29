docker-compose -f docker-compose.local.yml  --env-file .env down
docker-compose -f docker-compose.local.yml  --env-file .env up --build  -d
