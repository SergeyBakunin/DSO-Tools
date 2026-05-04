# Быстрый старт — DevSecOps Tools v1.6.8

---

## Вариант 1: Docker (рекомендуется)

### Требования
- Docker Engine или Docker Desktop

### Запуск

```bash
# Скачать образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.8
docker pull sergeybakunin/devsecops-tools-frontend:1.6.8

# Запустить (из папки docker/)
cd docker
docker compose up -d --no-build
```

### Проверка

```bash
docker ps
# devsecops-backend  — healthy
# devsecops-frontend — running
```

Открыть в браузере: **http://localhost:3000**

### Остановка

```bash
docker compose down
```

---

## Вариант 2: Локальный запуск

### Требования
- Python 3.11+ (рекомендуется 3.13)
- Node.js 18+, npm 10+

### Зависимости

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Запуск

```bash
# Терминал 1 — Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Терминал 2 — Frontend
cd frontend
npm start
```

Открыть: **http://localhost:3000** | Swagger UI: **http://localhost:8000/docs**

---

## Инструменты

### Выгрузка уязвимостей

1. Откройте http://localhost:3000 — откроется раздел "Выгрузка уязвимостей"
2. Введите название проекта и версию, выберите уровни Severity
3. Нажмите **"Получить уязвимости"**
4. Выберите нужные проекты чекбоксами (колонка "В SBOM" подсвечивает зелёным проекты из SBOM)
5. При необходимости подтвердите дату скана (если ближайший скан дальше 3 дней от SBOM)
6. Скачайте результат: CSV, VEX JSON или архив SBOM из Artifactory

### Триаж VEX

1. Выберите **"Триаж VEX"** в боковом меню
2. Загрузите CycloneDX VEX JSON файл
3. Редактируйте State / Justification / Response / Detail
4. Настройте фильтр по Severity для экспорта
5. Нажмите **"Скачать триажированный VEX"**

### Конвертер VEX

1. Выберите **"Конвертер VEX"** в боковом меню
2. Загрузите SBOM (JSON) или XLSX с уязвимостями
3. **"Анализировать SBOM"** — статистика
4. **"Конвертировать в VEX"** — скачать VEX JSON
5. **"Скачать XLS с уязвимостями"** — Excel для команд разработки

### Валидатор VEX

1. Выберите **"Валидатор VEX"** в боковом меню
2. Загрузите VEX JSON документ
3. Нажмите **"Валидировать VEX"**

### SBOM Merger

1. Выберите **"SBOM Merger"** в боковом меню
2. Загрузите ZIP архив с папками, содержащими SBOM JSON файлы
3. Нажмите **"Анализировать"** → **"Объединить и скачать"**

---

## Частые проблемы

### Порт занят

```bash
# Linux
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
```

### Backend не отвечает

```bash
docker logs devsecops-backend
docker compose restart backend
```

### exec format error

Образ собран под неправильную архитектуру. Пересоберите с явным указанием платформы:

```bash
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.8 ./backend
```

---

**Версия:** 1.6.8 | **Обновлено:** 04 мая 2026
