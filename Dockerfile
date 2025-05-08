FROM python:3.12-slim

RUN apt-get update && apt-get install -y

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout=100 -r requirements.txt
RUN playwright install --with-deps chromium

COPY app/ .

CMD alembic upgrade head && python main.py