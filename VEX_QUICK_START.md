# VEX Converter - Быстрый старт

## Запуск за 5 минут

### Шаг 1: Запустите приложение

**Терминал 1 - Backend:**
```bash
cd backend/app
py main.py
```

**Терминал 2 - Frontend:**
```bash
cd frontend
npm start
```

### Шаг 2: Откройте браузер

Перейдите на http://localhost:3000

### Шаг 3: Используйте VEX Converter

1. Нажмите на карточку **"VEX Converter"**
2. Загрузите ваш SBOM файл (формат: CycloneDX v1.6 JSON)
3. Нажмите **"Анализировать SBOM"** для просмотра статистики
4. Нажмите **"Конвертировать в VEX"** для создания VEX документа

Готово! VEX документ автоматически загрузится.

---

## Пример через API (curl)

```bash
# Конвертация SBOM в VEX
curl -X POST "http://localhost:8000/api/sbom-to-vex/export" \
  -F "sbom_file=@your_sbom_file.json" \
  -o vex_document.json

# Результат: vex_document.json
```

---

## Пример через API (Python)

```python
import requests

# Анализ SBOM
with open('sbom.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/sbom-to-vex',
        files={'sbom_file': f}
    )
    print(response.json())

# Конвертация в VEX
with open('sbom.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/sbom-to-vex/export',
        files={'sbom_file': f}
    )
    with open('vex.json', 'wb') as vex:
        vex.write(response.content)
```

---

## Тестовый пример

Используйте тестовый скрипт:

```bash
cd C:\Users\Sergey Bakunin\sbom-tools
py test_vex_converter.py
```

Результат будет сохранён в `test_vex_output.json`

---

## Что дальше?

📖 **Полная документация:** [VEX_CONVERTER_README.md](VEX_CONVERTER_README.md)

📊 **Детали реализации:** [VEX_IMPLEMENTATION_SUMMARY.md](VEX_IMPLEMENTATION_SUMMARY.md)

🔗 **API документация:** http://localhost:8000/docs (Swagger UI)

---

## Поддержка

**Формат входных файлов:** CycloneDX v1.6 (JSON)
**Формат выходных файлов:** CycloneDX VEX v1.6 (JSON)

**Проблемы?**
- Проверьте формат SBOM файла
- Убедитесь, что SBOM содержит уязвимости
- Проверьте логи backend в терминале

---

Made with ❤️ using FastAPI and React
