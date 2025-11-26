# Руководство по развертыванию DevSecOps Tools

Инструкции по развертыванию приложения на ноутбуке с доступом из локальной сети.

---

## Вариант 1: Docker (Рекомендуется) ⭐

**Преимущества:**
- Простое развертывание одной командой
- Изолированная среда
- Автоматический перезапуск
- Работает одинаково на Windows и WSL

### Шаг 1: Запуск приложения

```bash
# Переходим в директорию проекта
cd "C:\Users\Sergey Bakunin\sbom-tools\docker"

# Запускаем приложение
docker-compose up -d
```

### Шаг 2: Проверка статуса

```bash
# Проверяем, что контейнеры запущены
docker-compose ps

# Смотрим логи (если нужно)
docker-compose logs -f
```

### Шаг 3: Доступ к приложению

После запуска приложение доступно по адресам:

- **Frontend (UI):** http://localhost:3000
- **Backend (API):** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Шаг 4: Доступ из локальной сети

Узнайте IP-адрес вашего ноутбука:

```bash
# В Windows PowerShell
ipconfig

# Ищите строку "IPv4 Address" для вашей Wi-Fi или Ethernet адаптера
# Например: 192.168.1.100
```

Теперь другие устройства в локальной сети могут открыть:
- Frontend: `http://192.168.1.100:3000`
- API: `http://192.168.1.100:8000`

### Управление приложением

```bash
# Остановить приложение
docker-compose down

# Перезапустить приложение
docker-compose restart

# Обновить после изменений в коде
docker-compose down
docker-compose up -d --build

# Посмотреть логи
docker-compose logs backend
docker-compose logs frontend
```

### Автозапуск при загрузке Windows

Контейнеры настроены с `restart: unless-stopped`, поэтому:
- Docker Desktop должен автоматически стартовать при загрузке Windows
- Контейнеры автоматически запустятся вместе с Docker

**Проверьте настройки Docker Desktop:**
1. Откройте Docker Desktop
2. Settings → General
3. Включите "Start Docker Desktop when you log in"

---

## Вариант 2: WSL2 (Ubuntu)

### Подготовка WSL

```bash
# Запускаем WSL Ubuntu
wsl -d Ubuntu

# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv nodejs npm
```

### Установка приложения в WSL

```bash
# Переходим в директорию проекта (из Windows)
cd /mnt/c/Users/Sergey\ Bakunin/sbom-tools

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend (в новом окне терминала)
cd /mnt/c/Users/Sergey\ Bakunin/sbom-tools/frontend
npm install
npm run build
npm install -g serve  # Для раздачи статики
```

### Запуск в WSL

**Backend (терминал 1):**
```bash
cd /mnt/c/Users/Sergey\ Bakunin/sbom-tools/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend (терминал 2):**
```bash
cd /mnt/c/Users/Sergey\ Bakunin/sbom-tools/frontend
serve -s build -l 3000
```

### Доступ из локальной сети

Узнайте IP-адрес WSL:
```bash
ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1
```

Или используйте IP Windows-хоста (см. Вариант 1, Шаг 4).

### Создание systemd сервисов (автозапуск)

Создайте файлы сервисов в WSL:

**Backend service:**
```bash
sudo nano /etc/systemd/system/devsecops-backend.service
```

```ini
[Unit]
Description=DevSecOps Tools Backend
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/mnt/c/Users/Sergey Bakunin/sbom-tools/backend
Environment="PATH=/mnt/c/Users/Sergey Bakunin/sbom-tools/backend/venv/bin"
ExecStart=/mnt/c/Users/Sergey Bakunin/sbom-tools/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend service:**
```bash
sudo nano /etc/systemd/system/devsecops-frontend.service
```

```ini
[Unit]
Description=DevSecOps Tools Frontend
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/mnt/c/Users/Sergey Bakunin/sbom-tools/frontend
ExecStart=/usr/local/bin/serve -s build -l 3000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Активация сервисов:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable devsecops-backend
sudo systemctl enable devsecops-frontend
sudo systemctl start devsecops-backend
sudo systemctl start devsecops-frontend

# Проверка статуса
sudo systemctl status devsecops-backend
sudo systemctl status devsecops-frontend
```

---

## Вариант 3: Windows Native

### Подготовка

```powershell
# Установите Python (если еще не установлен)
# Скачайте с https://www.python.org/downloads/

# Установите Node.js (если еще не установлен)
# Скачайте с https://nodejs.org/
```

### Установка зависимостей

**Backend:**
```powershell
cd "C:\Users\Sergey Bakunin\sbom-tools\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd "C:\Users\Sergey Bakunin\sbom-tools\frontend"
npm install
npm run build
npm install -g serve
```

### Запуск приложения

**Backend (PowerShell окно 1):**
```powershell
cd "C:\Users\Sergey Bakunin\sbom-tools\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend (PowerShell окно 2):**
```powershell
cd "C:\Users\Sergey Bakunin\sbom-tools\frontend"
serve -s build -l 3000
```

### Автозапуск через Windows Task Scheduler

1. Откройте Task Scheduler (Планировщик заданий)
2. Создайте новую задачу: Actions → Create Task

**Backend задача:**
- Name: DevSecOps Backend
- Trigger: At log on
- Action: Start a program
  - Program: `C:\Users\Sergey Bakunin\sbom-tools\backend\venv\Scripts\python.exe`
  - Arguments: `-m uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Start in: `C:\Users\Sergey Bakunin\sbom-tools\backend`

**Frontend задача:**
- Name: DevSecOps Frontend
- Trigger: At log on
- Action: Start a program
  - Program: `C:\Program Files\nodejs\node.exe`
  - Arguments: `C:\Users\Sergey Bakunin\AppData\Roaming\npm\node_modules\serve\bin\serve.js -s build -l 3000`
  - Start in: `C:\Users\Sergey Bakunin\sbom-tools\frontend`

### Создание bat-файлов для быстрого запуска

**start-backend.bat:**
```batch
@echo off
cd "C:\Users\Sergey Bakunin\sbom-tools\backend"
call venv\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
```

**start-frontend.bat:**
```batch
@echo off
cd "C:\Users\Sergey Bakunin\sbom-tools\frontend"
serve -s build -l 3000
pause
```

---

## Настройка Firewall (для доступа из локальной сети)

### Windows Firewall

```powershell
# Разрешите порты 3000 и 8000 в Windows Firewall
New-NetFirewallRule -DisplayName "DevSecOps Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "DevSecOps Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Или через GUI:
1. Windows Security → Firewall & network protection
2. Advanced settings → Inbound Rules → New Rule
3. Port → TCP → Specific local ports: 3000, 8000
4. Allow the connection

---

## Проверка доступности

### Локальная проверка

```bash
# Frontend
curl http://localhost:3000

# Backend
curl http://localhost:8000

# API Docs
# Откройте в браузере: http://localhost:8000/docs
```

### Проверка из локальной сети

С другого устройства в сети:
```bash
# Замените 192.168.1.100 на IP вашего ноутбука
curl http://192.168.1.100:3000
curl http://192.168.1.100:8000
```

---

## Рекомендации

### Для постоянного использования:
1. **Домашняя сеть:** Docker (Вариант 1) - самый простой и надежный
2. **Рабочее окружение:** WSL2 с systemd (Вариант 2) - более гибкий контроль

### Для разработки:
- Windows Native (Вариант 3) - прямой доступ к файлам, быстрая перезагрузка

### Безопасность:
- Приложение доступно только в локальной сети
- Для доступа из интернета используйте VPN или настройте reverse proxy с SSL (nginx/Caddy)
- Не открывайте порты на роутере без HTTPS и авторизации

---

## Быстрый старт (для нетерпеливых)

```bash
# Самый простой способ - Docker
cd "C:\Users\Sergey Bakunin\sbom-tools\docker"
docker-compose up -d

# Откройте в браузере
# http://localhost:3000
```

**Готово!** 🚀

---

## Troubleshooting

### Docker не запускается
```bash
# Проверьте Docker Desktop
docker --version
docker ps

# Перезапустите Docker Desktop
# или
wsl --shutdown
# и запустите Docker Desktop снова
```

### Порт уже занят
```bash
# Найдите процесс, занимающий порт
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Остановите процесс по PID
taskkill /F /PID <PID>
```

### Frontend не подключается к Backend
- Проверьте, что оба сервиса запущены
- Проверьте URL в настройках frontend (должен быть `/api` для Docker)
- Проверьте логи: `docker-compose logs backend`

### Не могу подключиться из сети
- Проверьте IP-адрес ноутбука
- Проверьте Windows Firewall (см. раздел Firewall)
- Убедитесь, что приложение слушает `0.0.0.0`, а не `127.0.0.1`

---

## Обновление приложения после изменений

### Docker:
```bash
cd "C:\Users\Sergey Bakunin\sbom-tools\docker"
docker-compose down
docker-compose up -d --build
```

### WSL/Windows:
```bash
# Перезапустите сервисы
# или просто Ctrl+C в терминале и запустите снова
```
