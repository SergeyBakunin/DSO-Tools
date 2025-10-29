# VEX Converter Enhancement - XLSX Support

## Дата: 2025-10-29
## Версия: v1.2.0

---

## Обзор изменений

Добавлена поддержка конвертации XLSX файлов с уязвимостями в формат CycloneDX VEX v1.6. Теперь VEX Converter поддерживает два входных формата:
- **JSON**: CycloneDX SBOM (существующая функциональность)
- **XLSX**: Таблицы с уязвимостями из систем анализа (CodeScoring, NBSS, и т.д.) - **НОВОЕ!**

---

## Мотивация

Файл `NBSS 2_1_6_for_vex.xlsx` содержит 2,528 записей уязвимостей с полными VEX-совместимыми полями:
- **State** (100% заполнено): `in_triage` (1,895), `not_affected` (633)
- **Justification** (25% заполнено): `protected_by_mitigating_control`, `code_not_present`
- **Detail** (25% заполнено): детали анализа на русском языке
- Полная информация: CVE IDs, CVSS scores, CWEs, компоненты, версии, проекты, технологии

Необходимо было преобразовать эту информацию в стандартный VEX формат для обмена данными о применимости уязвимостей.

---

## Технические изменения

### 1. Backend (Python/FastAPI)

#### Новая функция: `convert_xlsx_to_vex()`
**Файл:** `backend/app/main.py` (строки 346-638)

**Функциональность:**
- Читает DataFrame из XLSX файла
- Валидирует обязательные колонки: `CVE ID`, `Dependency name`, `Dependency version`
- Создает VEX документ CycloneDX v1.6 со всеми полями
- Маппинг XLSX колонок → VEX структура:

```python
XLSX Column              → VEX Field
─────────────────────────────────────────────────────────
CVE ID                   → vulnerability.id
CVE Link / GHSA Link     → vulnerability.references
CVSS 3 Score/Severity    → vulnerability.ratings (CVSSv3)
CVSS 2 Score/Severity    → vulnerability.ratings (CVSSv2)
CWEs                     → vulnerability.cwes
Summary                  → vulnerability.description
Fixed version            → vulnerability.recommendation
Published / Updated      → vulnerability.published/updated
Dependency name/version  → vulnerability.affects
Technology               → vulnerability.properties (technology)
Relation                 → vulnerability.properties (dependency_relation)
Env                      → vulnerability.properties (environment)
Project                  → vulnerability.properties (project)
Has exploit              → vulnerability.properties (has_exploit)

# КЛЮЧЕВЫЕ VEX ПОЛЯ:
State                    → vulnerability.analysis.state
Justification            → vulnerability.analysis.justification
Response                 → vulnerability.analysis.response
Detail                   → vulnerability.analysis.detail
```

**Особенности реализации:**
- Валидация VEX полей согласно CycloneDX спецификации
- Автоматическое определение названия продукта из данных (если не указано)
- Парсинг CWE ID из строк формата "CWE-79, CWE-80"
- Конвертация дат в ISO 8601 формат
- Обработка пустых значений (NaN) в pandas DataFrame

#### Новые API эндпоинты

**1. POST `/api/xlsx-to-vex`**
- Конвертирует XLSX в VEX и возвращает статистику
- Параметры:
  - `xlsx_file` (file, обязательный): XLSX файл с уязвимостями
  - `product_name` (string, опциональный): название продукта
  - `product_version` (string, опциональный): версия продукта
- Возвращает JSON с детальной статистикой:
  - Распределение по статусам (state_distribution)
  - Распределение по обоснованиям (justification_distribution)
  - Распределение по проектам (project_distribution)
  - Распределение по технологиям (technology_distribution)
  - Количество уязвимостей с эксплойтами

**2. POST `/api/xlsx-to-vex/export`**
- Конвертирует XLSX в VEX и возвращает JSON файл для скачивания
- Параметры: те же
- Возвращает: VEX документ в формате JSON (Content-Type: application/json)
- Имя файла: `{original_name}_vex.json`

### 2. Frontend (React)

#### Обновленный компонент: `VEXConverter.js`
**Файл:** `frontend/src/components/VEXConverter.js`

**Новые возможности:**

1. **Автоопределение типа файла**
   ```javascript
   const [fileType, setFileType] = useState(null); // 'json' or 'xlsx'

   // В handleFileChange:
   if (file.name.endsWith('.json')) {
     setFileType('json');
   } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
     setFileType('xlsx');
   }
   ```

2. **Условные поля для XLSX**
   - Появляются только при выборе XLSX файла
   - Поля: Product Name, Product Version
   - Опциональные (автозаполнение из данных)

3. **Динамическая маршрутизация API**
   ```javascript
   if (fileType === 'json') {
     endpoint = '/api/sbom-to-vex/export';
     formData.append('sbom_file', sbomFile);
   } else if (fileType === 'xlsx') {
     endpoint = '/api/xlsx-to-vex/export';
     formData.append('xlsx_file', sbomFile);
     if (productName) formData.append('product_name', productName);
     if (productVersion) formData.append('product_version', productVersion);
   }
   ```

4. **Расширенная статистика для XLSX**
   - Отображение распределения по статусам (in_triage, not_affected)
   - Обоснования (justifications)
   - Топ-5 технологий
   - Топ-5 проектов
   - Предупреждение о количестве уязвимостей с эксплойтами

#### Новые CSS стили
**Файл:** `frontend/src/App.css` (строки 98-207)

**Добавленные классы:**
- `.file-type-badge` - бейдж типа файла [JSON]/[XLSX]
- `.file-hint` - подсказка о поддерживаемых форматах
- `.product-info-section` - секция с полями продукта
- `.product-inputs` - grid для полей (2 колонки)
- `.product-input` - стилизованный input
- `.statistics-section` - контейнер статистики
- `.stat-group` - группа статистики с цветным бордером
- `.stat-group.warning` - предупреждающая группа (оранжевая)

---

## Структура VEX документа

### Пример сгенерированного VEX (упрощенно):

```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "version": 1,
  "metadata": {
    "timestamp": "2025-10-29T14:00:00Z",
    "tools": {
      "components": [{
        "type": "application",
        "name": "DevSecOps Tools - XLSX to VEX Converter",
        "version": "1.1.0"
      }]
    },
    "component": {
      "type": "application",
      "name": "Multi-Project Analysis (103 projects)",
      "version": "unknown"
    }
  },
  "vulnerabilities": [
    {
      "id": "CVE-2024-50379",
      "bom-ref": "vuln-0-CVE-2024-50379",
      "source": {
        "name": "NVD",
        "url": "https://nvd.nist.gov/vuln/detail/CVE-2024-50379"
      },
      "references": [
        {
          "id": "CVE-2024-50379",
          "source": {
            "name": "NVD",
            "url": "https://nvd.nist.gov/vuln/detail/CVE-2024-50379"
          }
        },
        {
          "id": "GHSA-xxxx-xxxx-xxxx",
          "source": {
            "name": "GHSA",
            "url": "https://github.com/advisories/GHSA-xxxx-xxxx-xxxx"
          }
        }
      ],
      "ratings": [
        {
          "source": {"name": "NVD"},
          "score": 9.8,
          "severity": "critical",
          "method": "CVSSv3",
          "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        }
      ],
      "cwes": [367, 937, 1035],
      "description": "Apache Tomcat vulnerability description...",
      "recommendation": "Update to version 10.1.31",
      "published": "2024-10-15T00:00:00Z",
      "updated": "2024-10-20T00:00:00Z",
      "properties": [
        {"name": "technology", "value": "Java"},
        {"name": "dependency_relation", "value": "Indirect"},
        {"name": "environment", "value": "compile"},
        {"name": "project", "value": "my-backend-service"},
        {"name": "has_exploit", "value": "true"}
      ],
      "affects": [
        {
          "ref": "pkg:maven/org.apache.tomcat.embed/tomcat-embed-core@10.1.24",
          "versions": [
            {"version": "10.1.24", "status": "affected"},
            {"version": "10.1.31", "status": "unaffected"}
          ]
        }
      ],
      "analysis": {
        "state": "in_triage",
        "detail": "Vulnerability is under review by security team"
      }
    }
  ]
}
```

---

## Валидация VEX полей

### State (обязательное поле)
**Допустимые значения:** `exploitable`, `in_triage`, `false_positive`, `not_affected`, `resolved`

Из файла:
- `in_triage` → 1,895 уязвимостей (75%)
- `not_affected` → 633 уязвимости (25%)

### Justification (требуется для `not_affected`)
**Допустимые значения:**
- `code_not_present`
- `code_not_reachable`
- `requires_configuration`
- `requires_dependency`
- `requires_environment`
- `protected_by_compiler`
- `protected_by_mitigating_control`

Из файла:
- `protected_by_mitigating_control` → 603 уязвимости
- `code_not_present` → 30 уязвимостей

### Response (опционально)
**Допустимые значения:** `can_not_fix`, `will_not_fix`, `update`, `rollback`, `workaround_available`

В файле: пусто (можно добавить вручную)

### Detail (опционально)
Свободный текст с дополнительными деталями анализа.

В файле: 633 записи с текстом на русском языке (детали обоснования)

---

## Инструкция по использованию

### 1. Подготовка XLSX файла

**Обязательные колонки:**
- `CVE ID` - идентификатор уязвимости
- `Dependency name` - название зависимости
- `Dependency version` - версия зависимости

**Рекомендуемые VEX колонки:**
- `State` - статус анализа
- `Justification` - обоснование (для not_affected)
- `Response` - ответное действие
- `Detail` - детали анализа

**Дополнительные колонки** (все опциональные):
- CVE Link, GHSA ID, GHSA Link
- CVSS 2 Score, CVSS 2 Severity, CVSS 2 Metrics
- CVSS 3 Score, CVSS 3 Severity, CVSS 3 Metrics
- CWEs, Summary, Fixed version
- Technology, Relation, Env, Project
- Has exploit, Published, Updated, Files

### 2. Использование через UI

1. Откройте приложение: http://localhost:3000
2. Выберите **VEX Converter**
3. Загрузите XLSX файл (увидите бейдж `[XLSX]`)
4. Опционально: укажите название и версию продукта
5. Нажмите **"Анализировать XLSX"** для просмотра статистики
6. Нажмите **"Конвертировать в VEX"** для скачивания JSON

### 3. Использование через API

**Анализ XLSX:**
```bash
curl -X POST http://localhost:8000/api/xlsx-to-vex \
  -F "xlsx_file=@NBSS_2_1_6_for_vex.xlsx" \
  -F "product_name=My Application" \
  -F "product_version=1.0.0"
```

**Экспорт VEX:**
```bash
curl -X POST http://localhost:8000/api/xlsx-to-vex/export \
  -F "xlsx_file=@NBSS_2_1_6_for_vex.xlsx" \
  -F "product_name=My Application" \
  -F "product_version=1.0.0" \
  -o output_vex.json
```

---

## Пример результата статистики

```json
{
  "status": "success",
  "source_filename": "NBSS 2_1_6_for_vex.xlsx",
  "source_rows": 2528,
  "vex_vulnerabilities": 2524,
  "vex_serial_number": "urn:uuid:12345678-1234-1234-1234-123456789abc",
  "vex_version": "1.6",
  "conversion_timestamp": "2025-10-29T14:00:00Z",
  "product_name": "Multi-Project Analysis (103 projects)",
  "product_version": "unknown",
  "statistics": {
    "state_distribution": {
      "in_triage": 1895,
      "not_affected": 633
    },
    "justification_distribution": {
      "protected_by_mitigating_control": 603,
      "code_not_present": 30
    },
    "project_distribution": {
      "backend-service": 450,
      "frontend-app": 320,
      "api-gateway": 280,
      "...": "..."
    },
    "technology_distribution": {
      "Java": 1854,
      "JavaScript": 278,
      "Go": 145,
      "Rust": 89,
      "Python": 77
    },
    "has_exploit_count": 1252
  }
}
```

---

## Преимущества решения

### 1. Полная совместимость с CycloneDX VEX v1.6
- Валидация всех VEX полей
- Правильный маппинг XLSX → VEX структура
- Поддержка всех обязательных и опциональных полей

### 2. Универсальность
- Работает с любыми XLSX файлами, содержащими базовые колонки
- Автоматическая обработка различных форматов данных
- Гибкая конфигурация через опциональные параметры

### 3. Детальная статистика
- Распределение по статусам анализа
- Идентификация уязвимостей с эксплойтами
- Анализ по проектам и технологиям
- Визуализация обоснований

### 4. Удобство использования
- Drag & drop загрузка файлов
- Автоопределение формата файла
- Понятные подсказки и валидация
- Детальная документация в UI

---

## Тестирование

### Тестовый файл
**Файл:** `NBSS 2_1_6_for_vex.xlsx`
- Строки: 2,528
- Уязвимости: 2,524 (4 без CVE ID)
- Проекты: 103
- Технологии: 10
- Статусы: in_triage (75%), not_affected (25%)

### Ожидаемый результат
- VEX документ с 2,524 уязвимостями
- Все CVE с полными данными CVSS
- Корректный маппинг analysis.state и analysis.justification
- Properties с технологиями, проектами, окружением
- Affects с компонентами и версиями

### Проверка валидности
```bash
# Проверка через CycloneDX CLI (если установлен)
cyclonedx validate --input-file output_vex.json --schema-version 1.6

# Проверка структуры JSON
jq '.vulnerabilities | length' output_vex.json  # Должно быть 2524
jq '.vulnerabilities[0].analysis.state' output_vex.json  # Проверка VEX полей
```

---

## Следующие шаги

### Возможные улучшения:
1. **Batch processing** - обработка нескольких XLSX файлов
2. **Template validation** - валидация структуры XLSX перед конвертацией
3. **Custom mappings** - пользовательский маппинг колонок
4. **Export formats** - экспорт в другие форматы (CSV, HTML отчет)
5. **VEX diff** - сравнение двух VEX документов
6. **Automated remediation** - автоматические рекомендации по исправлению

---

## Заключение

Модуль VEX Converter теперь поддерживает полный цикл работы с уязвимостями:
1. **Импорт** из SBOM (JSON) или таблиц анализа (XLSX)
2. **Анализ** и статистика
3. **Конвертация** в стандартный VEX формат CycloneDX v1.6
4. **Экспорт** для обмена данными между системами

Это позволяет унифицировать работу с данными о уязвимостях независимо от источника данных.

---

**Версия:** v1.2.0
**Дата:** 2025-10-29
**Автор:** DevSecOps Tools Team
