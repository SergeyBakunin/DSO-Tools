# Настройка CI/CD для DevSecOps Tools

Пошаговая инструкция для настройки автоматической сборки и публикации Docker образов.

## Шаг 1: Создайте Docker Hub репозитории

1. Зайдите на https://hub.docker.com/
2. Нажмите **Create Repository**
3. Создайте два репозитория:
   - `devsecops-backend` (Public или Private)
   - `devsecops-frontend` (Public или Private)

## Шаг 2: Получите Docker Hub Access Token

1. Откройте https://hub.docker.com/settings/security
2. Нажмите **New Access Token**
3. Заполните:
   - **Description**: `github-actions-devsecops`
   - **Access permissions**: **Read, Write, Delete**
4. Нажмите **Generate**
5. **СКОПИРУЙТЕ ТОКЕН** - он больше не покажется!

## Шаг 3: Создайте GitHub репозиторий

### Вариант A: Через GitHub Desktop (проще)

1. Откройте GitHub Desktop
2. File → Add Local Repository
3. Выберите папку `C:\Users\Sergey Bakunin\sbom-tools`
4. Publish repository → выберите имя `devsecops-tools`
5. Опционально: сделайте Private

### Вариант B: Через командную строку

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# Если еще не инициализирован git
git init
git add .
git commit -m "Initial commit: DevSecOps Tools v1.0.0"

# Создайте репозиторий на GitHub через веб-интерфейс
# Затем добавьте remote и запушьте
git remote add origin https://github.com/YOUR_USERNAME/devsecops-tools.git
git branch -M main
git push -u origin main
```

## Шаг 4: Добавьте секреты в GitHub

1. Откройте ваш GitHub репозиторий
2. Перейдите: **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**

Создайте два секрета:

### Секрет 1: DOCKERHUB_USERNAME

- **Name**: `DOCKERHUB_USERNAME`
- **Secret**: ваш Docker Hub username (например: `sergeybak` или `deone37`)

### Секрет 2: DOCKERHUB_TOKEN

- **Name**: `DOCKERHUB_TOKEN`
- **Secret**: токен из Шага 2

## Шаг 5: Запустите первую сборку

### Автоматически (при push)

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"
git add .
git commit -m "Add GitHub Actions CI/CD workflow"
git push
```

GitHub Actions автоматически запустится и соберет образы!

### Вручную

1. GitHub → Actions → "Build and Push Docker Images"
2. Нажмите **Run workflow** → **Run workflow**

## Шаг 6: Проверьте сборку

1. GitHub → Actions → посмотрите логи workflow
2. Дождитесь зеленой галочки ✅
3. Проверьте Docker Hub - там появятся образы

## Шаг 7: Обновите docker-compose на NAS

Создайте файл для использования Docker Hub образов:

```bash
# На NAS создайте docker-compose.dockerhub.yml
cd /volume1/docker/devsecops/project
sudo nano docker-compose.dockerhub.yml
```

Содержимое:
```yaml
version: '3.8'

services:
  backend:
    image: YOUR_DOCKERHUB_USERNAME/devsecops-backend:latest
    container_name: devsecops-backend
    ports:
      - "8090:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=info
    restart: unless-stopped
    mem_limit: 512M
    mem_reservation: 256M
    networks:
      - devsecops-network

  frontend:
    image: YOUR_DOCKERHUB_USERNAME/devsecops-frontend:latest
    container_name: devsecops-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=https://dso.deone37.synology.me
    depends_on:
      - backend
    restart: unless-stopped
    mem_limit: 256M
    mem_reservation: 128M
    networks:
      - devsecops-network

networks:
  devsecops-network:
    driver: bridge
```

## Шаг 8: Обновление приложения в будущем

### Когда вы вносите изменения в код:

```bash
# 1. Внесите изменения в код
# 2. Закоммитьте
git add .
git commit -m "Feature: добавлена новая функция"
git push

# 3. Создайте версионный тег (опционально)
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# GitHub Actions автоматически соберет и опубликует образы
```

### На NAS обновите контейнеры:

**Через Container Manager (GUI):**
1. Образ → Обновить → проверит Docker Hub
2. Проект → devsecops → Действие → Сборка

**Через SSH:**
```bash
cd /volume1/docker/devsecops/project
sudo docker-compose -f docker-compose.dockerhub.yml pull
sudo docker-compose -f docker-compose.dockerhub.yml up -d
```

## Схема обновления

```
Изменения в коде
    ↓
Git push в GitHub
    ↓
GitHub Actions запускается
    ↓
Сборка Docker образов
    ↓
Публикация в Docker Hub
    ↓
Обновление на NAS (вручную или автоматически)
```

## Автоматическое обновление на NAS (опционально)

Можно настроить Webhook от Docker Hub к NAS для автоматического обновления при публикации новой версии.

## Проверка версий

```bash
# На NAS проверьте текущую версию
sudo docker images | grep devsecops

# На Docker Hub посмотрите доступные теги
https://hub.docker.com/r/YOUR_USERNAME/devsecops-backend/tags
```

## Откат к предыдущей версии

```bash
# Укажите конкретную версию в docker-compose
image: username/devsecops-backend:1.0.0  # вместо :latest

# Перезапустите
sudo docker-compose -f docker-compose.dockerhub.yml up -d
```

## Мониторинг сборок

- GitHub → Actions → посмотрите статус всех сборок
- Настройте email уведомления при ошибках сборки

## Troubleshooting

### Ошибка: invalid tag format
- Проверьте формат: `username/repository:tag`
- Username должен быть в нижнем регистре

### Ошибка: unauthorized
- Проверьте секреты DOCKERHUB_USERNAME и DOCKERHUB_TOKEN
- Убедитесь, что токен активен

### Образы не появляются на Docker Hub
- Проверьте логи GitHub Actions
- Убедитесь, что workflow завершился успешно (зеленая галочка)
