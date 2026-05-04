# Руководство по развёртыванию — DevSecOps Tools v1.6.8

---

## Схема развёртывания

```
[Разработка]                       [Production — VDI/сервер Ubuntu]
  Исходный код                           Docker pull
  docker buildx build  ──────────►   docker compose up
  docker push                            :3000 (frontend)
       │                                 :8000 (backend API)
       ▼
  DockerHub
  sergeybakunin/devsecops-tools-*
```

---

## Вариант 1: Готовые образы с DockerHub (рекомендуется)

```bash
# Скачать образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.8
docker pull sergeybakunin/devsecops-tools-frontend:1.6.8

# Запустить (из папки docker/)
cd docker
docker compose up -d --no-build
```

> Флаг `--no-build` обязателен — без него compose попытается собрать образы из исходников.

### Проверка

```bash
docker ps
# devsecops-backend  — healthy
# devsecops-frontend — running

docker logs devsecops-backend --tail 20
```

### Обновление до новой версии

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.8
docker pull sergeybakunin/devsecops-tools-frontend:1.6.8
docker compose down
docker compose up -d --no-build
```

---

## Вариант 2: Сборка из исходников

### ARM Windows / Mac (buildx обязателен)

```bash
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.8 ./backend

docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.8 ./frontend
```

### Linux x86_64

```bash
docker build -t sergeybakunin/devsecops-tools-backend:1.6.8 ./backend
docker build -t sergeybakunin/devsecops-tools-frontend:1.6.8 ./frontend
docker push sergeybakunin/devsecops-tools-backend:1.6.8
docker push sergeybakunin/devsecops-tools-frontend:1.6.8
```

---

## docker-compose.yml

```yaml
services:
  backend:
    image: sergeybakunin/devsecops-tools-backend:1.6.8
    container_name: devsecops-backend
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml:ro
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
    image: sergeybakunin/devsecops-tools-frontend:1.6.8
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

> `config.yaml` должен лежать рядом с `docker-compose.yml`. Содержит настройки Artifactory и CodeScoring.

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

Frontend образ содержит nginx, который проксирует `/api/*` → `http://backend:8000`.
Все API запросы из браузера идут через nginx, не напрямую к backend.

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_read_timeout 300s;
    client_max_body_size 100m;
}
```

Изменить конфиг: `frontend/nginx.conf` → пересобрать frontend образ.

---

## Доступ

| Адрес | Описание |
|---|---|
| http://localhost:3000 | Веб-интерфейс |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger UI |
| http://`<server-ip>`:3000 | Доступ из сети |

### Открыть порты (Linux/UFW)

```bash
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

---

## Управление контейнерами

```bash
docker compose ps                      # статус
docker logs devsecops-backend -f       # логи backend
docker compose restart backend         # перезапуск сервиса
docker compose down                    # остановка
docker compose down -v                 # остановка с удалением томов
```

---

## Очистка старых образов

```bash
docker rmi sergeybakunin/devsecops-tools-backend:1.6.7
docker rmi sergeybakunin/devsecops-tools-frontend:1.6.7
docker image prune -a                  # все неиспользуемые
```

---

## Диагностика

### exec format error
```bash
docker inspect <image> --format '{{.Architecture}}'
# arm64 на x86_64 сервере — пересобрать с --platform linux/amd64
```

### Backend unhealthy
```bash
docker logs devsecops-backend --tail 30
```

### Frontend не проксирует API
Убедитесь, что контейнеры в одной сети `devsecops-network` и backend-контейнер называется `backend` (совпадает с `proxy_pass http://backend:8000` в nginx.conf).

---

**Версия:** 1.6.8 | **Обновлено:** 04 мая 2026
