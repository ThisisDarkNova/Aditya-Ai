# Multi-stage Dockerfile for Aether-1.0.0 testing and execution
FROM python:3.11-slim AS backend-builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY backend/ /app/backend/

# Node environment builder
FROM node:20-slim AS frontend-builder

WORKDIR /app/client

COPY client/package.json client/package-lock.json ./
RUN npm ci

COPY client/ /app/client/
RUN npm run build

# Final image
FROM python:3.11-slim

WORKDIR /app

COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin
COPY --from=backend-builder /app/backend /app/backend
COPY --from=frontend-builder /app/client/dist /app/client/dist

EXPOSE 7865

CMD ["python", "backend/main.py"]
