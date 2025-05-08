FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    lsb-release \
    wget \
    gnupg2 \
    && mkdir -p /etc/apt/keyrings \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/keyrings/postgres.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/postgres.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/postgres.list \
    && apt-get update \
    && apt-get install -y postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout=100 -r requirements.txt
RUN playwright install --with-deps chromium

COPY app/ .

CMD alembic upgrade head && python main.py