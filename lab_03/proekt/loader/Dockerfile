FROM python:3.9-slim

WORKDIR /loader

RUN pip install --no-cache-dir pymysql faker

COPY loader.py .

CMD ["python", "loader.py"]
