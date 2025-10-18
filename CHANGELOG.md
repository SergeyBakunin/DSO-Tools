# Changelog

Все важные изменения в проекте DevSecOps Tools документированы в этом файле.

---

## [1.0.0] - 2025-10-18

### 🎉 Первый релиз

#### ✨ Добавлено
- **Переименование проекта**: "SBOM Tools" → "DevSecOps Tools"
- **Переименование основной функции**: "SBOM Migrate" → "Vulnerability Comments Transfer"
- **Компонент SBOMMigrate.js**: Полностью функциональный React компонент для переноса комментариев
- **CSS стили**: Добавлено 230+ строк стилей для красивого UI
- **Новые инструменты в Coming Soon**:
  - 🔐 GitLeaks Scanner - сканирование репозиториев на утечки секретов
  - 📋 VEX Converter - преобразование в формат VEX
- **Документация**:
  - PROJECT_STATUS.md - статус проекта
  - TECHNICAL_NOTES.md - технические заметки
  - QUICK_START.md - быстрый старт
  - CHANGELOG.md - этот файл

#### 🔧 Исправлено
- **Совместимость с Python 3.13**: Обновлена версия pandas с 2.1.4 до >=2.2.0
- **Отсутствующий компонент**: Создан компонент SBOMMigrate.js
- **Отсутствие стилей**: Добавлены CSS стили для всех компонентов

#### 📝 Изменено
- **Backend**:
  - `backend/requirements.txt`: pandas==2.1.4 → pandas>=2.2.0
  - `backend/app/main.py`: FastAPI title изменён на "DevSecOps Tools"
- **Frontend**:
  - `frontend/src/App.js`: Обновлён список инструментов, изменён заголовок
  - `frontend/src/App.css`: Добавлены стили для tool-container и компонентов
  - `frontend/src/components/SBOMMigrate.js`: Создан с нуля
  - `frontend/public/index.html`: Обновлён title и description
  - `frontend/package.json`: Изменено имя пакета на devsecops-tools-frontend

#### 📦 Зависимости
- **Backend установлено**:
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - python-multipart==0.0.6
  - pandas==2.3.3 (обновлено)
  - openpyxl==3.1.2
  - xlsxwriter==3.1.9
- **Frontend установлено**:
  - react==18.2.0
  - react-dom==18.2.0
  - axios==1.6.5
  - react-scripts==5.0.1

---

## [0.9.0] - До 2025-10-18 (Предыдущая работа)

### ✨ Добавлено
- **Backend на FastAPI**:
  - Функция `migrate_comments()` - основной алгоритм переноса комментариев
  - API endpoints: `/api/sbom-migrate` и `/api/sbom-migrate/export`
  - Поддержка CSV и XLSX форматов
  - CORS middleware для работы с frontend
- **Frontend на React**:
  - Главная страница с карточками инструментов
  - Базовая структура App.js
  - Стили для карточек инструментов
- **Инструменты в Coming Soon**:
  - Vulnerability Analyzer
  - Dependency Checker
  - SBOM Validator
- **Docker конфигурация** для backend
- **Bat-скрипты** для запуска на Windows

---

## Планируемые изменения

### [1.1.0] - В разработке

#### Планируется добавить:
- [ ] Unit тесты для backend
- [ ] Component тесты для frontend
- [ ] Drag-and-drop для загрузки файлов
- [ ] Превью данных перед миграцией
- [ ] Прогресс-бар для загрузки файлов
- [ ] Улучшенная обработка ошибок
- [ ] Логирование операций

### [2.0.0] - Будущее

#### Новые функции:
- [ ] GitLeaks Scanner - полная реализация
- [ ] VEX Converter - полная реализация
- [ ] База данных (PostgreSQL/SQLite)
- [ ] Аутентификация и авторизация (JWT)
- [ ] API токены для CI/CD интеграции
- [ ] Webhook'и для уведомлений
- [ ] Расширенная аналитика и дашборды

---

## Формат версионирования

Проект использует [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.x.x) - несовместимые изменения API
- **MINOR** (x.1.x) - новая функциональность, обратно совместимая
- **PATCH** (x.x.1) - обратно совместимые исправления

---

## Типы изменений

- **✨ Добавлено** - новая функциональность
- **🔧 Исправлено** - исправление багов
- **📝 Изменено** - изменения в существующей функциональности
- **🗑️ Удалено** - удалённая функциональность
- **🔒 Безопасность** - уязвимости и исправления безопасности
- **📦 Зависимости** - обновления зависимостей
- **🚀 Производительность** - улучшения производительности

---

**Формат Changelog основан на [Keep a Changelog](https://keepachangelog.com/)**
