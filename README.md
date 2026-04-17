# DevSecOps Tools

> Набор инструментов для работы с SBOM и управления уязвимостями

![Version](https://img.shields.io/badge/version-1.6.6-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![Status](https://img.shields.io/badge/status-active-success)

---

## 🚀 Быстрый старт

### Через Docker (рекомендуется):

```bash
# Скачать образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.6
docker pull sergeybakunin/devsecops-tools-frontend:1.6.6

# Запустить
docker compose up -d --no-build
```

Открыть: **http://localhost:3000**

### Локально (Windows):

```cmd
START.bat
```

📖 Подробнее: [QUICK_START.md](QUICK_START.md) | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## ✨ Инструменты

### 🔍 Выгрузка уязвимостей
Поиск уязвимостей по проекту и версии через Artifactory и CodeScoring.

- Поиск SBOM в Artifactory по названию проекта и версии
- Получение истории сканов через CodeScoring API
- Детальный лог выполнения с возможностью скачать
- Экспорт результатов в **CSV** и **VEX JSON**

### 🏷️ Триаж VEX
Редактирование состояния уязвимостей в CycloneDX VEX файле.

- Загрузка VEX JSON (drag-and-drop или выбор файла)
- Редактирование `State`, `Justification`, `Response`, `Detail` для каждой уязвимости
- Массовое применение статуса к выбранным записям
- Сортировка по CVE/Компоненту/Severity/State
- Фильтр по Severity для скачиваемого файла
- Валидация обязательного поля Detail перед экспортом

### 📋 Конвертер VEX
Конвертация CycloneDX SBOM или XLSX в формат VEX.

- Поддержка **CycloneDX SBOM v1.6 (JSON)** и **XLSX** с уязвимостями
- Фильтрация по проектам, массовый экспорт в ZIP
- **Скачать XLS с уязвимостями** — Excel отчёт для команд разработки
  (CVE ID, Компонент, Версия, Severity, CVSS, CWE, Описание, State, Разметка)

### ✅ Валидатор VEX
Валидация VEX документов согласно стандарту CycloneDX 1.6.

- Проверка структуры, обязательных полей и метаданных
- Валидация `analysis` (state, justification, response) по допустимым значениям
- Статистика по статусам, детальный отчёт об ошибках и предупреждениях

### 🔀 SBOM Merger
Объединение нескольких SBOM файлов в один для каждого проекта из ZIP архива.

- Рекурсивное сканирование вложенных ZIP архивов
- Дедупликация компонентов и уязвимостей
- Статистика по каждой папке, результат в ZIP

---

## 🛠️ Технологии

| | Стек |
|---|---|
| **Backend** | Python 3.13, FastAPI, Pandas, openpyxl, uvicorn |
| **Frontend** | React 18.2, Axios, CSS3 |
| **Deploy** | Docker, Nginx (reverse proxy) |
| **Registry** | [DockerHub: sergeybakunin](https://hub.docker.com/u/sergeybakunin) |

---

## 🐳 Docker

### Запуск готовых образов:

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.6
docker pull sergeybakunin/devsecops-tools-frontend:1.6.6
docker compose up -d --no-build
```

### Сборка из исходников:

```bash
# amd64 для Linux серверов (buildx обязателен на ARM-хосте)
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.6 ./backend

docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.6 ./frontend
```

📖 Подробнее: [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md)

---

## 🌐 API

**Swagger UI:** http://localhost:8000/docs (после запуска)

### Основные endpoints:

| Endpoint | Описание |
|---|---|
| `POST /api/vulnerability-report/fetch` | Поиск уязвимостей через Artifactory + CodeScoring |
| `POST /api/vulnerability-report/export-csv` | Экспорт в CSV |
| `POST /api/vulnerability-report/export-vex` | Экспорт в VEX JSON |
| `POST /api/sbom-to-vex` | Анализ SBOM → статистика |
| `POST /api/sbom-to-vex/export` | SBOM → VEX JSON файл |
| `POST /api/sbom-to-xlsx` | SBOM/VEX → Excel с уязвимостями |
| `POST /api/xlsx-to-vex` | XLSX → VEX (анализ) |
| `POST /api/xlsx-to-vex/export` | XLSX → VEX JSON файл |
| `POST /api/xlsx-to-vex/export-all-projects` | XLSX → ZIP (все проекты) |
| `POST /api/xlsx-to-vex/projects` | Получить список проектов из XLSX |
| `POST /api/vex/validate` | Валидация VEX документа |
| `POST /api/sbom-merge` | Анализ ZIP с SBOM файлами |
| `POST /api/sbom-merge/export` | Объединение SBOM → ZIP |

---

## 🏗️ Структура проекта

```
sbom-tools/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI — все endpoints
│   │   └── vulnerability_report.py  # Модуль выгрузки уязвимостей
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VulnerabilityReport.js  # Выгрузка уязвимостей
│   │   │   ├── VexTriage.js            # Триаж VEX
│   │   │   ├── VEXConverter.js         # Конвертер VEX
│   │   │   ├── VEXValidator.js         # Валидатор VEX
│   │   │   └── SBOMMerger.js           # SBOM Merger
│   │   ├── App.js
│   │   └── App.css
│   ├── nginx.conf
│   └── Dockerfile
├── docker/
│   └── docker-compose.yml
├── instructions/
│   ├── CHANGELOG.md
│   ├── DOCKER_GUIDE.md
│   ├── PROJECT_STATUS.md
│   ├── TECHNICAL_NOTES.md
│   └── VEX_CONVERTER_README.md
├── .github/workflows/
│   └── docker-publish.yml
├── START.bat
├── STOP.bat
├── QUICK_START.md
├── DEPLOYMENT_GUIDE.md
└── README.md
```

---

## 📚 Документация

| Документ | Описание |
|---|---|
| [QUICK_START.md](QUICK_START.md) | Запуск за 3 минуты |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Развёртывание на сервере |
| [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md) | Работа с Docker |
| [VEX_CONVERTER_README.md](instructions/VEX_CONVERTER_README.md) | Конвертер VEX — API и примеры |
| [CHANGELOG.md](instructions/CHANGELOG.md) | История изменений |
| [PROJECT_STATUS.md](instructions/PROJECT_STATUS.md) | Статус и планы |

---

## 🔒 Безопасность

> Приложение предназначено для использования во внутренней сети.

- CORS открыт для всех доменов (`*`) — ограничить при внешнем доступе
- Нет аутентификации — планируется
- Нет ограничений на размер файлов

---

## 🐛 Проблемы и обратная связь

[GitHub Issues](https://github.com/SergeyBakunin/DSO-Tools/issues)

---

## 👤 Автор

**Sergey Bakunin** — [@SergeyBakunin](https://github.com/SergeyBakunin)

---

**Версия:** 1.6.6 | **Обновлено:** 07 апреля 2026
