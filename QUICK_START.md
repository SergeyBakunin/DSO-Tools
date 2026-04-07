# 🚀 Быстрый старт — DevSecOps Tools v1.6.5

---

## Вариант 1: Docker (рекомендуется) 🐳

### Требования:
- Docker Engine или Docker Desktop

### Запуск:

```bash
# Скачать образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.5
docker pull sergeybakunin/devsecops-tools-frontend:1.6.5

# Запустить (из папки с docker-compose.yml)
docker compose up -d --no-build
```

### Проверка:

```bash
docker ps
# Должны быть запущены: devsecops-backend (healthy), devsecops-frontend
```

### Открыть в браузере: **http://localhost:3000**

### Остановка:

```bash
docker compose down
```

---

## Вариант 2: Windows — START.bat 🪟

```cmd
START.bat
```

Скрипт проверит наличие Docker и запустит приложение. Браузер откроется автоматически.

Остановка: `STOP.bat`

---

## Вариант 3: Локальный запуск 💻

### Требования:
- Python 3.11+ (рекомендуется 3.13)
- Node.js 18+, npm 10+

### Шаг 1: Зависимости

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Шаг 2: Запуск

```bash
# Терминал 1 — Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Терминал 2 — Frontend
cd frontend
npm start
```

Открыть: **http://localhost:3000** | API: **http://localhost:8000/docs**

---

## 🎯 Первое использование

### 🔍 Выгрузка уязвимостей

1. Откройте http://localhost:3000
2. Нажмите **"Выгрузка уязвимостей"**
3. Введите название проекта и версию
4. Нажмите **"Запустить поиск"**
5. Скачайте результат в CSV или VEX JSON

### 🏷️ Триаж VEX

1. Нажмите **"Триаж VEX"**
2. Загрузите CycloneDX VEX JSON файл
3. Редактируйте State / Justification / Response / Detail для уязвимостей
4. Настройте фильтр по Severity для экспорта
5. Нажмите **"Скачать триажированный VEX"**

### 📋 Конвертер VEX

1. Нажмите **"Конвертер VEX"**
2. Загрузите SBOM (JSON) или XLSX с уязвимостями
3. **"Анализировать SBOM"** — просмотр статистики
4. **"Конвертировать в VEX"** — скачать VEX JSON
5. **"⬇ Скачать XLS с уязвимостями"** — Excel для команд разработки

### ✅ Валидатор VEX

1. Нажмите **"Валидатор VEX"**
2. Загрузите VEX JSON документ
3. Нажмите **"Валидировать VEX"**
4. Просмотрите ошибки и предупреждения

### 🔀 SBOM Merger

1. Нажмите **"SBOM Merger"**
2. Загрузите ZIP архив с папками, содержащими SBOM JSON файлы
3. Нажмите **"Анализировать"** → **"Объединить и скачать"**

---

## 🔧 Частые проблемы

### Порт уже занят

```bash
# Linux/Mac
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
```

### Backend не отвечает

```bash
# Проверить логи
docker logs devsecops-backend

# Перезапустить
docker compose restart backend
```

### Образ не запускается (`exec format error`)

Образ собран под неправильную архитектуру. Пересоберите:

```bash
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.5 ./backend
```

---

## 📚 Дополнительно

- [README.md](README.md) — полная документация
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — развёртывание на сервере
- [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md) — работа с Docker
- [VEX_CONVERTER_README.md](instructions/VEX_CONVERTER_README.md) — Конвертер VEX API
- **Swagger UI:** http://localhost:8000/docs

---

**Версия:** 1.6.5 | **Обновлено:** 07 апреля 2026
