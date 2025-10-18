# DevSecOps Tools - Быстрый старт

## 🚀 Запуск за 3 минуты

### 1️⃣ Откройте ДВА терминала

### 2️⃣ В первом терминале (Backend):
```bash
cd "C:\Users\Sergey Bakunin\sbom-tools\backend\app"
py main.py
```
✅ Должно появиться: `Uvicorn running on http://0.0.0.0:8000`

### 3️⃣ Во втором терминале (Frontend):
```bash
cd "C:\Users\Sergey Bakunin\sbom-tools\frontend"
npm start
```
✅ Браузер автоматически откроется на http://localhost:3000

---

## 📋 Быстрый тест

1. Откройте http://localhost:3000
2. Нажмите **"Vulnerability Comments Transfer"**
3. Загрузите два файла CSV/XLSX
4. Нажмите **"Проверить миграцию"** или **"Экспортировать"**

---

## 🛑 Остановка

Нажмите `Ctrl+C` в обоих терминалах

---

## 📚 Полная документация

- **Статус проекта:** [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **Технические заметки:** [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- **Инструкция по запуску:** [README-RUN.md](README-RUN.md)

---

## 🆘 Проблемы?

### Frontend не запускается?
```bash
cd frontend
npm install
npm start
```

### Backend не запускается?
```bash
cd backend
py -m pip install -r requirements.txt
cd app
py main.py
```

### API не отвечает?
- Проверьте, что backend запущен на http://localhost:8000
- Откройте http://localhost:8000/docs для проверки API

---

## ✅ Что уже работает:

- ✅ **Vulnerability Comments Transfer** - перенос комментариев между выгрузками уязвимостей
- ✅ Поддержка CSV и XLSX форматов
- ✅ Автоматическое сопоставление по CVE ID + Project
- ✅ Экспорт результата

## 🚧 В разработке (Coming Soon):

- 🔐 **GitLeaks Scanner** - сканирование репозиториев
- 📋 **VEX Converter** - преобразование в VEX формат
- 🔍 **Vulnerability Analyzer** - анализ уязвимостей
- 📦 **Dependency Checker** - проверка зависимостей
- ✅ **SBOM Validator** - валидация SBOM файлов

---

**Версия:** 1.0.0
**Дата:** 18.10.2025
