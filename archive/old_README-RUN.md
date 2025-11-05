# SBOM Tools - Инструкция по запуску

## Требования

- Python 3.11+ (у вас установлен Python 3.13.3)
- Node.js 18+ (у вас установлен Node.js v22.20.0)
- npm 10+ (у вас установлен npm 10.9.3)

## Установка зависимостей

### Backend (один раз)
```bash
cd backend
py -m pip install -r requirements.txt
```

### Frontend (один раз)
```bash
cd frontend
npm install
```

## Запуск приложения

### Вариант 1: Использование bat-файлов (Windows)

1. Откройте **два** окна командной строки или терминала

2. В первом окне запустите backend:
   ```
   start-backend.bat
   ```

3. Во втором окне запустите frontend:
   ```
   start-frontend.bat
   ```

### Вариант 2: Ручной запуск

#### Терминал 1 - Backend
```bash
cd backend/app
py main.py
```
Backend будет доступен на: http://localhost:8000

#### Терминал 2 - Frontend
```bash
cd frontend
npm start
```
Frontend откроется автоматически на: http://localhost:3000

## Проверка работы

1. Откройте браузер и перейдите на http://localhost:3000
2. Вы увидите интерфейс SBOM Tools с карточками инструментов
3. Используйте инструмент "SBOM Migrate" для переноса комментариев между файлами

## API Документация

FastAPI автоматически генерирует документацию:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Остановка приложения

Нажмите `Ctrl+C` в каждом окне терминала для остановки серверов.

## Возможные проблемы

### Порт 8000 или 3000 занят
Если порт занят, измените его в конфигурации:
- Backend: в файле `backend/app/main.py` измените строку `uvicorn.run(app, host="0.0.0.0", port=8000)`
- Frontend: создайте файл `.env` в папке `frontend` с содержимым `PORT=3001`

### Ошибки при установке pandas
Pandas требует компилятора C++. Если установка не удаётся:
```bash
py -m pip install --upgrade pip
py -m pip install pandas --only-binary=:all:
```
