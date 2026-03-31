FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости для аналитики
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    sqlalchemy \
    pymysql \
    matplotlib \
    seaborn

# Копируем скрипт аналитики (если есть)
# COPY analytics.py .

# Команда по умолчанию - можно запускать аналитику в интерактивном режиме
CMD ["python", "-c", "print('Analytics container ready. Use kubectl exec to run analysis.')"]