# Развертывание на Synology DS723+ NAS

## Что в этой папке?

- `devsecops-backend-1.0.0.tar` - образ backend (94 MB)
- `devsecops-frontend-1.0.0.tar` - образ frontend (22 MB)
- `docker-compose.nas.yml` - конфигурация для NAS
- `.env` - переменные окружения (СОЗДАЙТЕ ИЗ .env.nas.example)

## Быстрая установка (5 минут)

### Шаг 1: Скопируйте файлы на NAS

Скопируйте всю папку `nas-deployment` на NAS в:
```
/volume1/docker/devsecops/
```

Должна получиться структура:
```
/volume1/docker/devsecops/
├── project/
│   ├── .env
│   └── docker-compose.nas.yml
├── backend-data/
├── backend-logs/
└── nas-deployment/           ← Эта папка
    ├── devsecops-backend-1.0.0.tar
    ├── devsecops-frontend-1.0.0.tar
    ├── docker-compose.nas.yml
    └── .env
```

### Шаг 2: Подключитесь к NAS по SSH

```bash
ssh admin@dso.deone37.synology.me
```

### Шаг 3: Импортируйте образы Docker

```bash
cd /volume1/docker/devsecops/nas-deployment

# Импорт backend
docker load -i devsecops-backend-1.0.0.tar

# Импорт frontend
docker load -i devsecops-frontend-1.0.0.tar

# Проверка
docker images | grep devsecops
```

Вы должны увидеть:
```
devsecops-tools-backend    1.0.0     1eab67b98a11   428MB
devsecops-tools-frontend   1.0.0     e449498569ff   80.8MB
```

### Шаг 4: Создайте .env файл

```bash
# Скопируйте из примера (если еще не создан в project/)
cp .env /volume1/docker/devsecops/project/.env

# Или отредактируйте существующий
nano /volume1/docker/devsecops/project/.env
```

Проверьте, что переменные правильные:
```env
NAS_DOMAIN=dso.deone37.synology.me
BACKEND_PORT=8090
API_URL=https://dso.deone37.synology.me
```

### Шаг 5: Запустите через Container Manager

**Вариант A: Через UI**
1. Откройте Container Manager
2. Перейдите в "Проект" → "Создать"
3. Имя проекта: `devsecops`
4. Путь: `/volume1/docker/devsecops/project`
5. Выберите файл `docker-compose.nas.yml`
6. Нажмите "Готово"

**Вариант B: Через SSH**
```bash
cd /volume1/docker/devsecops/project
docker-compose -f docker-compose.nas.yml up -d
```

### Шаг 6: Проверка

1. **Проверьте статус контейнеров:**
   ```bash
   docker ps
   ```

2. **Проверьте логи:**
   ```bash
   docker logs devsecops-backend
   docker logs devsecops-frontend
   ```

3. **Откройте в браузере:**
   ```
   https://dso.deone37.synology.me/
   ```

## Настройка Reverse Proxy (если еще не настроен)

Container Manager → Контрольная панель → Портал входа → Advanced → Reverse Proxy

Создайте правило:
- **Описание**: DevSecOps Tools
- **Источник**:
  - Протокол: HTTPS
  - Имя хоста: dso.deone37.synology.me
  - Порт: 443
  - HSTS: Включить
- **Назначение**:
  - Протокол: HTTP
  - Имя хоста: localhost
  - Порт: 8090

## Устранение неполадок

### Контейнеры не запускаются
```bash
# Проверьте логи
docker-compose -f docker-compose.nas.yml logs

# Пересоздайте контейнеры
docker-compose -f docker-compose.nas.yml down
docker-compose -f docker-compose.nas.yml up -d
```

### Не работает API
1. Проверьте, что backend доступен:
   ```bash
   curl http://localhost:8090/
   ```

2. Проверьте reverse proxy в настройках Synology

3. Проверьте переменную `API_URL` в `.env`

### Высокая нагрузка на NAS
Уменьшите лимиты ресурсов в `docker-compose.nas.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'    # было 1.0
      memory: 256M   # было 512M
```

## Обновление до новой версии

1. Получите новые tar файлы образов
2. Импортируйте их:
   ```bash
   docker load -i devsecops-backend-NEW_VERSION.tar
   docker load -i devsecops-frontend-NEW_VERSION.tar
   ```
3. Обновите версию в `docker-compose.nas.yml`
4. Перезапустите:
   ```bash
   docker-compose -f docker-compose.nas.yml down
   docker-compose -f docker-compose.nas.yml up -d
   ```

## Удаление старых образов

После успешного обновления:
```bash
# Посмотрите список образов
docker images

# Удалите старую версию
docker rmi devsecops-tools-backend:OLD_VERSION
docker rmi devsecops-tools-frontend:OLD_VERSION

# Очистите неиспользуемые данные
docker system prune -a
```
