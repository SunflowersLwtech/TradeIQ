# ─── TradeIQ Backend ───────────────────────────────────────
# Django + Channels (Daphne ASGI) for HTTP + WebSocket
# ───────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

COPY . .

# Collect static files (Django admin / DRF browsable API)
RUN DJANGO_SECRET_KEY=build-placeholder \
    DATABASE_URL="" \
    python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# Daphne for ASGI (supports HTTP + WebSocket)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "tradeiq.asgi:application"]
