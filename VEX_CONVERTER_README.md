# VEX Converter - Документация

## Описание

**VEX Converter** - модуль для конвертации SBOM файлов в формате CycloneDX v1.6 в формат VEX (Vulnerability Exploitability eXchange).

### Что такое VEX?

VEX (Vulnerability Exploitability eXchange) - это стандарт для обмена информацией о применимости уязвимостей к конкретным продуктам. VEX документ помогает:
- Определить, какие уязвимости действительно применимы к вашему продукту
- Задокументировать статус каждой уязвимости (affected, not_affected, fixed, under_investigation)
- Предоставить обоснование для каждого статуса
- Автоматизировать процесс принятия решений по уязвимостям

---

## Возможности

### Backend (Python/FastAPI)

**Реализованные функции:**
1. `convert_sbom_to_vex()` - основная функция конвертации
2. `POST /api/sbom-to-vex` - endpoint для анализа SBOM
3. `POST /api/sbom-to-vex/export` - endpoint для экспорта VEX документа

**Что конвертируется:**
- ✅ Все уязвимости из SBOM
- ✅ Рейтинги и оценки (CVSS scores)
- ✅ Ссылки на источники (NVD, GitHub Advisories, BDU FSTEC и т.д.)
- ✅ CWE классификация
- ✅ Описания и детали уязвимостей
- ✅ Рекомендации по устранению
- ✅ Затронутые компоненты (affects)
- ✅ Даты публикации и обновления
- ✅ Дополнительные свойства (properties)
- ✅ Метаданные компонента из исходного SBOM

**Анализ уязвимостей:**
Для каждой уязвимости автоматически добавляется секция `analysis` с полями:
- `state`: статус уязвимости (по умолчанию: "not_affected")
- `justification`: обоснование (по умолчанию: "component_not_present")
- `detail`: детали (по умолчанию: "Automated conversion from SBOM. Manual review required.")

---

## API Endpoints

### 1. `POST /api/sbom-to-vex`

Анализирует SBOM и возвращает статистику конвертации.

**Параметры:**
- `sbom_file` (file): SBOM файл в формате CycloneDX v1.6 (JSON)

**Ответ:**
```json
{
  "status": "success",
  "sbom_vulnerabilities": 63,
  "vex_vulnerabilities": 63,
  "sbom_components": 294,
  "sbom_format": "CycloneDX",
  "sbom_version": "1.6",
  "vex_serial_number": "urn:uuid:6f9ec72a-e5a4-41e0-83a2-5abc07587eb5",
  "conversion_timestamp": "2025-10-18T13:08:11.976761Z"
}
```

**Пример использования (curl):**
```bash
curl -X POST "http://localhost:8000/api/sbom-to-vex" \
  -F "sbom_file=@bom_CRAB_CRAB_file_cyclonedx_v1_6.json"
```

### 2. `POST /api/sbom-to-vex/export`

Конвертирует SBOM в VEX и возвращает JSON файл для скачивания.

**Параметры:**
- `sbom_file` (file): SBOM файл в формате CycloneDX v1.6 (JSON)

**Ответ:**
- Бинарный файл (application/json) с VEX документом
- Имя файла: `<исходное_имя>_vex.json`

**Пример использования (curl):**
```bash
curl -X POST "http://localhost:8000/api/sbom-to-vex/export" \
  -F "sbom_file=@bom_CRAB_CRAB_file_cyclonedx_v1_6.json" \
  -o vex_document.json
```

---

## Frontend (React)

**Компонент:** `VEXConverter.js`

**Функции:**
1. Загрузка SBOM файла (JSON)
2. Анализ SBOM с выводом статистики
3. Конвертация и скачивание VEX документа

**Интерфейс:**
- Поле для загрузки SBOM файла
- Кнопка "Анализировать SBOM" - показывает статистику
- Кнопка "Конвертировать в VEX" - создаёт и скачивает VEX файл
- Информационная секция с описанием VEX и инструкциями

---

## Использование

### Через Web-интерфейс

1. Запустите backend и frontend:
   ```bash
   # Terminal 1 - Backend
   cd backend/app
   py main.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

2. Откройте http://localhost:3000

3. Выберите карточку **"VEX Converter"**

4. Загрузите SBOM файл в формате CycloneDX v1.6 (JSON)

5. Нажмите **"Анализировать SBOM"** для просмотра статистики

6. Нажмите **"Конвертировать в VEX"** для создания и скачивания VEX документа

### Через API (Python)

```python
import requests

# Анализ SBOM
with open('bom_CRAB_CRAB_file_cyclonedx_v1_6.json', 'rb') as f:
    files = {'sbom_file': f}
    response = requests.post('http://localhost:8000/api/sbom-to-vex', files=files)
    print(response.json())

# Конвертация и сохранение VEX
with open('bom_CRAB_CRAB_file_cyclonedx_v1_6.json', 'rb') as f:
    files = {'sbom_file': f}
    response = requests.post('http://localhost:8000/api/sbom-to-vex/export', files=files)

    with open('vex_document.json', 'wb') as vex_file:
        vex_file.write(response.content)
```

### Программное использование функции

```python
from backend.app.main import convert_sbom_to_vex
import json

# Загрузка SBOM
with open('sbom.json', 'r') as f:
    sbom_data = json.load(f)

# Конвертация
vex_data = convert_sbom_to_vex(sbom_data)

# Сохранение VEX
with open('vex.json', 'w') as f:
    json.dump(vex_data, f, indent=2, ensure_ascii=False)
```

---

## Пример VEX документа

```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:6f9ec72a-e5a4-41e0-83a2-5abc07587eb5",
  "version": 1,
  "metadata": {
    "timestamp": "2025-10-18T13:08:11.976761Z",
    "tools": {
      "components": [
        {
          "type": "application",
          "name": "DevSecOps Tools - SBOM to VEX Converter",
          "version": "1.0.0",
          "description": "Converts CycloneDX SBOM to VEX format"
        }
      ]
    },
    "component": {
      "name": "MyProduct",
      "type": "application",
      "version": "1.0.0"
    }
  },
  "vulnerabilities": [
    {
      "id": "CVE-2016-1000027",
      "bom-ref": "BomRef.3377726651766537.7988194112831386",
      "description": "Pivotal Spring Framework contains unsafe Java deserialization methods",
      "ratings": [
        {
          "score": 9.8,
          "method": "CVSSv3",
          "vector": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
          "severity": "critical"
        }
      ],
      "cwes": [502],
      "affects": [
        {
          "ref": "pkg:maven/org.springframework/spring-web@5.3.31"
        }
      ],
      "analysis": {
        "state": "not_affected",
        "justification": "component_not_present",
        "detail": "Automated conversion from SBOM. Manual review required."
      }
    }
  ]
}
```

---

## Тестирование

### Автоматический тест

Запустите тестовый скрипт:

```bash
cd C:\Users\Sergey Bakunin\sbom-tools
py test_vex_converter.py
```

**Результат теста:**
```
================================================================================
Тестирование конвертера SBOM -> VEX
================================================================================

1. Загрузка SBOM из: [путь к файлу]
   ✓ SBOM загружен успешно
   - Формат: CycloneDX
   - Версия: 1.6
   - Компонентов: 294
   - Уязвимостей: 63

2. Конвертация в VEX формат...
   ✓ Конвертация успешна!

3. Статистика VEX документа:
   - Формат: CycloneDX
   - Версия: 1.6
   - Серийный номер: urn:uuid:...
   - Уязвимостей: 63
   - Время создания: 2025-10-18T13:08:11.976761Z

4. Пример первой уязвимости в VEX:
   - ID: CVE-2016-1000027
   - Описание: ...
   - Рейтинги: 2
   - Ссылки: 8
   - CWE: [502]
   - Затронутые компоненты: 1
   - Анализ: {...}

5. Сохранение VEX документа в: test_vex_output.json
   ✓ VEX документ сохранён успешно!

================================================================================
Тест завершён успешно!
================================================================================
```

---

## Структура файлов

```
sbom-tools/
├── backend/
│   └── app/
│       └── main.py                    # Функция convert_sbom_to_vex() + endpoints
├── frontend/
│   └── src/
│       ├── components/
│       │   └── VEXConverter.js        # React компонент
│       └── App.js                      # Роутинг (VEX Converter активен)
├── test_vex_converter.py               # Тестовый скрипт
├── test_vex_output.json                # Пример результата
└── VEX_CONVERTER_README.md             # Эта документация
```

---

## Ограничения и будущие улучшения

### Текущие ограничения:
- Анализ уязвимостей по умолчанию: `state: not_affected`, требует ручной проверки
- Поддерживается только CycloneDX v1.6 (JSON формат)

### Планируемые улучшения:
- [ ] Автоматическая классификация уязвимостей по критичности
- [ ] Интеграция с базами данных уязвимостей для автоматического определения статуса
- [ ] Поддержка пакетной конвертации нескольких SBOM файлов
- [ ] Валидация VEX документа по схеме CycloneDX
- [ ] Экспорт в другие VEX форматы (OpenVEX, CSAF VEX)
- [ ] История конвертаций с сохранением в БД

---

## Соответствие стандартам

**CycloneDX VEX спецификация:**
- ✅ Структура VEX документа соответствует CycloneDX 1.6
- ✅ Поля `vulnerabilities` полностью совместимы
- ✅ Секция `analysis` поддерживается
- ✅ Метаданные включают информацию о конвертере
- ✅ Серийные номера генерируются по стандарту URN UUID

**Статусы VEX (state):**
- `not_affected` - компонент не затронут уязвимостью
- `affected` - компонент затронут уязвимостью
- `fixed` - уязвимость устранена
- `under_investigation` - уязвимость находится на рассмотрении

**Обоснования (justification):**
- `component_not_present` - компонент отсутствует в продукте
- `vulnerable_code_not_present` - уязвимый код не используется
- `vulnerable_code_not_in_execute_path` - уязвимый код не выполняется
- `vulnerable_code_cannot_be_controlled_by_adversary` - уязвимый код недоступен атакующему
- `inline_mitigations_already_exist` - существуют встроенные меры защиты

---

## Лицензия

Не указана (TODO)

---

## Автор

**Sergey Bakunin**
**Инструмент:** DevSecOps Tools v1.0.0
**Дата создания:** 18 октября 2025

---

## Контакты и поддержка

- **Проект:** C:\Users\Sergey Bakunin\sbom-tools
- **Backend:** FastAPI, Python 3.13
- **Frontend:** React 18.2.0
- **API документация:** http://localhost:8000/docs (Swagger UI)

---

Made with Claude AI
