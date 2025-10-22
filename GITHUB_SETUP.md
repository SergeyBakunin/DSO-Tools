# Настройка GitHub и CI/CD

Пошаговая инструкция для проекта **DevSecOps Tools**

- **GitHub**: SergeyBakunin
- **Docker Hub**: deone37

---

## Шаг 1: Первая публикация в Docker Hub (вручную)

### 1.1. Запустите скрипт push-to-dockerhub.bat

Двойной клик на файл `push-to-dockerhub.bat` в корне проекта.

Или вручную выполните команды:

```bash
# Логин
docker login

# Тегирование
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:1.0.0
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:latest
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:1.0.0
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:latest

# Push
docker push deone37/devsecops-backend:1.0.0
docker push deone37/devsecops-backend:latest
docker push deone37/devsecops-frontend:1.0.0
docker push deone37/devsecops-frontend:latest
```

### 1.2. Проверьте на Docker Hub

Откройте:
- https://hub.docker.com/r/deone37/devsecops-backend
- https://hub.docker.com/r/deone37/devsecops-frontend

Должны появиться образы с тегами `1.0.0` и `latest`.

---

## Шаг 2: Создайте GitHub репозиторий

### 2.1. Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Заполните:
   - **Repository name**: `devsecops-tools`
   - **Description**: `DevSecOps Tools - SBOM to VEX converter and vulnerability comment migration`
   - **Visibility**: Private (или Public, как хотите)
3. **НЕ** добавляйте README, .gitignore, license (они уже есть)
4. Нажмите **Create repository**

### 2.2. Подключите локальный репозиторий

В терминале выполните:

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# Проверьте текущий статус
git status

# Если git еще не инициализирован
git init

# Добавьте remote
git remote add origin https://github.com/SergeyBakunin/devsecops-tools.git

# Добавьте все файлы
git add .

# Создайте коммит
git commit -m "Initial commit: DevSecOps Tools v1.0.0

Features:
- SBOM to VEX converter (CycloneDX v1.6)
- Vulnerability comments migration
- Docker containerization
- NAS deployment support
- GitHub Actions CI/CD"

# Запушьте
git branch -M main
git push -u origin main
```

---

## Шаг 3: Настройте Docker Hub secrets в GitHub

### 3.1. Создайте Docker Hub Access Token

1. Откройте https://hub.docker.com/settings/security
2. Нажмите **New Access Token**
3. Заполните:
   - **Access Token Description**: `github-actions-devsecops-tools`
   - **Access permissions**: **Read, Write, Delete**
4. Нажмите **Generate**
5. **СКОПИРУЙТЕ ТОКЕН** (показывается только один раз!)

### 3.2. Добавьте секреты в GitHub

1. Откройте https://github.com/SergeyBakunin/devsecops-tools/settings/secrets/actions
2. Нажмите **New repository secret**

**Секрет 1:**
- Name: `DOCKERHUB_USERNAME`
- Secret: `deone37`

**Секрет 2:**
- Name: `DOCKERHUB_TOKEN`
- Secret: `<токен из шага 3.1>`

---

## Шаг 4: Проверьте GitHub Actions

### 4.1. Автоматический запуск

После push в main, GitHub Actions автоматически запустится.

Проверьте: https://github.com/SergeyBakunin/devsecops-tools/actions

### 4.2. Ручной запуск (если нужно)

1. Откройте https://github.com/SergeyBakunin/devsecops-tools/actions
2. Выберите workflow **"Build and Push Docker Images"**
3. Нажмите **Run workflow** → **Run workflow**

### 4.3. Дождитесь зеленой галочки ✅

Сборка занимает 5-10 минут.

---

## Шаг 5: Обновите NAS для использования Docker Hub

### 5.1. Скопируйте docker-compose.dockerhub.yml на NAS

```bash
# На вашем ПК в проекте уже есть этот файл
# Скопируйте его на NAS в:
# /volume1/docker/devsecops/project/docker-compose.dockerhub.yml
```

### 5.2. Переключитесь на Docker Hub образы

На NAS выполните:

```bash
cd /volume1/docker/devsecops/project

# Остановите текущие контейнеры
sudo docker-compose -f docker-compose.nas.yml down

# Скачайте образы с Docker Hub
sudo docker pull deone37/devsecops-backend:latest
sudo docker pull deone37/devsecops-frontend:latest

# Запустите с Docker Hub образами
sudo docker-compose -f docker-compose.dockerhub.yml up -d

# Проверьте
sudo docker ps
```

### 5.3. Или используйте скрипт

```bash
cd /volume1/docker/devsecops/nas-deployment
chmod +x update-from-dockerhub.sh
sudo ./update-from-dockerhub.sh
```

---

## Шаг 6: Workflow обновлений в будущем

### Внесение изменений

```bash
cd "C:\Users\Sergey Bakunin\sbom-tools"

# 1. Внесите изменения в код
# 2. Commit
git add .
git commit -m "Feature: добавлена новая функция"

# 3. Push в GitHub
git push

# GitHub Actions автоматически:
# - Соберет образы
# - Опубликует в Docker Hub с тегом :latest
```

### Создание версионного релиза

```bash
# Создайте тег
git tag -a v1.0.1 -m "Release v1.0.1: bug fixes and improvements"
git push origin v1.0.1

# GitHub Actions создаст образы с тегами:
# - deone37/devsecops-backend:1.0.1
# - deone37/devsecops-backend:1.0
# - deone37/devsecops-backend:1
# - deone37/devsecops-backend:latest
```

### Обновление на NAS

**Автоматически через Synology:**
1. Container Manager → Образ → Обновить
2. Проверит Docker Hub на наличие новых версий
3. Скачает новые образы
4. Проект → devsecops → Действие → Сборка

**Вручную через SSH:**
```bash
cd /volume1/docker/devsecops/nas-deployment
sudo ./update-from-dockerhub.sh
```

---

## Полная схема CI/CD

```
Изменения в коде (локально)
    ↓
Git commit & push → GitHub
    ↓
GitHub Actions запускается
    ↓
Сборка Docker образов
    ↓
Публикация в Docker Hub
    ↓
Synology проверяет обновления
    ↓
Обновление контейнеров на NAS
```

---

## Проверка статуса

### GitHub Actions
https://github.com/SergeyBakunin/devsecops-tools/actions

### Docker Hub
- https://hub.docker.com/r/deone37/devsecops-backend/tags
- https://hub.docker.com/r/deone37/devsecops-frontend/tags

### Приложение
https://dso.deone37.synology.me/

---

## Troubleshooting

### GitHub Actions не запускается
- Проверьте, что файл `.github/workflows/docker-publish.yml` закоммичен
- Проверьте секреты в Settings → Secrets

### Ошибка "unauthorized" в GitHub Actions
- Проверьте секреты DOCKERHUB_USERNAME и DOCKERHUB_TOKEN
- Убедитесь, что токен не истек

### Образы не обновляются на NAS
```bash
# Принудительно скачайте новые
sudo docker pull deone37/devsecops-backend:latest --no-cache
sudo docker pull deone37/devsecops-frontend:latest --no-cache
sudo docker-compose -f docker-compose.dockerhub.yml up -d --force-recreate
```

---

## Полезные ссылки

- **GitHub Repo**: https://github.com/SergeyBakunin/devsecops-tools
- **Docker Hub Backend**: https://hub.docker.com/r/deone37/devsecops-backend
- **Docker Hub Frontend**: https://hub.docker.com/r/deone37/devsecops-frontend
- **Production**: https://dso.deone37.synology.me/
