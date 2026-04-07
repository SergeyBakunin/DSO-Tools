# VEX Converter — Документация

**Версия:** 1.6.5
**Последнее обновление:** 2026-04-07

---

## Описание

**Конвертер VEX** — модуль для работы с CycloneDX VEX/SBOM файлами:
- Конвертация CycloneDX SBOM (JSON) или XLSX в формат VEX
- Экспорт уязвимостей в Excel для передачи командам разработки

---

## Возможности

### Backend — API Endpoints

| Endpoint | Метод | Описание |
|---|---|---|
| `/api/sbom-to-vex` | POST | Анализ SBOM, возвращает статистику |
| `/api/sbom-to-vex/export` | POST | Конвертация SBOM → VEX JSON для скачивания |
| `/api/sbom-to-xlsx` | POST | Экспорт уязвимостей из SBOM/VEX → Excel |
| `/api/xlsx-to-vex` | POST | Конвертация XLSX → VEX |
| `/api/xlsx-to-vex/export` | POST | Экспорт XLSX → VEX JSON для скачивания |
| `/api/xlsx-to-vex/projects` | POST | Получение списка проектов из XLSX |
| `/api/xlsx-to-vex/export-all-projects` | POST | Экспорт всех проектов из XLSX → ZIP |

### Frontend — компонент `VEXConverter.js`

- Загрузка файла: CycloneDX SBOM JSON или XLSX
- **Анализировать SBOM** — статистика по уязвимостям и компонентам
- **Конвертировать в VEX** — создать и скачать VEX JSON документ
- **⬇ Скачать XLS с уязвимостями** — экспорт в Excel (только для JSON файлов)

---

## Excel экспорт (`/api/sbom-to-xlsx`)

Генерирует `.xlsx` файл со следующими столбцами:

| Столбец | Источник в JSON |
|---|---|
| CVE ID | `vulnerabilities[].id` |
| Компонент | `components[]` по `affects[].ref` |
| Версия | `components[].version` |
| Severity | `ratings[].severity` (предпочтение CVSSv3) |
| CVSS Score | `ratings[].score` |
| CVSS Vector | `ratings[].vector` |
| CWE | `vulnerabilities[].cwes[]` |
| Описание | `vulnerabilities[].description` |
| State | `analysis.state` |
| Разметка | `analysis.detail` (пусто для чистого SBOM, заполнено для VEX) |

**Форматирование:**
- Ячейки Severity окрашены: Critical=красный, High=оранжевый, Medium=жёлтый, Low=зелёный
- Автофильтр на всех столбцах
- Заморозка первой строки
- Перенос текста в столбцах "Описание" и "Разметка"

---

## API — примеры запросов

### Анализ SBOM
```bash
curl -X POST "http://localhost:8000/api/sbom-to-vex" \
  -F "sbom_file=@sbom.json"
```

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
  "conversion_timestamp": "2026-04-07T10:00:00Z"
}
```

### Экспорт VEX JSON
```bash
curl -X POST "http://localhost:8000/api/sbom-to-vex/export" \
  -F "sbom_file=@sbom.json" \
  -o vex_document.json
```

### Экспорт уязвимостей в Excel
```bash
curl -X POST "http://localhost:8000/api/sbom-to-xlsx" \
  -F "sbom_file=@sbom.json" \
  -o vulnerabilities.xlsx
```

---

## Формат VEX документа

Конвертер создаёт CycloneDX 1.6 VEX документ. Для уязвимостей без анализа используется `state: in_triage` (требует ручной разметки через модуль "Триаж VEX").

```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "vulnerabilities": [
    {
      "id": "CVE-2024-1234",
      "ratings": [{ "score": 9.8, "method": "CVSSv3", "severity": "critical" }],
      "affects": [{ "ref": "pkg:maven/org.example/lib@1.0.0" }],
      "analysis": {
        "state": "in_triage"
      }
    }
  ]
}
```

**Валидные значения `state`** (CycloneDX 1.6):
`in_triage` | `affected` | `not_affected` | `exploitable` | `false_positive` | `resolved`

**Валидные значения `justification`** (только при `state: not_affected`):
`code_not_present` | `code_not_reachable` | `requires_configuration` | `requires_dependency` | `requires_environment` | `protected_by_compiler` | `protected_at_runtime` | `protected_at_perimeter` | `protected_by_mitigating_control`

---

## Требования к XLSX файлу

| Столбец | Обязательный |
|---|---|
| CVE ID | ✅ |
| Dependency name | ✅ |
| Dependency version | ✅ |
| State | — |
| Justification | — |
| Response | — |
| Detail | — |
| CVSS Score (v2/v3) | — |
| CWE | — |
| Summary | — |
| Technology | — |
| Project | — |

---

## Структура файлов

```
sbom-tools/
├── backend/app/main.py          # Endpoints: sbom-to-vex, sbom-to-xlsx, xlsx-to-vex
├── frontend/src/components/
│   └── VEXConverter.js          # React компонент
└── instructions/
    └── VEX_CONVERTER_README.md  # Эта документация
```

---

## Docker

```bash
# Запуск
docker compose up -d --no-build

# Образы
docker pull sergeybakunin/devsecops-tools-backend:1.6.5
docker pull sergeybakunin/devsecops-tools-frontend:1.6.5
```

**API документация (Swagger UI):** http://localhost:8000/docs

---

**Автор:** Sergey Bakunin
**Инструмент:** DevSecOps Tools v1.6.5
