# Docker — Руководство по сборке и запуску

**Версия:** 1.6.5 | **Обновлено:** 07 апреля 2026

---

## Предварительные требования

- **Docker Engine** или **Docker Desktop**
- Для сборки с ARM-хоста (Windows M-series): Docker Buildx (входит в Docker Desktop)

```bash
docker --version
docker compose version
```

---

## Быстрый старт — готовые образы с DockerHub

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.5
docker pull sergeybakunin/devsecops-tools-frontend:1.6.5

# Из папки с docker-compose.yml
docker compose up -d --no-build
```

Открыть: **http://localhost:3000**

> **Почему `--no-build`?** На сервере нет исходников. Без этого флага `docker compose` попытается собрать образы из `build: context:`, которого не существует, и упадёт с ошибкой.

---

## Сборка из исходников

### На ARM-хосте (Windows с процессором ARM, Apple M-series)

Обязательно указывать `--platform linux/amd64` и использовать `--push` (минует локальный ARM-кеш):

```bash
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.5 ./backend

docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.5 ./frontend
```

### На Linux x86_64

```bash
docker build -t sergeybakunin/devsecops-tools-backend:1.6.5 ./backend
docker build -t sergeybakunin/devsecops-tools-frontend:1.6.5 ./frontend

docker push sergeybakunin/devsecops-tools-backend:1.6.5
docker push sergeybakunin/devsecops-tools-frontend:1.6.5
```

---

## docker-compose.yml

Файл находится в `docker/docker-compose.yml`.

```yaml
services:
  backend:
    image: sergeybakunin/devsecops-tools-backend:1.6.5
    container_name: devsecops-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/config.yaml:/app/config.yaml:ro
    networks:
      - devsecops-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  frontend:
    image: sergeybakunin/devsecops-tools-frontend:1.6.5
    container_name: devsecops-frontend
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - devsecops-network
    restart: unless-stopped

networks:
  devsecops-network:
    driver: bridge
```

---

## Управление контейнерами

```bash
# Статус
docker compose ps

# Логи
docker logs devsecops-backend -f
docker logs devsecops-frontend -f

# Перезапуск одного сервиса
docker compose restart backend

# Остановка
docker compose down

# Остановка с удалением volumes
docker compose down -v
```

---

## Обновление до новой версии

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.5
docker pull sergeybakunin/devsecops-tools-frontend:1.6.5
docker compose down
docker compose up -d --no-build
```

---

## Подключение к контейнеру

```bash
# Backend
docker exec -it devsecops-backend /bin/bash

# Frontend (nginx)
docker exec -it devsecops-frontend /bin/sh
```

---

## Очистка образов

```bash
# Удалить конкретную версию
docker rmi sergeybakunin/devsecops-tools-backend:1.6.4
docker rmi sergeybakunin/devsecops-tools-frontend:1.6.4

# Все неиспользуемые образы
docker image prune -a

# Полная очистка Docker системы (осторожно!)
docker system prune -a --volumes
```

---

## Troubleshooting

### `exec format error`

Образ собран под неправильную архитектуру.

```bash
docker inspect <image> --format '{{.Architecture}}'
# Если arm64, а сервер x86_64 — нужно пересобрать с --platform linux/amd64
```

### Backend unhealthy

```bash
docker logs devsecops-backend --tail 30
```

### Frontend не проксирует API

Убедитесь что:
- Оба контейнера в одной сети (`devsecops-network`)
- Backend называется `backend` (совпадает с nginx.conf `proxy_pass http://backend:8000`)

### Порт уже занят

```bash
# Linux
lsof -i :3000

# Windows
netstat -ano | findstr :3000
```

---

## Nginx (включён во frontend образ)

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_read_timeout 300s;
}
```

Изменить конфиг: `frontend/nginx.conf` → пересобрать образ.

---

## Архитектура контейнеров

| | Backend | Frontend |
|---|---|---|
| **Base image** | python:3.13-slim | nginx:alpine (multi-stage) |
| **Port** | 8000 | 80 → 3000 |
| **Health check** | HTTP GET / | HTTP GET /health |
