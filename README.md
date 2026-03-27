# Docker

#!/bin/bash

# start.sh
# Задание: Запустить контейнер, создать внутри файл script.py
# (выводящий "Hello Data Analysis"), выполнить его и получить результат

echo "Запуск Docker контейнера и выполнение Python скрипта..."
echo ""

# Docker автоматически скачает образ python:3.9-slim, если его нет локально
# Запускаем контейнер, создаем script.py внутри и выполняем его
docker run --rm python:3.9-slim sh -c "
    echo 'Создаю файл script.py...' &&
    echo 'print(\"Hello Data Analysis\")' > script.py &&
    echo '' &&
    echo 'Содержимое script.py:' &&
    cat script.py &&
    echo '' &&
    echo 'Результат выполнения:' &&
    python script.py
"

echo ""
echo "Готово!"
