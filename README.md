# DevSecOps Tools

> Набор инструментов для работы с SBOM и управления уязвимостями

![Version](https://img.shields.io/badge/version-1.3.0-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Status](https://img.shields.io/badge/status-active-success)

---

## 🚀 Быстрый старт

### Самый простой способ (Windows):

```cmd
START.bat
```

Откройте http://localhost:3000

### Вариант 1: Docker (рекомендуется)

```bash
cd docker
docker-compose up -d
```

Откройте http://localhost:3000

### Вариант 2: Локальный запуск

```bash
# Терминал 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Терминал 2 - Frontend
cd frontend
npm start
```

Откройте http://localhost:3000

📖 **Подробнее:** [QUICK_START.md](QUICK_START.md) | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## ✨ Основные возможности

### ✅ Работает сейчас:

#### 🔄 Vulnerability Comments Transfer
Автоматический перенос комментариев и VEX-полей между выгрузками уязвимостей:
- ✅ Поддержка CSV и XLSX форматов
- ✅ Сопоставление по CVE ID + Project
- ✅ Перенос комментариев и VEX-полей (State, Justification, Response, Detail)
- ✅ Экспорт результата в CSV/XLSX
- ✅ Детальная статистика миграции
- ✅ Красивый веб-интерфейс

#### 📋 Конвертер VEX
Конвертация CycloneDX SBOM или XLSX в формат VEX:
- ✅ Поддержка CycloneDX v1.6 (JSON)
- ✅ Поддержка XLSX с уязвимостями
- ✅ Фильтрация по проектам
- ✅ Массовый экспорт в ZIP
- ✅ Опциональные поля продукта
- ✅ Сохранение всех уязвимостей и метаданных
- ✅ Автоматический анализ и статистика
- ✅ Веб-интерфейс и REST API

#### ✅ Валидатор VEX
Валидация VEX документов согласно стандарту CycloneDX 1.6:
- ✅ Проверка структуры документа
- ✅ Валидация обязательных полей
- ✅ Проверка VEX analysis (state, justification, response)
- ✅ Соответствие допустимым значениям
- ✅ Детальные отчеты об ошибках и предупреждениях
- ✅ Статистика по статусам и обоснованиям

#### 🔀 SBOM Merger
Объединение нескольких SBOM файлов в один для каждого проекта:
- ✅ Загрузка ZIP архива с папками SBOM файлов
- ✅ Автоматическое объединение нескольких файлов в один
- ✅ Копирование одиночных файлов
- ✅ Дедупликация компонентов и уязвимостей
- ✅ Детальная статистика по каждой папке
- ✅ Скачивание результата в ZIP архиве

### 🚧 В разработке (Coming Soon):

- 🔐 **GitLeaks Scanner** - сканирование репозиториев на утечки секретов

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
- 📗 [Конвертер VEX](instructions/VEX_CONVERTER_README.md) - подробное руководство
- 🔧 [API документация](http://localhost:8000/docs) - Swagger UI (после запуска)

### Для разработчиков:
- 💻 [Технические заметки](instructions/TECHNICAL_NOTES.md) - архитектура и решения
- 📝 [Changelog](instructions/CHANGELOG.md) - история изменений
- 📙 [Статус проекта](instructions/PROJECT_STATUS.md) - текущее состояние и планы

### Дополнительно:
- 🐳 [Docker Guide](instructions/DOCKER_GUIDE.md) - работа с Docker
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md) - полное руководство по развертыванию

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

### Конвертер VEX

1. Запустите приложение (см. [Быстрый старт](#-быстрый-старт))
2. Откройте http://localhost:3000
3. Нажмите **"Конвертер VEX"**
4. Загрузите файл:
   - **SBOM** в формате CycloneDX v1.6 (JSON)
   - **XLSX** с уязвимостями (CodeScoring, NBSS, и т.д.)
5. Для XLSX:
   - Выберите проект или "Все проекты"
   - Опционально укажите название и версию продукта
6. Нажмите **"Анализировать"** для просмотра статистики
7. Нажмите **"Конвертировать в VEX"** для создания и скачивания VEX документа

**Что такое VEX?**
VEX (Vulnerability Exploitability eXchange) - стандарт для обмена информацией о применимости уязвимостей к конкретным продуктам.

**Подробная документация:** [VEX_CONVERTER_README.md](instructions/VEX_CONVERTER_README.md)

### Валидатор VEX

1. Запустите приложение (см. [Быстрый старт](#-быстрый-старт))
2. Откройте http://localhost:3000
3. Нажмите **"Валидатор VEX"**
4. Загрузите **VEX документ** в формате CycloneDX JSON
5. Нажмите **"Валидировать VEX"**
6. Просмотрите результаты валидации:
   - ✅ Информация о документе (serial number, версия, продукт)
   - ✅ Статистика по уязвимостям и статусам
   - ❌ Список ошибок (если есть)
   - ⚠️ Предупреждения (если есть)

**Что проверяет валидатор:**
- Структура документа (bomFormat, specVersion, serialNumber, version)
- Обязательные поля метаданных (timestamp, tools, component)
- VEX analysis для каждой уязвимости (state, justification, response)
- Соответствие допустимым значениям CycloneDX 1.6

### SBOM Merger

1. Запустите приложение (см. [Быстрый старт](#-быстрый-старт))
2. Откройте http://localhost:3000
3. Нажмите **"SBOM Merger"**
4. Загрузите ZIP архив с папками, содержащими SBOM файлы (JSON)
5. Нажмите **"Анализировать"** для просмотра статистики
6. Нажмите **"Объединить и скачать"** для получения ZIP архива с результатами

**Структура входного архива:**
```
archive.zip/
  ├── project-1/
  │   ├── backend-sbom.json
  │   └── frontend-sbom.json
  ├── project-2/
  │   └── app-sbom.json
  └── project-3/
      ├── api-sbom.json
      ├── web-sbom.json
      └── mobile-sbom.json
```

**Результат:**
```
merged_sboms.zip/
  ├── project-1/
  │   └── project-1.json  (объединённый SBOM)
  ├── project-2/
  │   └── project-2.json  (скопирован как есть)
  └── project-3/
      └── project-3.json  (объединённый SBOM)
```

**Что делает merger:**
- Объединяет несколько SBOM файлов в один для каждой папки
- Дедуплицирует компоненты и уязвимости
- Сохраняет все метаданные и зависимости
- Копирует файл если в папке только один SBOM

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
│   │   │   ├── VEXConverter.js # Компонент VEX конвертера
│   │   │   └── VEXValidator.js # Компонент VEX валидатора
│   │   ├── App.js             # Главный компонент
│   │   ├── App.css            # Стили
│   │   └── index.js
│   ├── public/
│   └── package.json
├── docker/                     # Docker конфигурация
│   └── docker-compose.yml     # Docker Compose файл
├── instructions/               # Документация
│   ├── CHANGELOG.md
│   ├── DOCKER_GUIDE.md
│   ├── TECHNICAL_NOTES.md
│   ├── PROJECT_STATUS.md
│   └── VEX_CONVERTER_README.md
├── START.bat                   # Быстрый запуск (Windows)
├── STOP.bat                    # Остановка приложения
├── DEPLOYMENT_GUIDE.md         # Руководство по развертыванию
├── QUICK_START.md              # Быстрый старт
└── README.md                   # Этот файл
```

---

## 🔌 API

### Основные endpoints:

#### `GET /`
Проверка работы API
```json
{
  "message": "DevSecOps Tools API",
  "version": "1.3.0"
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

#### `POST /api/xlsx-to-vex`
Анализ XLSX и конвертация в VEX

**Параметры:**
- `xlsx_file` - XLSX файл с уязвимостями
- `project_filter` - (опционально) Имя проекта для фильтрации
- `product_name` - (опционально) Название продукта
- `product_version` - (опционально) Версия продукта

**Ответ:**
```json
{
  "status": "success",
  "source_filename": "vulnerabilities.xlsx",
  "source_rows": 150,
  "vex_vulnerabilities": 150,
  "product_name": "My Application",
  "product_version": "1.0.0",
  "statistics": { ... }
}
```

#### `POST /api/xlsx-to-vex/export`
Экспорт XLSX в VEX документ

**Параметры:**
- `xlsx_file` - XLSX файл с уязвимостями
- `project_filter` - (опционально) Имя проекта
- `product_name` - (опционально) Название продукта
- `product_version` - (опционально) Версия продукта

**Ответ:** VEX документ (JSON файл)

#### `POST /api/xlsx-to-vex/export-all-projects`
Массовый экспорт всех проектов в ZIP

**Параметры:**
- `xlsx_file` - XLSX файл с уязвимостями
- `product_version` - (опционально) Версия продукта

**Ответ:** ZIP архив с VEX файлами для каждого проекта

#### `POST /api/sbom-merge`
Анализ ZIP архива с SBOM файлами

**Параметры:**
- `zip_file` - ZIP архив с папками, содержащими SBOM JSON файлы

**Ответ:**
```json
{
  "status": "success",
  "statistics": {
    "total_folders": 3,
    "processed_folders": 3,
    "skipped_folders": 0,
    "failed_folders": 0,
    "folder_details": [
      {
        "folder": "project-1",
        "status": "merged",
        "files_count": 2,
        "output": "project-1.json"
      }
    ]
  },
  "timestamp": "2025-11-26T..."
}
```

#### `POST /api/sbom-merge/export`
Объединение SBOM и скачивание ZIP архива

**Параметры:**
- `zip_file` - ZIP архив с папками, содержащими SBOM JSON файлы

**Ответ:** ZIP архив с объединёнными SBOM файлами

#### `POST /api/vex/validate`
Валидация VEX документа

**Параметры:**
- `vex_file` - VEX файл в формате CycloneDX JSON

**Ответ:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "info": {
    "filename": "vex_document.json",
    "serial_number": "urn:uuid:...",
    "version": 1,
    "product_name": "My Application",
    "vulnerabilities_count": 63,
    "has_vex_analysis": 63,
    "missing_vex_analysis": 0,
    "state_distribution": {
      "in_triage": 45,
      "not_affected": 18
    },
    "justification_distribution": {
      "code_not_reachable": 18
    }
  }
}
```

**Подробная документация API:** [VEX_CONVERTER_README.md](instructions/VEX_CONVERTER_README.md)

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
docker-compose -f docker/docker-compose.yml up -d

# Просмотр логов
docker-compose -f docker/docker-compose.yml logs -f

# Остановка
docker-compose -f docker/docker-compose.yml down
```

**Что запускается:**
- ✅ Backend (FastAPI) на порту 8000
- ✅ Frontend (React + Nginx) на порту 3000
- ✅ Автоматическая сеть между сервисами
- ✅ Health checks для мониторинга

### Через VS Code Docker Extension:

1. Откройте `docker/docker-compose.yml`
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

📖 **Подробная документация:** [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md)

---

## 🤝 Участие в разработке

Проект находится в активной разработке. Планируемые улучшения:

- [ ] Unit и integration тесты
- [ ] Аутентификация и авторизация
- [ ] Реализация GitLeaks Scanner
- [ ] CI/CD pipeline
- [ ] Поддержка других форматов SBOM

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

См. [TECHNICAL_NOTES.md](instructions/TECHNICAL_NOTES.md#-безопасность-security-checklist) для деталей.

---

## 🐛 Известные проблемы

Нет критических проблем.

Сообщить о проблеме: [GitHub Issues](https://github.com/SergeyBakunin/DSO-Tools/issues)

---

## 📝 Changelog

См. [CHANGELOG.md](instructions/CHANGELOG.md) для полной истории изменений.

---

## 📄 Лицензия

Не указана (TODO)

---

## 👤 Автор

**Sergey Bakunin**

- 💼 GitHub: [@SergeyBakunin](https://github.com/SergeyBakunin)

---

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- React за мощный UI фреймворк
- Pandas за обработку данных
- CycloneDX за стандарт VEX

---

## 🌐 Доступ из локальной сети

### Быстрая настройка:

1. **Откройте Firewall (PowerShell от администратора):**
   ```powershell
   New-NetFirewallRule -DisplayName "DevSecOps Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "DevSecOps Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

2. **Узнайте IP вашего ноутбука:**
   ```powershell
   ipconfig
   ```
   Найдите **IPv4 Address** (например: 192.168.1.100)

3. **Подключитесь с другого устройства:**
   ```
   http://192.168.1.100:3000
   ```

📖 **Подробное руководство:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📞 Контакты и поддержка

- **Документация:** [QUICK_START.md](QUICK_START.md) | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Инструкции:** См. папку `/instructions`
- **Автор:** Sergey Bakunin

---

**Версия:** 1.3.0
**Последнее обновление:** 26 ноября 2025
**Статус:** Active Development

---

Made with ❤️ using FastAPI and React
