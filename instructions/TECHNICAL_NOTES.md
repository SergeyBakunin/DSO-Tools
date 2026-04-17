# Технические заметки — DevSecOps Tools

**Версия:** 1.6.6
**Дата обновления:** 07 апреля 2026

---

## 🏗️ Архитектура

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

**Важно:** Все API запросы из браузера идут через nginx (`/api → http://backend:8000`).
В React компонентах: `API_URL = process.env.REACT_APP_API_URL || ''` — пустая строка означает относительный URL, nginx сам проксирует.

---

## 🔧 Решённые технические проблемы

### 1. RemoteProtocolError в history endpoint (CodeScoring)

**Проблема:** `httpcore.RemoteProtocolError: Server disconnected without sending a response`

**Причина:** httpcore/httpx кешируют TLS-сессию. В контексте uvicorn повторное использование сессии приводило к обрыву соединения с CodeScoring.

**Решение:** Заменили async httpx на sync stdlib `urllib.request` с созданием нового SSL контекста для каждого запроса. Вызов через `loop.run_in_executor()` чтобы не блокировать event loop.

```python
def _fetch_all_analyses_sync(project_id, cfg, target_date_iso=None):
    import urllib.request, ssl, json as _json
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    # ... полная реализация в vulnerability_report.py

async def _fetch_all_analyses(project_id, cfg, target_date_iso=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_all_analyses_sync, project_id, cfg, target_date_iso)
```

**Файл:** `backend/app/vulnerability_report.py`

---

### 2. exec format error на VDI (x86_64)

**Проблема:** `exec /usr/local/bin/python3: exec format error` при запуске образов на Ubuntu x86_64 VDI.

**Причина:** Сборка на Windows ARM64 давала arm64 образы по умолчанию. Docker кешировал архитектуру даже при указании `--platform`.

**Решение:** Использовать `buildx --push` (минует локальный кеш, сразу пушит в реджестри под нужную платформу):

```bash
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.6 ./backend
```

**Правило:** Никогда не собирать без `--platform linux/amd64` на ARM-хосте.

---

### 3. API_URL в Docker (VEX Converter, VEX Validator)

**Проблема:** POST запросы из VEXConverter не доходили до backend в Docker.

**Причина:** `API_URL = '...' || 'http://localhost:8000'` — внутри Docker `localhost` указывает на frontend контейнер, а не backend.

**Решение:** Изменить fallback на пустую строку `''`:

```javascript
const API_URL = process.env.REACT_APP_API_URL || '';
```

Относительные URL (`/api/...`) проксируются nginx на `http://backend:8000`.

**Файлы:** `frontend/src/components/VEXConverter.js`, `VEXValidator.js`

---

### 4. Недопустимое значение justification в VEX

**Проблема:** VEX Converter генерировал `"justification": "component_not_present"` — значение отсутствует в CycloneDX 1.6.

**Решение:** Убрали justification из дефолтного analysis, заменили на минимально допустимый вариант:

```python
# Было:
default_analysis = {"state": "in_triage", "justification": "component_not_present"}

# Стало:
default_analysis = {"state": "in_triage"}
```

**Допустимые state (CycloneDX 1.6):** `in_triage`, `affected`, `not_affected`, `exploitable`, `false_positive`, `resolved`

**Файл:** `backend/app/main.py`

---

### 5. Pandas + Python 3.13

**Проблема:** `pandas==2.1.4` не имел wheels для Python 3.13.

**Решение:** `pandas>=2.2.0` в `requirements.txt`.

---

## 🐳 Docker

### Сборка образов (с ARM-хоста Windows)

```bash
# Обязательно --platform linux/amd64 и --push
docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-backend:1.6.6 ./backend

docker buildx build --platform linux/amd64 --push \
  -t sergeybakunin/devsecops-tools-frontend:1.6.6 ./frontend
```

### Запуск на сервере (без исходников)

```bash
docker compose up -d --no-build
```

Флаг `--no-build` обязателен: на сервере нет исходников, `docker compose` не должен пытаться собирать образы из `build: context:`.

### Образы

| Образ | Описание |
|---|---|
| `sergeybakunin/devsecops-tools-backend:1.6.6` | FastAPI + Python 3.13 |
| `sergeybakunin/devsecops-tools-frontend:1.6.6` | React + Nginx |

### config.yaml

Конфиг backend монтируется через volume:

```yaml
volumes:
  - ./backend/config.yaml:/app/config.yaml:ro
```

```yaml
artifactory:
  url: https://artifactory.example.com
  username: user
  password: token

codescoring:
  url: https://codescoring.example.com
  api_key: your-api-key
```

---

## 📦 Зависимости

### Backend (Python 3.13):

```
fastapi          — Web framework
uvicorn          — ASGI server
python-multipart — File upload
pandas>=2.2.0    — Data processing (XLSX)
openpyxl==3.1.2  — Excel read/write
xlsxwriter==3.1.9 — Excel write (альтернатива)
pyyaml           — config.yaml parsing
```

### Frontend (React 18.2):

```
react: ^18.2.0
react-dom: ^18.2.0
axios: ^1.x
react-scripts: 5.0.1
```

---

## 🔐 Безопасность (текущее состояние)

- ❌ CORS открыт (`allow_origins=["*"]`) — для внутренней сети допустимо
- ❌ Нет аутентификации
- ❌ Нет ограничения размера файлов
- ✅ Используется для внутренней инфраструктуры

---

## 📝 Структура API

Все endpoints в `backend/app/main.py` и `backend/app/vulnerability_report.py`.

Полная документация: **http://localhost:8000/docs** (Swagger UI после запуска).

---

**Автор:** Sergey Bakunin
**Последнее обновление:** 07 апреля 2026
