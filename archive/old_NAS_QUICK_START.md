# NAS - Быстрый старт

## 🚀 Развертывание за 5 минут

### Для Synology NAS

#### 1. Загрузите проект на NAS

```bash
# Подключитесь к NAS через SSH
ssh admin@your-nas-ip

# Создайте директорию и клонируйте проект
sudo mkdir -p /volume1/docker/devsecops/project
cd /volume1/docker/devsecops/project
sudo git clone https://github.com/YOUR_USERNAME/sbom-tools.git .
```

**ИЛИ** загрузите файлы через **File Station** в `/docker/devsecops/project`

#### 2. Настройте переменные окружения

```bash
# Скопируйте example файл
sudo cp .env.nas.example .env

# Отредактируйте .env
sudo nano .env
```

**Измените:**
```bash
NAS_IP=192.168.1.100  # IP вашего NAS
```

#### 3. Запустите контейнеры

```bash
# Сборка и запуск
sudo docker-compose -f docker-compose.nas.yml up -d
```

#### 4. Готово!

Откройте в браузере:
- 🌐 **Frontend:** http://192.168.1.100:3000
- 🔧 **Backend:** http://192.168.1.100:8000

---

### Для QNAP NAS

#### 1. Загрузите проект на NAS

```bash
# Подключитесь к NAS через SSH
ssh admin@your-nas-ip

# Создайте директорию и клонируйте проект
mkdir -p /share/Container/devsecops/project
cd /share/Container/devsecops/project
git clone https://github.com/YOUR_USERNAME/sbom-tools.git .
```

**ИЛИ** загрузите файлы через **File Browser** в `/Container/devsecops/project`

#### 2. Настройте переменные окружения

```bash
# Скопируйте example файл
cp .env.nas.example .env

# Отредактируйте .env
nano .env
```

**Измените:**
```bash
NAS_IP=192.168.1.100  # IP вашего NAS
```

#### 3. Запустите контейнеры

```bash
# Сборка и запуск
docker-compose -f docker-compose.nas.yml up -d
```

#### 4. Готово!

Откройте в браузере:
- 🌐 **Frontend:** http://192.168.1.100:3000
- 🔧 **Backend:** http://192.168.1.100:8000

---

## 📊 Проверка статуса

```bash
# Synology
sudo docker ps | grep devsecops

# QNAP
docker ps | grep devsecops
```

**Ожидаемый результат:**
```
devsecops-backend    Up    0.0.0.0:8000->8000/tcp
devsecops-frontend   Up    0.0.0.0:3000->80/tcp
```

---

## 📝 Просмотр логов

```bash
# Synology
sudo docker logs -f devsecops-backend

# QNAP
docker logs -f devsecops-backend
```

---

## 🛑 Остановка

```bash
# Synology
cd /volume1/docker/devsecops/project
sudo docker-compose -f docker-compose.nas.yml down

# QNAP
cd /share/Container/devsecops/project
docker-compose -f docker-compose.nas.yml down
```

---

## 🔄 Обновление

```bash
# Synology
cd /volume1/docker/devsecops/project
sudo git pull
sudo docker-compose -f docker-compose.nas.yml build
sudo docker-compose -f docker-compose.nas.yml up -d

# QNAP
cd /share/Container/devsecops/project
git pull
docker-compose -f docker-compose.nas.yml build
docker-compose -f docker-compose.nas.yml up -d
```

---

## ⚙️ Основные настройки

### Изменить порты

Отредактируйте `docker-compose.nas.yml`:
```yaml
ports:
  - "8080:8000"  # Backend на порту 8080
  - "8090:80"    # Frontend на порту 8090
```

### Ограничить ресурсы

Отредактируйте `docker-compose.nas.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'   # Уменьшить до 0.5 CPU
      memory: 256M  # Уменьшить до 256MB
```

---

## ⚠️ Возможные проблемы

### Ошибка: Permission denied

**Решение:**
```bash
# Synology
sudo chmod -R 755 /volume1/docker/devsecops
sudo chown -R 1000:1000 /volume1/docker/devsecops

# QNAP
chmod -R 755 /share/Container/devsecops
chown -R 1000:1000 /share/Container/devsecops
```

### Ошибка: Port already in use

**Решение:** Измените порты в `docker-compose.nas.yml`

### Ошибка: Not enough memory

**Решение:** Уменьшите лимиты памяти в `docker-compose.nas.yml`

---

## 📖 Подробная документация

См. [NAS_DEPLOYMENT_GUIDE.md](NAS_DEPLOYMENT_GUIDE.md) для детальных инструкций

---

**Готово! Приложение работает на вашем NAS!** 🎉
