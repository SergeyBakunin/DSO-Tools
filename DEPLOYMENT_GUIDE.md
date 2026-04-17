# Руководство по развёртыванию — DevSecOps Tools v1.6.7

---

## Схема развёртывания

```
[Windows/Mac — разработка]         [Ubuntu VDI/сервер — production]
   Исходный код                          Docker pull
   docker buildx build  ──────────►  docker compose up
   docker push                           :3000 (frontend)
      │                                  :8000 (backend)
      ▼
   DockerHub
   sergeybakunin/devsecops-tools-*
```

---

## Вариант 1: Готовые образы с DockerHub (рекомендуется) ⭐

**Используется на VDI/сервере Ubuntu:**

```bash
# Скачать образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.7
docker pull sergeybakunin/devsecops-tools-frontend:1.6.7

# Обновить версию в docker-compose.yml
sed -i 's/1\.[0-9]\.[0-9]/1.6.7/g' docker-compose.yml

# Запустить (без пересборки)
docker compose up -d --no-build
```

> **Важно:** флаг `--no-build` обязателен, если в docker-compose.yml есть секция `build:`.
> Без него compose попытается собрать образы из исходников, которых нет на сервере.

### Проверка:

```bash
docker ps
# devsecops-backend  — должен быть healthy
# devsecops-frontend — должен быть running

docker logs devsecops-backend --tail 20
```

### Обновление до новой версии:

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.7
docker pull sergeybakunin/devsecops-tools-frontend:1.6.7
docker compose down
docker compose up -d --no-build
```

---

## Вариант 2: Сборка из исходников

> Используется при разработке или если нет доступа к DockerHub.

### На ARM Windows (buildx обязателен):

```bash
# Backend
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.7 ./backend

# Frontend
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.7 ./frontend
```

### На Linux (x86_64):

```bash
docker build -t sergeybakunin/devsecops-tools-backend:1.6.7 ./backend
docker build -t sergeybakunin/devsecops-tools-frontend:1.6.7 ./frontend
docker push sergeybakunin/devsecops-tools-backend:1.6.7
docker push sergeybakunin/devsecops-tools-frontend:1.6.7
```

---

## docker-compose.yml

```yaml
services:
  backend:
    image: sergeybakunin/devsecops-tools-backend:1.6.7
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
    image: sergeybakunin/devsecops-tools-frontend:1.6.7
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

> **Конфиг:** `backend/config.yaml` должен лежать рядом с docker-compose.yml.
> Содержит настройки Artifactory и CodeScoring API.

---

## Конфигурация backend (`config.yaml`)

```yaml
artifactory:
  url: https://artifactory.example.com
  username: user
  password: token

codescoring:
  url: https://codescoring.example.com
  api_key: your-api-key
```

---

## Nginx (включён во frontend образ)

Frontend образ содержит nginx с проксированием `/api` → `http://backend:8000`.
Это означает, что все API запросы из браузера идут через nginx, а не напрямую к backend.

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_read_timeout 300s;
}
```

Изменить конфиг nginx: `frontend/nginx.conf` → пересобрать образ.

---

## Доступ

| Адрес | Описание |
|---|---|
| http://localhost:3000 | Веб-интерфейс |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger UI |
| http://`<server-ip>`:3000 | Доступ из сети |

### Открыть доступ из сети (Linux):

```bash
# UFW firewall
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

### Открыть доступ из сети (Windows):

```powershell
New-NetFirewallRule -DisplayName "DevSecOps Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "DevSecOps Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
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

# Остановка с удалением томов
docker compose down -v
```

---

## Очистка старых образов

```bash
# Удалить конкретную версию
docker rmi sergeybakunin/devsecops-tools-backend:1.6.4
docker rmi sergeybakunin/devsecops-tools-frontend:1.6.4

# Удалить все неиспользуемые образы
docker image prune -a
```

---

## Диагностика проблем

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
Убедитесь что контейнеры в одной сети (`devsecops-network`) и backend называется именно `backend` (совпадает с nginx.conf `proxy_pass http://backend:8000`).

---

**Версия:** 1.6.7 | **Обновлено:** 17 апреля 2026
