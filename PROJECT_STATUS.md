# DevSecOps Tools - Статус проекта

**Дата последнего обновления:** 18 октября 2025
**Версия:** 1.0.0

---

## 📋 Описание проекта

**DevSecOps Tools** - веб-приложение для работы с SBOM и управления уязвимостями. Предоставляет набор инструментов для DevSecOps инженеров.

### Технологический стек:
- **Backend:** Python 3.13, FastAPI, Pandas, Uvicorn
- **Frontend:** React 18.2.0, Axios
- **Форматы данных:** CSV, XLSX

---

## 🎯 Реализованные функции

### ✅ Vulnerability Comments Transfer (ранее SBOM Migrate)
**Статус:** Полностью реализовано и работает

**Назначение:** Перенос комментариев между выгрузками уязвимостей

**Как работает:**
1. Пользователь загружает старую выгрузку с комментариями (CSV/XLSX)
2. Пользователь загружает новую выгрузку без комментариев (CSV/XLSX)
3. Система автоматически сопоставляет записи по **CVE ID** + **Project**
4. Переносит комментарии из старой выгрузки в новую
5. Результат можно скачать в CSV или XLSX формате

**API Endpoints:**
- `POST /api/sbom-migrate` - предварительный просмотр результата
- `POST /api/sbom-migrate/export` - экспорт файла с результатом

**Файлы:**
- Backend: `backend/app/main.py` - функции `migrate_comments()`, `sbom_migrate()`, `sbom_migrate_export()`
- Frontend: `frontend/src/components/SBOMMigrate.js`

**Алгоритм сопоставления:**
```python
# Создаётся словарь: (CVE ID, Project) -> Comment
# Комментарии переносятся по точному совпадению ключа
```

---

## 🚧 Запланированные функции (Coming Soon)

### 1. GitLeaks Scanner
**Иконка:** 🔐
**Описание:** Сканирование репозиториев на наличие утечек секретов и учётных данных
**Статус:** Заглушка создана, реализация планируется

### 2. VEX Converter
**Иконка:** 📋
**Описание:** Преобразование отчётов об уязвимостях в формат VEX (Vulnerability Exploitability eXchange)
**Статус:** Заглушка создана, реализация планируется

### 3. Vulnerability Analyzer
**Иконка:** 🔍
**Описание:** Анализ уязвимостей и генерация отчётов
**Статус:** Заглушка создана

### 4. Dependency Checker
**Иконка:** 📦
**Описание:** Проверка зависимостей на наличие известных уязвимостей
**Статус:** Заглушка создана

### 5. SBOM Validator
**Иконка:** ✅
**Описание:** Валидация SBOM файлов по стандартам CycloneDX и SPDX
**Статус:** Заглушка создана

---

## 📁 Структура проекта

```
C:\Users\Sergey Bakunin\sbom-tools/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI приложение
│   ├── Dockerfile               # Docker для backend
│   └── requirements.txt          # Python зависимости
├── frontend/
│   ├── public/
│   │   └── index.html           # HTML точка входа
│   ├── src/
│   │   ├── components/
│   │   │   └── SBOMMigrate.js   # Компонент переноса комментариев
│   │   ├── App.js               # Главный компонент React
│   │   ├── App.css              # Стили приложения
│   │   ├── index.js             # React точка входа
│   │   └── index.css            # Глобальные стили
│   └── package.json             # Node.js зависимости
├── start-backend.bat            # Скрипт запуска backend (Windows)
├── start-frontend.bat           # Скрипт запуска frontend (Windows)
├── README-RUN.md                # Инструкция по запуску
└── PROJECT_STATUS.md            # Этот файл
```

---

## 🚀 Инструкция по запуску

### Требования:
- Python 3.11+ (установлен: Python 3.13.3)
- Node.js 18+ (установлен: Node.js v22.20.0)
- npm 10+ (установлен: npm 10.9.3)

### Установка зависимостей (ОДИН РАЗ):

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

### Запуск приложения:

#### Вариант 1: Использование bat-файлов (Windows)

1. Откройте **первый терминал** и запустите:
   ```bash
   start-backend.bat
   ```

2. Откройте **второй терминал** и запустите:
   ```bash
   start-frontend.bat
   ```

#### Вариант 2: Ручной запуск

**Терминал 1 - Backend:**
```bash
cd backend/app
py main.py
```
Backend будет доступен на: http://localhost:8000

**Терминал 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend откроется автоматически на: http://localhost:3000

### Проверка работы:

1. Откройте браузер: http://localhost:3000
2. Вы увидите главную страницу **DevSecOps Tools**
3. Нажмите на карточку **"Vulnerability Comments Transfer"**
4. Загрузите два файла и протестируйте функционал

---

## 🔧 API Документация

FastAPI автоматически генерирует интерактивную документацию:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### Основные эндпоинты:

#### GET /
Проверка работы API
```json
{
  "message": "DevSecOps Tools API",
  "version": "1.0.0"
}
```

#### POST /api/sbom-migrate
Просмотр результата миграции без скачивания

**Параметры:**
- `source_file` (file): Старая выгрузка с комментариями
- `target_file` (file): Новая выгрузка

**Ответ:**
```json
{
  "status": "success",
  "source_rows": 150,
  "target_rows": 200,
  "result_rows": 200,
  "columns": ["CVE ID", "Project", "Comment", ...]
}
```

#### POST /api/sbom-migrate/export
Экспорт результата миграции

**Параметры:**
- `source_file` (file): Старая выгрузка с комментариями
- `target_file` (file): Новая выгрузка
- `export_format` (string): "csv" или "xlsx" (по умолчанию "xlsx")

**Ответ:** Бинарный файл (CSV или XLSX)

---

## 🎨 Дизайн и UI

### Цветовая схема:
- **Основной градиент:** #667eea → #764ba2 (фиолетовый)
- **Успех:** #28a745 → #20c997 (зелёный)
- **Ошибка:** #f44336 (красный)
- **Фон:** Градиент от синего до фиолетового

### Компоненты:
- **Карточки инструментов** - с тенями и hover-эффектами
- **Кнопки** - с градиентами и анимацией
- **Поля загрузки файлов** - с пунктирной рамкой
- **Сообщения** - с цветной левой границей

---

## 📝 История изменений

### 18.10.2025 - v1.0.0
- ✅ Переименовано приложение: "SBOM Tools" → "DevSecOps Tools"
- ✅ Переименована функция: "SBOM Migrate" → "Vulnerability Comments Transfer"
- ✅ Добавлены CSS стили для компонента переноса комментариев
- ✅ Добавлены новые инструменты в Coming Soon:
  - GitLeaks Scanner
  - VEX Converter
- ✅ Установлены все зависимости для Python 3.13
- ✅ Создана документация и инструкции по запуску
- ✅ Реализован полностью рабочий функционал переноса комментариев

### Ранее:
- ✅ Создан backend на FastAPI
- ✅ Создан frontend на React
- ✅ Реализован алгоритм миграции комментариев
- ✅ Добавлена поддержка CSV и XLSX форматов
- ✅ Настроен CORS для взаимодействия frontend-backend

---

## 🐛 Известные проблемы

### Решённые:
- ✅ Pandas 2.1.4 несовместим с Python 3.13 → Обновлено до pandas>=2.2.0
- ✅ Отсутствовал компонент SBOMMigrate.js → Создан
- ✅ Отсутствовали CSS стили → Добавлены

### Текущие:
- Нет

---

## 🔐 Безопасность

- CORS настроен на `allow_origins=["*"]` - **В продакшене нужно ограничить!**
- Нет аутентификации - планируется добавить
- Загружаемые файлы не проверяются на вредоносность

**TODO для продакшена:**
- [ ] Добавить аутентификацию (JWT)
- [ ] Ограничить CORS конкретными доменами
- [ ] Добавить валидацию загружаемых файлов
- [ ] Добавить rate limiting
- [ ] Настроить HTTPS

---

## 📚 Полезные команды

### Backend:
```bash
# Установка зависимостей
py -m pip install -r requirements.txt

# Запуск сервера
py main.py

# Обновление pip
py -m pip install --upgrade pip

# Просмотр установленных пакетов
py -m pip list
```

### Frontend:
```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm start

# Сборка для продакшена
npm run build

# Аудит безопасности
npm audit
```

### Docker (если нужно):
```bash
# Сборка backend образа
cd backend
docker build -t devsecops-tools-backend .

# Запуск backend контейнера
docker run -p 8000:8000 devsecops-tools-backend
```

---

## 💡 Идеи для будущего развития

1. **Аутентификация и авторизация**
   - JWT токены
   - OAuth 2.0 интеграция

2. **База данных**
   - Хранение истории миграций
   - Сохранение пользовательских настроек

3. **Расширенная аналитика**
   - Статистика по уязвимостям
   - Графики и дашборды

4. **Интеграции**
   - GitHub Actions
   - GitLab CI/CD
   - Jira

5. **Дополнительные форматы**
   - JSON
   - XML
   - CycloneDX
   - SPDX

6. **API для автоматизации**
   - Batch обработка
   - Webhook'и
   - REST API для CI/CD

---

## 👥 Контакты

**Разработчик:** Sergey Bakunin
**Путь к проекту:** `C:\Users\Sergey Bakunin\sbom-tools`

---

## 📄 Лицензия

Не указана (TODO)

---

**Последнее обновление:** 18.10.2025
**Автор документа:** Claude (AI Assistant) + Sergey Bakunin
