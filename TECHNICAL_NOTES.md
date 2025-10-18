# Технические заметки и решения

**Проект:** DevSecOps Tools
**Дата:** 18 октября 2025

---

## 🔧 Решённые технические проблемы

### 1. Проблема совместимости Pandas с Python 3.13

**Проблема:**
```
ERROR: Could not find a version that satisfies the requirement pandas==2.1.4
```

**Причина:** Pandas 2.1.4 не имеет готовых бинарных колёс (wheels) для Python 3.13, требовалась компиляция из исходников с компилятором C++.

**Решение:**
- Обновили `requirements.txt`: `pandas==2.1.4` → `pandas>=2.2.0`
- Pandas 2.3.3 имеет готовые wheels для Python 3.13
- Установка через: `py -m pip install --no-cache-dir pandas`

**Файл:** `backend/requirements.txt`

---

### 2. Отсутствующий компонент SBOMMigrate

**Проблема:**
- В `App.js` был импорт `import SBOMMigrate from './components/SBOMMigrate';`
- Файл не существовал → ошибка при запуске

**Решение:**
- Создан полноценный React компонент `frontend/src/components/SBOMMigrate.js`
- Реализован UI для загрузки файлов
- Добавлена интеграция с API через axios
- Реализована обработка ошибок и отображение результатов

**Файл:** `frontend/src/components/SBOMMigrate.js`

---

### 3. Отсутствие стилей для компонента

**Проблема:**
- Компонент отображался без стилей (как на втором скриншоте)

**Решение:**
- Добавлены CSS стили в `App.css`:
  - `.tool-container` - контейнер инструмента
  - `.back-button` - кнопка возврата
  - `.tool-header` - заголовок инструмента
  - `.upload-section` - секция загрузки файлов
  - `.file-input-group` - группа полей ввода
  - `.format-selector` - селектор формата
  - `.action-buttons` - кнопки действий
  - `.message` - сообщения об ошибках/успехе
  - `.info-section` - информационная секция

**Файл:** `frontend/src/App.css`

---

## 📝 Архитектурные решения

### Backend архитектура

**FastAPI приложение:**
```python
app = FastAPI(title="DevSecOps Tools")
```

**CORS middleware:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: ограничить в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Функции:**
1. `read_file(file: UploadFile) -> pd.DataFrame`
   - Читает CSV или XLSX файлы
   - Возвращает pandas DataFrame

2. `migrate_comments(source_df: DataFrame, target_df: DataFrame) -> DataFrame`
   - Основной алгоритм миграции
   - Создаёт словарь `{(CVE ID, Project): Comment}`
   - Переносит комментарии по совпадению ключа

3. `sbom_migrate()` - API endpoint для предпросмотра
4. `sbom_migrate_export()` - API endpoint для экспорта

### Frontend архитектура

**Структура компонентов:**
```
App
├── Header
└── Tools Grid
    └── Tool Card (x6)
        └── SBOMMigrate (при клике)
```

**State management:**
```javascript
const [activeCard, setActiveCard] = useState(null);
const [sourceFile, setSourceFile] = useState(null);
const [targetFile, setTargetFile] = useState(null);
const [exportFormat, setExportFormat] = useState('xlsx');
const [loading, setLoading] = useState(false);
const [result, setResult] = useState(null);
const [error, setError] = useState(null);
```

---

## 🗃️ Структура данных

### Формат входных файлов (CSV/XLSX)

**Обязательные столбцы:**
- `CVE ID` или `CVE` - идентификатор уязвимости
- `Project` - название проекта
- `Comment` - комментарий (только в source файле)

**Пример:**
```csv
CVE ID,Project,Severity,Comment
CVE-2024-1234,MyProject,High,False positive
CVE-2024-5678,MyProject,Medium,Need to update library
```

### API Responses

**Success (preview):**
```json
{
  "status": "success",
  "source_rows": 150,
  "target_rows": 200,
  "result_rows": 200,
  "columns": ["CVE ID", "Project", "Severity", "Comment"]
}
```

**Error:**
```json
{
  "detail": "Source file missing required columns. Found: ['CVE', 'Title']"
}
```

---

## 🔍 Алгоритм миграции комментариев

### Псевдокод:
```python
# Шаг 1: Нормализация названий столбцов
source_cols = {col.lower().strip(): col for col in source_df.columns}
target_cols = {col.lower().strip(): col for col in result_df.columns}

# Шаг 2: Определение ключевых столбцов
cve_col_source = source_cols.get('cve id') or source_cols.get('cve')
project_col_source = source_cols.get('project')
comment_col_source = source_cols.get('comment')

# Шаг 3: Создание словаря комментариев
comment_map = {}
for row in source_df:
    key = (row[cve_id], row[project])
    if key не пустой and comment не пустой:
        comment_map[key] = comment

# Шаг 4: Перенос комментариев
for row in result_df:
    key = (row[cve_id], row[project])
    if key in comment_map:
        result_df[row_index][comment_col] = comment_map[key]
        matched_count += 1

return result_df
```

### Особенности:
- Ключ состоит из двух полей: CVE ID + Project
- Регистронезависимый поиск столбцов
- Пропуск пустых значений
- Подсчёт успешных совпадений

---

## 🎨 CSS Стили и дизайн-система

### Цветовая палитра:
```css
/* Основные цвета */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--success-gradient: linear-gradient(135deg, #28a745 0%, #20c997 100%);
--error-color: #f44336;
--text-primary: #333;
--text-secondary: #666;
--background-light: #f8f9ff;
```

### Ключевые компоненты UI:

**Карточки:**
```css
.card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}
```

**Кнопки:**
```css
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: all 0.3s ease;
}
```

**Hover эффекты:**
```css
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}
```

---

## 🔌 API Integration

### Axios конфигурация:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### Пример запроса на миграцию:
```javascript
const formData = new FormData();
formData.append('source_file', sourceFile);
formData.append('target_file', targetFile);

const response = await axios.post(`${API_URL}/api/sbom-migrate`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
```

### Пример запроса на экспорт:
```javascript
const response = await axios.post(
  `${API_URL}/api/sbom-migrate/export`,
  formData,
  {
    responseType: 'blob',  // Важно для получения файла
  }
);

// Скачивание файла
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', `sbom_migrated.${exportFormat}`);
document.body.appendChild(link);
link.click();
link.remove();
```

---

## 📦 Зависимости

### Backend (Python):
```
fastapi==0.109.0      # Web framework
uvicorn==0.27.0       # ASGI server
python-multipart==0.0.6  # File upload support
pandas>=2.2.0         # Data processing
openpyxl==3.1.2       # Excel reading
xlsxwriter==3.1.9     # Excel writing
```

### Frontend (React):
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.5",
  "react-scripts": "5.0.1"
}
```

---

## 🐳 Docker конфигурация

### Существующий Dockerfile (backend):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**TODO:** Обновить на Python 3.13 или использовать 3.12

---

## 🧪 Тестирование

### Планируемые тесты:

**Backend:**
- [ ] Unit тесты для `migrate_comments()`
- [ ] Integration тесты для API endpoints
- [ ] Тесты на граничные случаи (пустые файлы, отсутствующие столбцы)

**Frontend:**
- [ ] Component тесты для SBOMMigrate
- [ ] E2E тесты с Cypress/Playwright

### Пример теста (pytest):
```python
def test_migrate_comments():
    source_df = pd.DataFrame({
        'CVE ID': ['CVE-1', 'CVE-2'],
        'Project': ['P1', 'P1'],
        'Comment': ['Comment 1', 'Comment 2']
    })

    target_df = pd.DataFrame({
        'CVE ID': ['CVE-1', 'CVE-3'],
        'Project': ['P1', 'P1']
    })

    result = migrate_comments(source_df, target_df)

    assert result.loc[0, 'Comment'] == 'Comment 1'
    assert pd.isna(result.loc[1, 'Comment'])
```

---

## 🚀 Оптимизации и улучшения

### Текущие ограничения:
1. **Производительность:** Pandas iterate_rows медленный для больших файлов
2. **Память:** Весь файл загружается в память
3. **Безопасность:** Нет проверки размера файла

### Планируемые оптимизации:

**Backend:**
```python
# Использовать vectorized операции pandas
result_df = target_df.merge(
    source_df[['CVE ID', 'Project', 'Comment']],
    on=['CVE ID', 'Project'],
    how='left'
)
```

**Frontend:**
- Добавить прогресс-бар для загрузки файлов
- Реализовать drag-and-drop для файлов
- Добавить превью данных перед миграцией

---

## 📊 Метрики и мониторинг

### Планируемые метрики:
- Количество обработанных файлов
- Среднее время обработки
- Процент успешных совпадений
- Размер обрабатываемых файлов

### Логирование:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Matched {matched_count} comments from {len(comment_map)} available")
```

---

## 🔐 Безопасность (Security Checklist)

### Текущее состояние:
- ❌ Нет аутентификации
- ❌ CORS открыт для всех (`allow_origins=["*"]`)
- ❌ Нет ограничения размера файлов
- ❌ Нет валидации типов файлов
- ❌ Нет rate limiting

### TODO для продакшена:
```python
# 1. Ограничение размера файлов
@app.post("/api/upload")
async def upload(file: UploadFile = File(..., max_size=10_000_000)):  # 10MB
    pass

# 2. Валидация типов файлов
ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
    raise HTTPException(400, "Invalid file type")

# 3. Rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/sbom-migrate")
@limiter.limit("10/minute")
async def sbom_migrate():
    pass
```

---

## 📝 Changelog детали

### v1.0.0 (18.10.2025)

**Commits (логическая последовательность):**

1. `fix: Update pandas version for Python 3.13 compatibility`
   - Файл: `backend/requirements.txt`
   - Изменение: `pandas==2.1.4` → `pandas>=2.2.0`

2. `feat: Create SBOMMigrate component`
   - Файл: `frontend/src/components/SBOMMigrate.js`
   - Добавлен полноценный React компонент

3. `style: Add CSS styles for tool components`
   - Файл: `frontend/src/App.css`
   - Добавлено ~230 строк CSS

4. `refactor: Rename SBOM Tools to DevSecOps Tools`
   - Файлы: `App.js`, `main.py`, `index.html`, `package.json`
   - Глобальное переименование

5. `refactor: Rename SBOM Migrate to Vulnerability Comments Transfer`
   - Файлы: `App.js`, `SBOMMigrate.js`
   - Более точное название функции

6. `feat: Add GitLeaks and VEX Converter tool cards`
   - Файл: `App.js`
   - Добавлены новые инструменты в Coming Soon

7. `docs: Add project documentation`
   - Файлы: `PROJECT_STATUS.md`, `TECHNICAL_NOTES.md`
   - Полная документация проекта

---

## 💻 Команды для разработки

### Git (если используется):
```bash
# Инициализация репозитория
git init
git add .
git commit -m "Initial commit: DevSecOps Tools v1.0.0"

# Создание .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
```

### Форматирование кода:
```bash
# Python (black)
pip install black
black backend/app/

# JavaScript (prettier)
npm install --save-dev prettier
npx prettier --write "frontend/src/**/*.{js,jsx,css}"
```

### Линтеры:
```bash
# Python (flake8)
pip install flake8
flake8 backend/app/

# JavaScript (eslint)
npm install --save-dev eslint
npx eslint frontend/src/
```

---

## 🎯 Следующие шаги разработки

### Краткосрочные (1-2 недели):
1. Добавить unit тесты
2. Реализовать превью данных перед миграцией
3. Добавить drag-and-drop для файлов
4. Улучшить обработку ошибок

### Среднесрочные (1 месяц):
1. Начать разработку GitLeaks Scanner
2. Реализовать VEX Converter
3. Добавить базу данных (PostgreSQL/SQLite)
4. Реализовать аутентификацию

### Долгосрочные (3+ месяца):
1. Реализовать все инструменты
2. Добавить API для CI/CD интеграции
3. Создать мобильное приложение
4. Развернуть в облаке (AWS/Azure/GCP)

---

**Автор:** Claude AI + Sergey Bakunin
**Последнее обновление:** 18.10.2025
