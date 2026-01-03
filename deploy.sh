#!/bin/bash

APP_NAME=watch-scraper
HOST_PORT=8000
ENV_FILE=.env.production

cd ~/apps/$APP_NAME || { echo "App folder not found"; exit 1; }

echo "Pulling latest code..."
git pull

echo "Building Docker image..."
docker build -t $APP_NAME .

echo "Stopping old container if exists..."
docker stop $APP_NAME || true
docker rm $APP_NAME || true

echo "Running new container..."
docker run -d \
  --name $APP_NAME \
  -p $HOST_PORT:8000 \
  --env-file $ENV_FILE \
  --restart unless-stopped \
  $APP_NAME

echo "Deployment complete. Container is running on port $HOST_PORT"
