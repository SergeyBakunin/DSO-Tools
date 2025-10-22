# ИСПРАВЛЕНИЕ: NanoCPUs error на Synology

## Проблема
```
Error response from daemon: NanoCPUs can not be set, as your kernel does not support CPU CFS scheduler or the cgroup is not mounted
```

## Причина
Docker Compose v3.8 на Synology не поддерживает секцию `deploy.resources` - это функция Docker Swarm mode.

## Решение

### Вариант 1: Скопировать исправленный файл (рекомендуется)

Обновленный `docker-compose.nas.yml` уже находится в этой папке.

```bash
# На NAS выполните:
cd /volume1/docker/devsecops/nas-deployment

# Скопируйте исправленный файл
sudo cp docker-compose.nas.yml /volume1/docker/devsecops/project/docker-compose.nas.yml

# Перезапустите контейнеры
cd /volume1/docker/devsecops/project
sudo docker-compose -f docker-compose.nas.yml down
sudo docker-compose -f docker-compose.nas.yml up -d
```

### Вариант 2: Через Container Manager UI

1. **Удалите старый проект:**
   - Container Manager → Проект → devsecops → Действие → Удалить

2. **Загрузите новый docker-compose.nas.yml:**
   - Скопируйте обновленный файл из `nas-deployment/` в `project/`

3. **Создайте проект заново:**
   - Container Manager → Проект → Создать
   - Имя: devsecops
   - Путь: `/volume1/docker/devsecops/project`
   - Файл: `docker-compose.nas.yml`

## Что изменилось?

### БЫЛО (не работает на Synology):
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

### СТАЛО (работает на Synology):
```yaml
cpus: 1.0
mem_limit: 512M
mem_reservation: 256M
```

## Проверка

После перезапуска:

```bash
# Проверьте статус
sudo docker ps

# Должны быть запущены оба контейнера:
# - devsecops-backend (port 8090)
# - devsecops-frontend (port 3000)

# Проверьте логи
sudo docker logs devsecops-backend
sudo docker logs devsecops-frontend
```

## Доступ к приложению

После успешного запуска откройте:
```
https://dso.deone37.synology.me/
```

Reverse Proxy должен перенаправлять трафик на backend (порт 8090).

## Если всё равно не работает

### Упрощенная версия БЕЗ лимитов ресурсов:

```bash
# Отредактируйте docker-compose.nas.yml
sudo nano /volume1/docker/devsecops/project/docker-compose.nas.yml

# Удалите строки с:
# cpus: ...
# mem_limit: ...
# mem_reservation: ...

# Сохраните (Ctrl+O, Enter, Ctrl+X)

# Перезапустите
sudo docker-compose -f docker-compose.nas.yml down
sudo docker-compose -f docker-compose.nas.yml up -d
```

## Альтернатива: Runtime flags

Вместо docker-compose можно запустить контейнеры вручную с флагами:

```bash
# Backend
sudo docker run -d \
  --name devsecops-backend \
  --cpus="1.0" \
  --memory="512m" \
  --memory-reservation="256m" \
  -p 8090:8000 \
  -e PYTHONUNBUFFERED=1 \
  -e LOG_LEVEL=info \
  --restart unless-stopped \
  devsecops-tools-backend:1.0.0

# Frontend
sudo docker run -d \
  --name devsecops-frontend \
  --cpus="0.5" \
  --memory="256m" \
  --memory-reservation="128m" \
  -p 3000:80 \
  -e REACT_APP_API_URL=https://dso.deone37.synology.me \
  --restart unless-stopped \
  devsecops-tools-frontend:1.0.0
```

Но лучше использовать docker-compose!
