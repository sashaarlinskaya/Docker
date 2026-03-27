#!/bin/bash


echo "Запуск Docker контейнера..."

# Запускаем контейнер в фоне и сохраняем имя
CONTAINER_NAME="python-container-$(date +%s)"
docker run -d --name $CONTAINER_NAME python:3.9-slim sleep infinity

echo "Создаем файл script.py внутри запущенного контейнера..."
docker exec $CONTAINER_NAME sh -c "echo 'print(\"Hello Data Analysis\")' > script.py"

echo "Выполняем скрипт:"
docker exec $CONTAINER_NAME python script.py

