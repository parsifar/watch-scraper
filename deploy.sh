#!/bin/bash
APP_NAME=watch-scraper
cd ~/apps/$APP_NAME
git pull
docker build -t $APP_NAME .
docker stop $APP_NAME
docker rm $APP_NAME
docker run -d --name $APP_NAME -p 8000:8000 $APP_NAME
