# DevSecOps Tools

> Набор инструментов для работы с SBOM и управления уязвимостями

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Status](https://img.shields.io/badge/status-active-success)

---

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# Одна команда для запуска всего приложения
docker-compose up -d
```

Откройте http://localhost:3000

📖 **Подробнее:** [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

### Вариант 2: Локальный запуск

```bash
# Терминал 1 - Backend
cd backend/app
py main.py

# Терминал 2 - Frontend
cd frontend
npm start
```

Откройте http://localhost:3000

📖 **Подробнее:** [QUICK_START.md](QUICK_START.md)

---

## ✨ Основные возможности

### ✅ Работает сейчас:

#### 🔄 Vulnerability Comments Transfer
Автоматический перенос комментариев между выгрузками уязвимостей:
- ✅ Поддержка CSV и XLSX форматов
- ✅ Сопоставление по CVE ID + Project
- ✅ Экспорт результата в CSV/XLSX
- ✅ Красивый веб-интерфейс

#### 📋 VEX Converter
Конвертация CycloneDX SBOM в формат VEX:
- ✅ Поддержка CycloneDX v1.6 (JSON)
- ✅ Сохранение всех уязвимостей и метаданных
- ✅ Экспорт в VEX документ (JSON)
- ✅ Автоматический анализ и статистика
- ✅ Веб-интерфейс и REST API

### 🚧 В разработке (Coming Soon):

- 🔐 **GitLeaks Scanner** - сканирование репозиториев на утечки секретов
- 🔍 **Vulnerability Analyzer** - анализ уязвимостей
- 📦 **Dependency Checker** - проверка зависимостей
- ✅ **SBOM Validator** - валидация SBOM файлов

---

## 🛠️ Технологии

**Backend:**
- Python 3.13
- FastAPI
- Pandas
- Uvicorn

**Frontend:**
- React 18.2
- Axios
- CSS3

---

## 📚 Документация

### Для пользователей:
- 📘 [Быстрый старт](QUICK_START.md) - запуск за 3 минуты
- 📗 [Руководство по запуску](README-RUN.md) - подробная инструкция
- 📙 [Статус проекта](PROJECT_STATUS.md) - текущее состояние и планы

### Для разработчиков:
- 💻 [Технические заметки](TECHNICAL_NOTES.md) - архитектура и решения
- 📝 [Changelog](CHANGELOG.md) - история изменений
- 🔧 [API документация](http://localhost:8000/docs) - Swagger UI (после запуска)

---

## 📦 Установка

### Требования:
- Python 3.11+ (рекомендуется 3.13)
- Node.js 18+
- npm 10+

### Установка зависимостей:

**Backend:**
```bash
cd backend
py -m pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## 🎯 Использование

### Vulnerability Comments Transfer

1. Запустите приложение (см. [Быстрый старт](#-быстрый-старт))
2. Откройте http://localhost:3000
3. Нажмите **"Vulnerability Comments Transfer"**
4. Загрузите:
   - **Старую выгрузку** (с комментариями) - CSV или XLSX
   - **Новую выгрузку** (без комментариев) - CSV или XLSX
5. Выберите формат экспорта (CSV или XLSX)
6. Нажмите **"Проверить миграцию"** для предпросмотра
7. Нажмите **"Экспортировать"** для скачивания результата

**Формат файлов:**
```csv
CVE ID,Project,Severity,Comment
CVE-2024-1234,MyProject,High,False positive
CVE-2024-5678,MyProject,Medium,Need to update
```

### VEX Converter

1. Запустите приложение (см. [Быстрый старт](#-быстрый-старт))
2. Откройте http://localhost:3000
3. Нажмите **"VEX Converter"**
4. Загрузите **SBOM файл** в формате CycloneDX v1.6 (JSON)
5. Нажмите **"Анализировать SBOM"** для просмотра статистики
6. Нажмите **"Конвертировать в VEX"** для создания и скачивания VEX документа

**Что такое VEX?**
VEX (Vulnerability Exploitability eXchange) - стандарт для обмена информацией о применимости уязвимостей к конкретным продуктам.

**Подробная документация:** [VEX_CONVERTER_README.md](VEX_CONVERTER_README.md)

---

## 🏗️ Структура проекта

```
sbom-tools/
├── backend/                    # Backend (FastAPI)
│   ├── app/
│   │   └── main.py            # Основное приложение
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── SBOMMigrate.js # Компонент переноса комментариев
│   │   │   └── VEXConverter.js # Компонент VEX конвертера
│   │   ├── App.js             # Главный компонент
│   │   ├── App.css            # Стили
│   │   └── index.js
│   ├── public/
│   └── package.json
├── docs/                       # Документация
│   ├── PROJECT_STATUS.md
│   ├── TECHNICAL_NOTES.md
│   ├── QUICK_START.md
│   └── CHANGELOG.md
├── start-backend.bat          # Скрипт запуска backend
├── start-frontend.bat         # Скрипт запуска frontend
└── README.md                  # Этот файл
```

---

## 🔌 API

### Основные endpoints:

#### `GET /`
Проверка работы API
```json
{
  "message": "DevSecOps Tools API",
  "version": "1.0.0"
}
```

#### `POST /api/sbom-migrate`
Предварительный просмотр миграции

**Параметры:**
- `source_file` - старая выгрузка (CSV/XLSX)
- `target_file` - новая выгрузка (CSV/XLSX)

**Ответ:**
```json
{
  "status": "success",
  "source_rows": 150,
  "target_rows": 200,
  "result_rows": 200,
  "columns": ["CVE ID", "Project", "Comment"]
}
```

#### `POST /api/sbom-migrate/export`
Экспорт результата

**Параметры:**
- `source_file` - старая выгрузка
- `target_file` - новая выгрузка
- `export_format` - "csv" или "xlsx"

**Ответ:** Файл для скачивания

#### `POST /api/sbom-to-vex`
Анализ SBOM и конвертация в VEX

**Параметры:**
- `sbom_file` - SBOM файл в формате CycloneDX v1.6 (JSON)

**Ответ:**
```json
{
  "status": "success",
  "sbom_vulnerabilities": 63,
  "vex_vulnerabilities": 63,
  "sbom_components": 294,
  "sbom_format": "CycloneDX",
  "sbom_version": "1.6",
  "vex_serial_number": "urn:uuid:...",
  "conversion_timestamp": "2025-10-18T13:08:11.976761Z"
}
```

#### `POST /api/sbom-to-vex/export`
Конвертация и экспорт VEX документа

**Параметры:**
- `sbom_file` - SBOM файл в формате CycloneDX v1.6 (JSON)

**Ответ:** VEX документ (JSON файл)

**Подробная документация API:** [VEX_CONVERTER_README.md](VEX_CONVERTER_README.md)

---

## 🧪 Тестирование

### Backend тесты:
```bash
cd backend
pytest
```

### Frontend тесты:
```bash
cd frontend
npm test
```

*(Тесты в разработке)*

---

## 🐳 Docker

### Быстрый запуск через Docker Compose (рекомендуется):

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

**Что запускается:**
- ✅ Backend (FastAPI) на порту 8000
- ✅ Frontend (React + Nginx) на порту 3000
- ✅ Автоматическая сеть между сервисами
- ✅ Health checks для мониторинга

### Через VS Code Docker Extension:

1. Откройте `docker-compose.yml`
2. Щёлкните правой кнопкой → **"Compose Up"**
3. Готово! Контейнеры запущены

### Ручная сборка образов:

**Backend:**
```bash
cd backend
docker build -t devsecops-tools-backend:1.0.0 .
docker run -d -p 8000:8000 devsecops-tools-backend:1.0.0
```

**Frontend:**
```bash
cd frontend
docker build -t devsecops-tools-frontend:1.0.0 .
docker run -d -p 3000:80 devsecops-tools-frontend:1.0.0
```

📖 **Подробная документация:** [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

---

## 🤝 Участие в разработке

Проект находится в активной разработке. Планируемые улучшения:

- [ ] Unit и integration тесты
- [ ] Аутентификация и авторизация
- [ ] База данных для истории операций
- [ ] Реализация остальных инструментов
- [ ] CI/CD pipeline
- [ ] Docker Compose для запуска

---

## 📊 Производительность

**Текущие возможности:**
- Обработка файлов до 100,000 строк
- Поддержка файлов до 50 MB
- Среднее время обработки: ~2-5 секунд

**Планируемые улучшения:**
- Batch обработка больших файлов
- Асинхронная обработка
- Кэширование результатов

---

## 🔒 Безопасность

**Текущее состояние:**
- ⚠️ Нет аутентификации
- ⚠️ CORS открыт для всех доменов
- ⚠️ Нет ограничения размера файлов

**В продакшене необходимо:**
- Настроить CORS на конкретные домены
- Добавить аутентификацию (JWT/OAuth)
- Ограничить размер загружаемых файлов
- Добавить rate limiting
- Использовать HTTPS

См. [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md#-безопасность-security-checklist) для деталей.

---

## 🐛 Известные проблемы

Нет критических проблем.

Сообщить о проблеме: [GitHub Issues](https://github.com/username/devsecops-tools/issues)

---

## 📝 Changelog

См. [CHANGELOG.md](CHANGELOG.md) для полной истории изменений.

---

## 📄 Лицензия

Не указана (TODO)

---

## 👤 Автор

**Sergey Bakunin**

- 📧 Email: your.email@example.com
- 💼 GitHub: [@username](https://github.com/username)

---

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- React за мощный UI фреймворк
- Pandas за обработку данных
- Claude AI за помощь в разработке

---

## 📞 Контакты и поддержка

- **Документация:** См. папку `/docs`
- **Вопросы:** Создайте Issue на GitHub
- **Email:** your.email@example.com

---

**Версия:** 1.0.0
**Последнее обновление:** 18 октября 2025
**Статус:** Active Development

---

Made with ❤️ using FastAPI and React
