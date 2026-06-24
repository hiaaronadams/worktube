FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# init_db is idempotent (create tables + seed sources), then serve.
# The compose file gates startup on the db healthcheck.
CMD ["sh", "-c", "python -m app.scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
