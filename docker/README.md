# Docker Deployment - DevSecOps Tools

Полное руководство по развертыванию DevSecOps Tools с использованием Docker.

---

## 🎯 Быстрый старт

```bash
# Перейдите в директорию docker
cd docker

# Запустите приложение
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

Откройте в браузере: **http://localhost:3000**

---

## 📦 Созданные образы

После сборки у вас будут следующие Docker образы:

| Образ | Версия | Размер | Описание |
|-------|--------|--------|----------|
| `devsecops-tools-backend` | 1.3.0 | ~428MB | FastAPI backend с Python 3.13 |
| `devsecops-tools-frontend` | 1.3.0 | ~81MB | React frontend с Nginx |

### Проверка образов

```bash
docker images | grep devsecops-tools
```

---

## 🚀 Команды Docker Compose

### Запуск приложения

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Запуск с просмотром логов
docker-compose up

# Пересоздать и запустить контейнеры
docker-compose up -d --force-recreate
```

### Остановка приложения

```bash
# Остановить контейнеры (данные сохраняются)
docker-compose stop

# Остановить и удалить контейнеры
docker-compose down

# Остановить и удалить контейнеры + образы
docker-compose down --rmi all
```

### Пересборка образов

```bash
# Пересобрать все образы
docker-compose build

# Пересобрать без кэша
docker-compose build --no-cache

# Пересобрать конкретный сервис
docker-compose build backend
docker-compose build frontend
```

### Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Последние 100 строк логов
docker-compose logs --tail=100 -f
```

### Проверка статуса

```bash
# Список запущенных контейнеров
docker-compose ps

# Детальная информация
docker-compose ps -a

# Использование ресурсов
docker stats devsecops-backend devsecops-frontend
```

---

## 🔧 Конфигурация

### Структура файлов

```
docker/
├── docker-compose.yml    # Основная конфигурация
├── .env.example          # Пример переменных окружения
└── README.md            # Этот файл
```

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Доступные переменные:

```env
# Порты
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Сеть
NETWORK_NAME=devsecops-network

# Версии образов
BACKEND_IMAGE_TAG=1.3.0
FRONTEND_IMAGE_TAG=1.3.0
```

### Изменение портов

Отредактируйте `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Внешний:Внутренний

  frontend:
    ports:
      - "80:80"      # Внешний:Внутренний
```

---

## 🏗️ Сборка образов вручную

### Backend

```bash
cd ../backend
docker build -t devsecops-tools-backend:1.3.0 .
```

### Frontend

```bash
cd ../frontend
docker build -t devsecops-tools-frontend:1.3.0 .
```

---

## 🔍 Отладка

### Вход в контейнер

```bash
# Backend
docker exec -it devsecops-backend /bin/bash

# Frontend
docker exec -it devsecops-frontend /bin/sh
```

### Проверка здоровья сервисов

```bash
# Backend health check
curl http://localhost:8000/

# Frontend health check
curl http://localhost:3000/health
```

### Просмотр сетевых настроек

```bash
# Список сетей Docker
docker network ls

# Подробная информация о сети
docker network inspect devsecops-network
```

### Проверка volumes (если используются)

```bash
# Список volumes
docker volume ls

# Подробная информация
docker volume inspect devsecops-backend-data
```

---

## 📊 Мониторинг

### Health Checks

Docker Compose автоматически проверяет здоровье сервисов:

**Backend:**
- Интервал: 30s
- Timeout: 10s
- Retries: 3
- Проверка: `http://localhost:8000/`

**Frontend:**
- Интервал: 30s
- Timeout: 10s
- Retries: 3
- Проверка: `http://localhost/health`

### Зависимости сервисов

Frontend ждёт, пока backend будет здоров:

```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy
```

---

## 🔒 Безопасность

### Текущая конфигурация

- Backend работает от непривилегированного пользователя `appuser`
- CORS открыт для всех доменов (только для разработки!)
- Порты открыты на localhost

### Рекомендации для production

1. **Настройте CORS**
   ```python
   # В backend/app/main.py
   allow_origins=["https://yourdomain.com"]
   ```

2. **Используйте HTTPS**
   - Настройте Nginx с SSL-сертификатами
   - Используйте Let's Encrypt или свой сертификат

3. **Ограничьте доступ**
   - Используйте firewall
   - Настройте reverse proxy (Nginx/Traefik)

4. **Обновляйте образы**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 🐛 Решение проблем

### Порт уже занят

**Проблема:**
```
Error: bind: address already in use
```

**Решение:**
```bash
# Проверьте, что использует порт
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Остановите процесс или измените порт в docker-compose.yml
```

### Контейнер постоянно перезапускается

**Проблема:**
Контейнер в статусе "Restarting"

**Решение:**
```bash
# Проверьте логи
docker-compose logs backend

# Проверьте health check
docker inspect devsecops-backend | grep -A 20 Health
```

### Не загружается frontend

**Проблема:**
Браузер показывает "Cannot connect"

**Решение:**
```bash
# Проверьте, что контейнеры запущены
docker-compose ps

# Проверьте, что Nginx работает
docker exec devsecops-frontend nginx -t

# Перезапустите frontend
docker-compose restart frontend
```

### Ошибки сборки

**Проблема:**
Ошибка при `docker-compose build`

**Решение:**
```bash
# Очистите кэш Docker
docker system prune -a

# Пересоберите без кэша
docker-compose build --no-cache

# Проверьте Dockerfile
cat ../backend/Dockerfile
cat ../frontend/Dockerfile
```

---

## 📈 Оптимизация

### Уменьшение размера образов

Образы уже оптимизированы:
- ✅ Multi-stage build для frontend
- ✅ Python 3.13-slim для backend
- ✅ Nginx Alpine для frontend
- ✅ --no-cache-dir для pip

### Кэширование

Docker автоматически кэширует слои:
```bash
# Первая сборка: ~2-3 минуты
docker-compose build

# Повторная сборка: ~10-30 секунд
docker-compose build
```

---

## 🔄 Обновление

### Обновление кода

```bash
# 1. Остановите контейнеры
docker-compose down

# 2. Обновите код (git pull или изменения)
git pull

# 3. Пересоберите образы
docker-compose build

# 4. Запустите с новыми образами
docker-compose up -d
```

### Обновление зависимостей

**Backend:**
```bash
# Обновите requirements.txt
cd ../backend
pip freeze > requirements.txt

# Пересоберите образ
cd ../docker
docker-compose build backend
```

**Frontend:**
```bash
# Обновите package.json
cd ../frontend
npm update

# Пересоберите образ
cd ../docker
docker-compose build frontend
```

---

## 🌐 Развертывание в production

### На сервере

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/username/sbom-tools.git
cd sbom-tools/docker

# 2. Соберите образы
docker-compose build

# 3. Запустите в production режиме
docker-compose up -d

# 4. Настройте автозапуск
# Добавьте в systemd или используйте restart: always
```

### На Synology NAS

См. подробное руководство: [../instructions/NAS_DEPLOYMENT_GUIDE.md](../instructions/NAS_DEPLOYMENT_GUIDE.md)

### С Docker Hub

```bash
# 1. Загрузите образы с Docker Hub
docker-compose -f docker-compose.dockerhub.yml pull

# 2. Запустите
docker-compose -f docker-compose.dockerhub.yml up -d
```

---

## 📞 Поддержка

**Проблемы с Docker?**
- Проверьте логи: `docker-compose logs -f`
- Проверьте health checks: `docker-compose ps`
- Проверьте сеть: `docker network inspect devsecops-network`

**Дополнительная информация:**
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Основной README](../README.md)

---

**Версия:** 1.3.0
**Последнее обновление:** 5 ноября 2025
**Docker Compose версия:** 3.8
