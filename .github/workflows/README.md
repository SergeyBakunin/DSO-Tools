# GitHub Actions CI/CD

Этот проект использует GitHub Actions для автоматической сборки и публикации Docker образов в Docker Hub.

## Как это работает

1. **При push в main/master** - собираются и публикуются образы с тегом `latest`
2. **При создании тега вида v1.0.0** - собираются образы с версионными тегами
3. **При pull request** - собираются образы для тестирования (без публикации)

## Настройка

### 1. Создайте Docker Hub Access Token

1. Зайдите на https://hub.docker.com/settings/security
2. Нажмите **New Access Token**
3. Имя: `github-actions`
4. Права: **Read, Write, Delete**
5. Скопируйте токен (он показывается только один раз!)

### 2. Добавьте секреты в GitHub

Откройте репозиторий → Settings → Secrets and variables → Actions → New repository secret

Создайте два секрета:

**DOCKERHUB_USERNAME**
```
ваш_username_на_dockerhub
```

**DOCKERHUB_TOKEN**
```
токен_созданный_в_шаге_1
```

### 3. Workflow запустится автоматически

После push в репозиторий, GitHub Actions:
- ✅ Соберет backend и frontend образы
- ✅ Запушит их в Docker Hub
- ✅ Добавит теги `latest` и версионные теги

## Использование версий

### Создание новой версии

```bash
# Создайте git tag с версией
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

Это создаст образы с тегами:
- `username/devsecops-backend:1.0.1`
- `username/devsecops-backend:1.0`
- `username/devsecops-backend:1`
- `username/devsecops-backend:latest`

### Обновление на NAS

После публикации новой версии на Docker Hub:

**Автоматически через Synology:**
1. Container Manager → Образ → Обновить (проверит Docker Hub)
2. Увидит новую версию → Скачает
3. Container Manager → Проект → Остановить → Запустить (с новыми образами)

**Вручную через SSH:**
```bash
cd /volume1/docker/devsecops/project
sudo docker-compose -f docker-compose.nas.yml pull
sudo docker-compose -f docker-compose.nas.yml up -d
```

## Структура тегов

| Push событие | Теги образов |
|--------------|--------------|
| Push в main | `latest`, `main` |
| Tag v1.2.3 | `1.2.3`, `1.2`, `1`, `latest` |
| Pull Request #42 | `pr-42` (не публикуется) |

## Просмотр логов сборки

GitHub → Actions → выберите workflow → посмотрите логи

## Локальная сборка и публикация

Если нужно собрать вручную:

```bash
# Сборка
docker build -t username/devsecops-backend:1.0.0 ./backend
docker build -t username/devsecops-frontend:1.0.0 ./frontend

# Тегирование latest
docker tag username/devsecops-backend:1.0.0 username/devsecops-backend:latest
docker tag username/devsecops-frontend:1.0.0 username/devsecops-frontend:latest

# Публикация
docker push username/devsecops-backend:1.0.0
docker push username/devsecops-backend:latest
docker push username/devsecops-frontend:1.0.0
docker push username/devsecops-frontend:latest
```
