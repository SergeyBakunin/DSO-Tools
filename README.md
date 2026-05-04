# DevSecOps Tools

> Набор инструментов для работы с SBOM и управления уязвимостями

![Version](https://img.shields.io/badge/version-1.6.8-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![Status](https://img.shields.io/badge/status-active-success)

---

## Быстрый старт

```bash
docker pull sergeybakunin/devsecops-tools-backend:1.6.8
docker pull sergeybakunin/devsecops-tools-frontend:1.6.8

cd docker
docker compose up -d --no-build
```

Открыть: **http://localhost:3000**

Подробнее: [QUICK_START.md](instructions/QUICK_START.md) | [DEPLOYMENT_GUIDE.md](instructions/DEPLOYMENT_GUIDE.md)

---

## Инструменты

### Выгрузка уязвимостей
Поиск уязвимостей по проекту и версии через Artifactory и CodeScoring.

- Поиск SBOM в Artifactory по названию и версии
- Автовыбор ближайшего скана в пределах ±3 дней от даты загрузки SBOM
- Чекбоксы выбора проектов, индикатор "В SBOM" — зелёная подсветка проектов из SBOM
- Скачивание архива SBOM из Artifactory
- Экспорт в **CSV** и **VEX JSON**

### Триаж VEX
Редактирование состояния уязвимостей в CycloneDX VEX файле.

- Загрузка VEX JSON (drag-and-drop)
- Редактирование `State`, `Justification`, `Response`, `Detail`
- Массовое применение статуса к выбранным записям
- Сортировка по CVE/Компоненту/Severity/State
- Фильтр по Severity с цветными чекбоксами
- Валидация обязательного поля Detail перед экспортом

### Конвертер VEX
Конвертация CycloneDX SBOM или XLSX в формат VEX.

- Поддержка **CycloneDX SBOM v1.6 (JSON)** и **XLSX**
- Фильтрация по проектам, массовый экспорт в ZIP
- **Скачать XLS с уязвимостями** — Excel отчёт (CVE, Компонент, Severity, CVSS, CWE, State)

### Валидатор VEX
Валидация VEX документов по стандарту CycloneDX 1.6.

- Структура, обязательные поля, метаданные
- Допустимые значения `state`, `justification`, `response`
- Детальный отчёт об ошибках и предупреждениях

### SBOM Merger
Объединение нескольких SBOM файлов из ZIP архива.

- Рекурсивное сканирование вложенных ZIP архивов
- Дедупликация компонентов и уязвимостей
- Результат в ZIP

---

## Технологии

| | Стек |
|---|---|
| **Backend** | Python 3.13, FastAPI, Pandas, openpyxl, uvicorn |
| **Frontend** | React 18.2, Axios |
| **Deploy** | Docker, Nginx (reverse proxy) |
| **Registry** | [DockerHub: sergeybakunin](https://hub.docker.com/u/sergeybakunin) |

---

## Docker

```bash
# Готовые образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.8
docker pull sergeybakunin/devsecops-tools-frontend:1.6.8

# Сборка из исходников (ARM/Mac → linux/amd64)
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.8 ./backend

docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.8 ./frontend
```

Подробнее: [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md)

---

## API

**Swagger UI:** http://localhost:8000/docs

| Endpoint | Описание |
|---|---|
| `POST /api/vulnerability-report/fetch` | Поиск уязвимостей |
| `POST /api/vulnerability-report/export-csv` | Экспорт в CSV |
| `POST /api/vulnerability-report/export-vex` | Экспорт в VEX JSON |
| `POST /api/vulnerability-report/export-sbom` | Скачивание архива SBOM из Artifactory |
| `POST /api/sbom-to-vex` | Анализ SBOM → статистика |
| `POST /api/sbom-to-vex/export` | SBOM → VEX JSON файл |
| `POST /api/sbom-to-xlsx` | SBOM/VEX → Excel с уязвимостями |
| `POST /api/xlsx-to-vex` | XLSX → VEX (анализ) |
| `POST /api/xlsx-to-vex/export` | XLSX → VEX JSON файл |
| `POST /api/xlsx-to-vex/export-all-projects` | XLSX → ZIP (все проекты) |
| `POST /api/xlsx-to-vex/projects` | Список проектов из XLSX |
| `POST /api/vex/validate` | Валидация VEX документа |
| `POST /api/sbom-merge` | Анализ ZIP с SBOM файлами |
| `POST /api/sbom-merge/export` | Объединение SBOM → ZIP |

---

## Структура проекта

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
│   │   │   ├── VulnerabilityReport.js
│   │   │   ├── VexTriage.js
│   │   │   ├── VEXConverter.js
│   │   │   ├── VEXValidator.js
│   │   │   └── SBOMMerger.js
│   │   ├── App.js
│   │   └── App.css
│   ├── nginx.conf
│   └── Dockerfile
├── docker/
│   └── docker-compose.yml
├── instructions/
│   ├── CHANGELOG.md
│   ├── QUICK_START.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DOCKER_GUIDE.md
│   ├── PROJECT_STATUS.md
│   ├── TECHNICAL_NOTES.md
│   └── VEX_CONVERTER_README.md
└── README.md
```

---

## Документация

| Документ | Описание |
|---|---|
| [QUICK_START.md](instructions/QUICK_START.md) | Запуск за 5 минут |
| [DEPLOYMENT_GUIDE.md](instructions/DEPLOYMENT_GUIDE.md) | Развёртывание на сервере |
| [DOCKER_GUIDE.md](instructions/DOCKER_GUIDE.md) | Работа с Docker |
| [VEX_CONVERTER_README.md](instructions/VEX_CONVERTER_README.md) | Конвертер VEX — API и примеры |
| [CHANGELOG.md](instructions/CHANGELOG.md) | История изменений |
| [PROJECT_STATUS.md](instructions/PROJECT_STATUS.md) | Статус проекта |

---

## Безопасность

Приложение предназначено для использования во внутренней сети.

- CORS открыт (`*`) — ограничить при внешнем доступе
- Аутентификация не реализована

---

## Проблемы и обратная связь

[GitHub Issues](https://github.com/SergeyBakunin/DSO-Tools/issues)

---

**Автор:** Sergey Bakunin — [@SergeyBakunin](https://github.com/SergeyBakunin)

**Версия:** 1.6.8 | **Обновлено:** 04 мая 2026
