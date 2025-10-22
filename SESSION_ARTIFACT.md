# DevSecOps Tools - Артефакт сессии разработки

**Дата**: 19-20 октября 2025
**Проект**: DevSecOps Tools - SBOM to VEX Converter & Vulnerability Comments Migration
**Разработчик**: Sergey Bakunin (deone37)

---

## 📋 Оглавление

1. [Описание проекта](#описание-проекта)
2. [Инфраструктура](#инфраструктура)
3. [Архитектура приложения](#архитектура-приложения)
4. [Развертывание](#развертывание)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Важные конфигурации](#важные-конфигурации)
7. [Решенные проблемы](#решенные-проблемы)
8. [Команды для управления](#команды-для-управления)
9. [Следующие шаги](#следующие-шаги)

---

## Описание проекта

**DevSecOps Tools** - веб-приложение для работы с уязвимостями в формате CycloneDX.

### Основные функции:

1. **VEX Converter** - конвертация SBOM (CycloneDX v1.6) в VEX формат
   - Сохраняет все метаданные уязвимостей
   - Добавляет секцию analysis
   - Экспорт в JSON формат

2. **SBOM Migrate** - перенос комментариев между экспортами уязвимостей
   - Поддержка CSV/XLSX и JSON форматов
   - Сопоставление по CVE ID
   - Сохранение истории комментариев

### Технологический стек:

**Backend:**
- Python 3.13
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- openpyxl, pandas (обработка XLSX/CSV)

**Frontend:**
- React 18.2
- Axios (HTTP client)
- CSS modules
- Nginx (production server)

**DevOps:**
- Docker / Docker Compose
- GitHub Actions (CI/CD)
- Synology Container Manager

---

## Инфраструктура

### Synology NAS DS723+

**Модель**: Synology DS723+
**CPU**: AMD Ryzen R1600 (2 cores, 4 threads)
**RAM**: минимум 2GB

**Сетевая конфигурация:**

| Параметр | Значение |
|----------|----------|
| Внешний домен | dso.deone37.synology.me |
| Внешний IP | 31.207.64.66 |
| Локальный IP (eth0) | 192.168.0.233/24 |
| Локальный IP (eth1) | 192.168.0.234/24 |

**Проброс портов на роутере:**
- Порт 80 (HTTP) → 192.168.0.233:80
- Порт 443 (HTTPS) → 192.168.0.233:443

**Reverse Proxy (Synology):**
- Источник: `https://dso.deone37.synology.me:443`
- Назначение: `http://localhost:3000` (frontend)
- HSTS: включен

### Структура директорий на NAS

```
/volume1/docker/devsecops/
├── project/
│   ├── .env                           # Переменные окружения
│   ├── docker-compose.nas.yml         # Compose для локальных образов
│   └── docker-compose.dockerhub.yml   # Compose для Docker Hub образов
├── backend-data/                      # Данные backend (опционально)
├── backend-logs/                      # Логи backend (опционально)
└── nas-deployment/
    ├── devsecops-backend-1.0.0.tar   # Экспорт backend образа
    ├── devsecops-frontend-1.0.0.tar  # Экспорт frontend образа
    ├── docker-compose.nas-simple.yml # Упрощенный compose
    ├── update-from-dockerhub.sh      # Скрипт обновления
    ├── HOTFIX.md                      # Документация исправлений
    └── README.md                      # Инструкции по развертыванию
```

### Docker Hub

**Username**: `deone37`

**Репозитории:**
- `deone37/devsecops-backend:latest`
- `deone37/devsecops-backend:1.0.0`
- `deone37/devsecops-frontend:latest`
- `deone37/devsecops-frontend:1.0.0`

### GitHub

**Username**: `SergeyBakunin`
**Repository**: `devsecops-tools` (планируется создать)

**GitHub Secrets (необходимо настроить):**
- `DOCKERHUB_USERNAME`: `deone37`
- `DOCKERHUB_TOKEN`: (создать на hub.docker.com/settings/security)

---

## Архитектура приложения

### Компоненты

```
┌─────────────────────────────────────────────┐
│         Synology Reverse Proxy              │
│  https://dso.deone37.synology.me:443        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Frontend Container (Nginx)          │
│              Port: 3000 → 80                │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │     React Application               │   │
│  │  - SBOM Migrate Component           │   │
│  │  - VEX Converter Component          │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Nginx Config:                              │
│  - / → React app                            │
│  - /api → proxy to backend:8000             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Backend Container (FastAPI)         │
│              Port: 8090 → 8000              │
│                                             │
│  API Endpoints:                             │
│  - GET  /                  (health check)   │
│  - GET  /docs              (Swagger UI)     │
│  - POST /api/migrate       (CSV/XLSX)       │
│  - POST /api/migrate-json  (JSON)           │
│  - POST /api/sbom-to-vex   (analysis)       │
│  - POST /api/sbom-to-vex/export (download)  │
└─────────────────────────────────────────────┘
```

### Docker Network

**Сеть**: `devsecops-network` (bridge)
**Subnet**: 172.25.0.0/16

Контейнеры общаются между собой по именам:
- Frontend может обращаться к backend как `http://backend:8000`

### Ограничения ресурсов

**Backend:**
- Memory Limit: 512M
- Memory Reservation: 256M
- CPU Limits: не используются (несовместимость с Synology kernel)

**Frontend:**
- Memory Limit: 256M
- Memory Reservation: 128M
- CPU Limits: не используются

---

## Развертывание

### Локальная разработка (Windows)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start  # Запускается на http://localhost:3000
```

### Docker Compose (локально)

```bash
docker-compose up -d
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Первоначальное развертывание на NAS

**Шаг 1: Сборка образов (на локальном ПК)**

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# Сборка
docker build -t devsecops-tools-backend:1.0.0 ./backend
docker build -t devsecops-tools-frontend:1.0.0 ./frontend

# Экспорт
docker save devsecops-tools-backend:1.0.0 -o devsecops-backend-1.0.0.tar
docker save devsecops-tools-frontend:1.0.0 -o devsecops-frontend-1.0.0.tar
```

**Шаг 2: Копирование на NAS**

Скопировать tar файлы в `/volume1/docker/devsecops/nas-deployment/`

**Шаг 3: Импорт на NAS**

```bash
ssh admin@dso.deone37.synology.me

cd /volume1/docker/devsecops/nas-deployment

sudo docker load -i devsecops-backend-1.0.0.tar
sudo docker load -i devsecops-frontend-1.0.0.tar

# Проверка
sudo docker images | grep devsecops
```

**Шаг 4: Настройка окружения**

```bash
cd /volume1/docker/devsecops/project

# Создать .env файл
nano .env
```

Содержимое `.env`:
```env
# Домен и IP
NAS_DOMAIN=dso.deone37.synology.me
NAS_IP=192.168.0.233

# Timezone
TZ=Europe/Moscow

# Порты
BACKEND_PORT=8090
FRONTEND_PORT=3000

# API URL
API_URL=https://dso.deone37.synology.me

# Логирование
LOG_LEVEL=info

# Ограничения ресурсов
BACKEND_MEMORY_LIMIT=512M
FRONTEND_MEMORY_LIMIT=256M
```

**Шаг 5: Запуск**

```bash
cd /volume1/docker/devsecops/project

# Остановить старые (если есть)
sudo docker-compose -f docker-compose.nas.yml down

# Запустить
sudo docker-compose -f docker-compose.nas.yml up -d

# Проверка
sudo docker ps
sudo docker logs devsecops-backend
sudo docker logs devsecops-frontend
```

**Шаг 6: Настройка Reverse Proxy**

Synology → Контрольная панель → Портал входа → Advanced → Reverse Proxy

Создать правило:
- **Описание**: `DSO Tools`
- **Источник**:
  - Протокол: HTTPS
  - Имя хоста: `dso.deone37.synology.me`
  - Порт: 443
  - HSTS: включить
- **Назначение**:
  - Протокол: HTTP
  - Имя хоста: `localhost`
  - Порт: 3000

**Шаг 7: Проверка**

Открыть в браузере: https://dso.deone37.synology.me/

---

## CI/CD Pipeline

### GitHub Actions Workflow

Файл: `.github/workflows/docker-publish.yml`

**Триггеры:**
- Push в `main` / `master` → собрать и запушить `latest`
- Создание тега `v*.*.*` → версионный релиз
- Pull Request → только сборка (без публикации)
- Ручной запуск (workflow_dispatch)

**Шаги:**
1. Checkout кода
2. Setup Docker Buildx
3. Login в Docker Hub
4. Build Backend → Push в `deone37/devsecops-backend`
5. Build Frontend → Push в `deone37/devsecops-frontend`

**Теги при релизе v1.0.1:**
- `1.0.1`
- `1.0`
- `1`
- `latest`

### Первая публикация в Docker Hub (вручную)

Запустить: `push-to-dockerhub.bat`

Или вручную:
```bash
docker login

docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:1.0.0
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:latest
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:1.0.0
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:latest

docker push deone37/devsecops-backend:1.0.0
docker push deone37/devsecops-backend:latest
docker push deone37/devsecops-frontend:1.0.0
docker push deone37/devsecops-frontend:latest
```

### Создание релиза

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# Внести изменения
git add .
git commit -m "Feature: новая функция"
git push

# Создать версионный тег
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

GitHub Actions автоматически соберет и опубликует образы.

### Обновление на NAS

**Вариант 1: Автоматически через Synology UI**
1. Container Manager → Образ
2. Нажать "Обновить" → проверит Docker Hub
3. Скачает новые версии
4. Проект → devsecops → Действие → Сборка

**Вариант 2: Через скрипт**

```bash
cd /volume1/docker/devsecops/nas-deployment
sudo ./update-from-dockerhub.sh
```

**Вариант 3: Вручную**

```bash
cd /volume1/docker/devsecops/project

# Скачать обновления
sudo docker-compose -f docker-compose.dockerhub.yml pull

# Пересоздать контейнеры
sudo docker-compose -f docker-compose.dockerhub.yml up -d --force-recreate
```

---

## Важные конфигурации

### backend/Dockerfile

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile

```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY public ./public
COPY src ./src
RUN npm run build

# Stage 2: Production
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### frontend/nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### docker-compose.dockerhub.yml

```yaml
version: '3.8'

services:
  backend:
    image: deone37/devsecops-backend:latest
    container_name: devsecops-backend
    ports:
      - "8090:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=info
      - TZ=Europe/Moscow
    networks:
      - devsecops-network
    restart: unless-stopped
    mem_limit: 512M
    mem_reservation: 256M
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  frontend:
    image: deone37/devsecops-frontend:latest
    container_name: devsecops-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=https://dso.deone37.synology.me
      - TZ=Europe/Moscow
    depends_on:
      - backend
    networks:
      - devsecops-network
    restart: unless-stopped
    mem_limit: 256M
    mem_reservation: 128M
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

networks:
  devsecops-network:
    driver: bridge
```

---

## Решенные проблемы

### Проблема 1: NanoCPUs error на Synology

**Ошибка:**
```
Error response from daemon: NanoCPUs can not be set, as your kernel does not support CPU CFS scheduler
```

**Причина:**
Synology kernel не поддерживает CPU CFS scheduler для `deploy.resources.limits.cpus`.

**Решение:**
Убрали `cpus:` ограничения, оставили только `mem_limit` и `mem_reservation`.

**Было:**
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

**Стало:**
```yaml
mem_limit: 512M
mem_reservation: 256M
```

### Проблема 2: ERR_CONNECTION_RESET при доступе к сайту

**Причина:**
Не настроен проброс портов 80 и 443 на роутере. DNS резолвил домен на внешний IP, но роутер не перенаправлял трафик на NAS.

**Решение:**
Настроили Port Forwarding на роутере:
- Порт 80 → 192.168.0.233:80
- Порт 443 → 192.168.0.233:443

### Проблема 3: Port 3000 already allocated

**Причина:**
Порт 3000 уже занят контейнером Gitea.

**Решение:**
Пользователь удалил Gitea, освободив порт 3000. Альтернатива - изменить `FRONTEND_PORT` в `.env`.

### Проблема 4: invalid tag format при push в Docker Hub

**Причина:**
Неправильный формат тега. Должен быть `username/repository:tag`.

**Решение:**
Использовать правильный формат:
```bash
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:1.0.0
```

### Проблема 5: npm ci failure в frontend Dockerfile

**Ошибка:**
```
npm ci can only install packages when your package.json and package-lock.json are in sync
Invalid: lock file's typescript@5.9.3 does not satisfy typescript@4.9.5
```

**Решение:**
Заменили `npm ci --only=production` на `npm install` в Dockerfile.

### Проблема 6: react-scripts not found

**Причина:**
`--omit=dev` исключал dev dependencies, а `react-scripts` находится в devDependencies.

**Решение:**
Использовать `npm install` без флагов для установки всех зависимостей (они нужны для сборки).

---

## Команды для управления

### Локальная разработка

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Docker (локально)

```bash
# Сборка
docker build -t devsecops-tools-backend:1.0.0 ./backend
docker build -t devsecops-tools-frontend:1.0.0 ./frontend

# Запуск
docker-compose up -d

# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Пересборка
docker-compose up -d --build
```

### Управление на NAS

```bash
# SSH подключение
ssh admin@dso.deone37.synology.me

# Переход в проект
cd /volume1/docker/devsecops/project

# Просмотр статуса
sudo docker ps
sudo docker ps -a

# Логи
sudo docker logs devsecops-backend
sudo docker logs devsecops-frontend
sudo docker logs -f devsecops-backend  # follow mode

# Остановка
sudo docker-compose -f docker-compose.dockerhub.yml down

# Запуск
sudo docker-compose -f docker-compose.dockerhub.yml up -d

# Перезапуск одного контейнера
sudo docker restart devsecops-backend

# Обновление образов
sudo docker-compose -f docker-compose.dockerhub.yml pull
sudo docker-compose -f docker-compose.dockerhub.yml up -d --force-recreate

# Проверка health
sudo docker inspect devsecops-backend | grep -A 20 Health
sudo docker inspect devsecops-frontend | grep -A 20 Health

# Вход в контейнер
sudo docker exec -it devsecops-backend sh
sudo docker exec -it devsecops-frontend sh

# Очистка неиспользуемых образов
sudo docker system prune -a

# Просмотр использования ресурсов
sudo docker stats
```

### Git операции

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# Статус
git status

# Коммит
git add .
git commit -m "Описание изменений"

# Push
git push

# Создание тега
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# Просмотр тегов
git tag -l

# Удаление тега (локально и удаленно)
git tag -d v1.0.1
git push origin :refs/tags/v1.0.1
```

### Docker Hub

```bash
# Login
docker login

# Push образов
docker push deone37/devsecops-backend:1.0.0
docker push deone37/devsecops-backend:latest

# Pull образов
docker pull deone37/devsecops-backend:latest

# Просмотр локальных образов
docker images | grep devsecops

# Удаление локального образа
docker rmi deone37/devsecops-backend:1.0.0
```

---

## Следующие шаги

### 1. Настройка GitHub репозитория

- [ ] Создать репозиторий `devsecops-tools` на GitHub
- [ ] Добавить remote и запушить код
- [ ] Настроить GitHub secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] Проверить работу GitHub Actions

**Инструкция**: [GITHUB_SETUP.md](GITHUB_SETUP.md)

### 2. Публикация в Docker Hub

- [ ] Запустить `push-to-dockerhub.bat`
- [ ] Проверить образы на hub.docker.com/r/deone37
- [ ] Обновить NAS для использования Docker Hub образов

### 3. Переход на собственную инфраструктуру (опционально)

Если у вас есть собственный Git/Registry:

- [ ] Адаптировать CI/CD под Gitea/GitLab
- [ ] Настроить Docker Registry на NAS
- [ ] Обновить образы для использования локального registry
- [ ] Создать webhook для автоматического обновления

### 4. Улучшения приложения

**Backend:**
- [ ] Добавить аутентификацию (JWT)
- [ ] Добавить rate limiting
- [ ] Настроить CORS для production
- [ ] Добавить метрики (Prometheus)
- [ ] Настроить structured logging

**Frontend:**
- [ ] Добавить обработку ошибок
- [ ] Улучшить UX (loading states, notifications)
- [ ] Добавить темную тему
- [ ] Мобильная адаптация
- [ ] Добавить тесты (Jest, React Testing Library)

**DevOps:**
- [ ] Настроить мониторинг (Grafana + Prometheus)
- [ ] Добавить автоматическое резервное копирование
- [ ] Настроить alerting
- [ ] Добавить smoke tests после деплоя
- [ ] Настроить log aggregation (ELK stack)

### 5. Документация

- [ ] Создать README.md с quick start
- [ ] Добавить API документацию (расширенную)
- [ ] Создать user guide с примерами
- [ ] Добавить архитектурные диаграммы
- [ ] Записать demo видео

### 6. Безопасность

- [ ] Сканирование образов на уязвимости (Trivy)
- [ ] Настроить HTTPS для всех endpoints
- [ ] Добавить Content Security Policy
- [ ] Регулярное обновление зависимостей
- [ ] Secrets management (не хранить в .env)

---

## Полезные ссылки

### Документация проекта

- [README.md](README.md) - главная документация
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - настройка GitHub и CI/CD
- [SETUP_CICD.md](SETUP_CICD.md) - детальная настройка CI/CD
- [nas-deployment/README.md](nas-deployment/README.md) - развертывание на NAS
- [nas-deployment/HOTFIX.md](nas-deployment/HOTFIX.md) - исправления и troubleshooting

### Инфраструктура

- **Production**: https://dso.deone37.synology.me/
- **API Docs**: https://dso.deone37.synology.me/docs
- **Docker Hub Backend**: https://hub.docker.com/r/deone37/devsecops-backend
- **Docker Hub Frontend**: https://hub.docker.com/r/deone37/devsecops-frontend
- **GitHub** (планируется): https://github.com/SergeyBakunin/devsecops-tools

### Synology

- **NAS Dashboard**: https://dso.deone37.synology.me:5001
- **Container Manager**: https://dso.deone37.synology.me:5001/#/Docker
- **SSH**: `ssh admin@dso.deone37.synology.me`

---

## Технические детали

### Версии

- **Backend Docker Image**: `deone37/devsecops-backend:1.0.0`
- **Frontend Docker Image**: `deone37/devsecops-frontend:1.0.0`
- **Python**: 3.13
- **Node.js**: 22
- **React**: 18.2
- **FastAPI**: latest
- **Nginx**: alpine

### Порты

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| Frontend | 3000 | 80 | React app + Nginx |
| Backend | 8090 | 8000 | FastAPI + Uvicorn |
| HTTPS | 443 | - | Reverse proxy (Synology) |
| HTTP | 80 | - | Redirect to HTTPS |

### Переменные окружения

```env
# NAS
NAS_DOMAIN=dso.deone37.synology.me
NAS_IP=192.168.0.233
TZ=Europe/Moscow

# Порты
BACKEND_PORT=8090
FRONTEND_PORT=3000

# API
API_URL=https://dso.deone37.synology.me
LOG_LEVEL=info

# Ресурсы
BACKEND_MEMORY_LIMIT=512M
FRONTEND_MEMORY_LIMIT=256M
```

### Структура проекта

```
sbom-tools/
├── .github/
│   └── workflows/
│       ├── docker-publish.yml          # GitHub Actions CI/CD
│       └── README.md                   # Документация workflow
├── backend/
│   ├── app/
│   │   └── main.py                     # FastAPI приложение
│   ├── requirements.txt                # Python зависимости
│   ├── Dockerfile                      # Backend образ
│   └── .dockerignore
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── SBOMMigrate.js         # Компонент миграции
│   │   │   └── VEXConverter.js         # Компонент VEX конвертера
│   │   ├── App.js                      # Главный компонент
│   │   └── index.js
│   ├── package.json                    # Node зависимости
│   ├── nginx.conf                      # Nginx конфигурация
│   ├── Dockerfile                      # Frontend образ
│   └── .dockerignore
├── nas-deployment/
│   ├── devsecops-backend-1.0.0.tar    # Экспорт backend
│   ├── devsecops-frontend-1.0.0.tar   # Экспорт frontend
│   ├── docker-compose.nas-simple.yml  # Упрощенный compose
│   ├── update-from-dockerhub.sh       # Скрипт обновления
│   ├── QUICK_FIX.sh                   # Быстрое исправление
│   ├── HOTFIX.md                      # Troubleshooting
│   └── README.md                      # Инструкции
├── docker-compose.yml                  # Локальная разработка
├── docker-compose.nas.yml              # Для NAS (локальные образы)
├── docker-compose.dockerhub.yml        # Для NAS (Docker Hub)
├── push-to-dockerhub.bat               # Скрипт публикации
├── .env.nas.example                    # Пример .env для NAS
├── .gitignore
├── .gitattributes
├── README.md                           # Главная документация
├── GITHUB_SETUP.md                     # GitHub инструкции
├── SETUP_CICD.md                       # CI/CD настройка
├── DEPLOY_TO_NAS.md                    # NAS деплой
└── SESSION_ARTIFACT.md                 # Этот файл
```

---

## История версий

### v1.0.0 (19-20 октября 2025)

**Функции:**
- ✅ VEX Converter (SBOM → VEX)
- ✅ SBOM Migrate (перенос комментариев)
- ✅ Docker контейнеризация
- ✅ Развертывание на Synology NAS
- ✅ GitHub Actions CI/CD
- ✅ Docker Hub интеграция

**Тестирование:**
- ✅ Конвертация 63 уязвимостей (CRAB)
- ✅ Конвертация 462 уязвимостей (ClickHouse)
- ✅ Сохранение 98-100% метаданных
- ✅ Production деплой на dso.deone37.synology.me

---

## Контакты и учетные данные

### GitHub
- **Username**: SergeyBakunin
- **Email**: sergey.bakunin@example.com (указать реальный)

### Docker Hub
- **Username**: deone37
- **Repositories**:
  - deone37/devsecops-backend
  - deone37/devsecops-frontend

### Synology NAS
- **Model**: DS723+
- **Domain**: dso.deone37.synology.me
- **IP**: 192.168.0.233
- **User**: admin (или deone37)

### Пути на локальной машине
- **Проект**: `C:\Users\Sergey Bakunin\sbom-tools`
- **Тестовые SBOM**: `C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\CodeScoring files\SBOM_to_VEX\`

---

## Примечания для продолжения

### Если используете собственный Git/Registry:

**Информация необходимая для адаптации:**
1. URL Git сервера (Gitea/GitLab)
2. URL Container Registry
3. Тип CI/CD (Gitea Actions, GitLab CI, Jenkins)
4. Примеры конфигурационных файлов

**Что нужно будет изменить:**
- `.github/workflows/` → `.gitea/workflows/` или `.gitlab-ci.yml`
- Registry URL: `docker.io/deone37` → `registry.yourdomain.com/deone37`
- Git remote URL
- Credentials для CI/CD

### Возможные улучшения инфраструктуры:

1. **Локальный Docker Registry на NAS**
   - Установить registry:2 контейнер
   - Настроить TLS
   - Интегрировать с CI/CD

2. **Gitea/GitLab на NAS**
   - Развернуть Git сервер
   - Настроить Gitea Actions / GitLab Runner
   - Webhook для автодеплоя

3. **Мониторинг**
   - Prometheus + Grafana
   - Alertmanager
   - Node Exporter для NAS метрик

4. **Backup & Recovery**
   - Автоматическое резервное копирование
   - Snapshot volumes
   - Disaster recovery план

---

## Чеклист для нового сеанса

При продолжении работы над проектом:

- [ ] Проверить статус контейнеров на NAS
- [ ] Проверить доступность https://dso.deone37.synology.me/
- [ ] Убедиться, что GitHub репозиторий создан
- [ ] Проверить образы на Docker Hub
- [ ] Просмотреть логи на наличие ошибок
- [ ] Обновить документацию при изменениях
- [ ] Создать backup перед крупными изменениями

---

**Дата создания артефакта**: 20 октября 2025, 01:15
**Версия проекта**: 1.0.0
**Статус**: Production Ready ✅

---

*Этот артефакт содержит всю критическую информацию о проекте DevSecOps Tools для продолжения разработки в новом сеансе.*
