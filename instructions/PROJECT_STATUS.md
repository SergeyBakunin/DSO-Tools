# DevSecOps Tools — Статус проекта

**Версия:** 1.6.8
**Дата обновления:** 04 мая 2026
**Статус:** Active Development

---

## Реализованные инструменты

### Выгрузка уязвимостей
**Файлы:** `backend/app/vulnerability_report.py`, `frontend/src/components/VulnerabilityReport.js`

- Поиск SBOM в Artifactory по проекту и версии
- История сканов через CodeScoring API (stdlib urllib)
- Автовыбор ближайшего скана ±3 дня от даты загрузки SBOM
- Чекбоксы выбора проектов при экспорте
- Индикатор "В SBOM" — сопоставление проектов CodeScoring с компонентами SBOM
- Скачивание архива SBOM из Artifactory
- Экспорт: CSV, VEX JSON, детальный лог

**Endpoints:**
- `POST /api/vulnerability-report/fetch`
- `POST /api/vulnerability-report/export-csv`
- `POST /api/vulnerability-report/export-vex`
- `POST /api/vulnerability-report/export-sbom`

---

### Триаж VEX
**Файл:** `frontend/src/components/VexTriage.js`

- Загрузка VEX JSON (drag-and-drop)
- Редактирование State / Justification / Response / Detail
- Массовое применение State к выбранным записям
- Сортировка по CVE/Компоненту/Severity/State
- Фильтр по Severity (чекбоксы) для скачиваемого файла
- Валидация Detail перед экспортом

**Валидные State (CycloneDX 1.6):** `in_triage`, `affected`, `not_affected`, `exploitable`, `false_positive`, `resolved`

---

### Конвертер VEX
**Файлы:** `backend/app/main.py`, `frontend/src/components/VEXConverter.js`

- CycloneDX SBOM v1.6 (JSON) → VEX JSON
- XLSX с уязвимостями → VEX JSON (фильтрация по проектам, ZIP для всех проектов)
- Excel экспорт: CVE ID, Компонент, Версия, Severity, CVSS, CWE, Описание, State, Разметка

**Endpoints:** `/api/sbom-to-vex`, `/api/sbom-to-vex/export`, `/api/sbom-to-xlsx`, `/api/xlsx-to-vex`, `/api/xlsx-to-vex/export`, `/api/xlsx-to-vex/projects`, `/api/xlsx-to-vex/export-all-projects`

---

### Валидатор VEX
**Файлы:** `backend/app/main.py`, `frontend/src/components/VEXValidator.js`

- Структура документа (bomFormat, specVersion, serialNumber, version)
- Метаданные (timestamp, tools, component)
- `analysis`: допустимые state, justification, response
- Статистика по статусам

**Endpoint:** `POST /api/vex/validate`

---

### SBOM Merger
**Файлы:** `backend/app/main.py`, `frontend/src/components/SBOMMerger.js`

- Рекурсивное сканирование ZIP (вложенные архивы)
- Объединение нескольких SBOM в один для каждой папки
- Дедупликация компонентов и уязвимостей
- Статистика, результат в ZIP

**Endpoints:** `POST /api/sbom-merge`, `POST /api/sbom-merge/export`

---

## Coming Soon

### Security posture
Дашборд сводной статистики по уязвимостям — заглушка в боковом меню, реализация запланирована.

---

## Технический стек

| Компонент | Версия |
|---|---|
| Python | 3.13 |
| FastAPI | latest |
| pandas | ≥2.2.0 |
| openpyxl | 3.1.2 |
| xlsxwriter | 3.1.9 |
| React | 18.2 |
| Axios | 1.x |
| Nginx | alpine |
| Docker образы | `sergeybakunin/devsecops-tools-*:1.6.8` |

---

## Архитектура

```
Browser
  │
  ▼ :3000
Nginx (frontend container)
  │
  ├── статика (React build)
  │
  └── /api/* ──► Backend (FastAPI) :8000
                    │
                    ├── vulnerability_report.py  (Artifactory + CodeScoring)
                    └── main.py                  (VEX, SBOM, Merger, Validator)
```

Все API запросы из браузера идут через nginx proxy (`/api → http://backend:8000`).
В frontend компонентах `API_URL = ''` (относительный URL).

---

## Известные ограничения

- CORS открыт (`*`) — для продакшена нужно ограничить
- Нет аутентификации
- Конфиг Artifactory/CodeScoring только через `config.yaml`, нет UI настроек

---

**Автор:** Sergey Bakunin
**Репозиторий:** https://github.com/SergeyBakunin/DSO-Tools
