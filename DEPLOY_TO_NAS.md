# Развертывание на Synology NAS - Пошаговая инструкция

## Проблема
Container Manager на NAS не может найти образы `devsecops-tools-backend:1.0.0` и `devsecops-tools-frontend:1.0.0`, потому что они существуют только локально на вашем компьютере.

## Решение: Экспорт и импорт образов

### Вариант 1: Через Docker Hub (рекомендуется для будущих обновлений)

#### Шаг 1: Залогиньтесь в Docker Hub
```bash
docker login
```
Введите ваш Docker Hub username и password.

#### Шаг 2: Тегируйте образы с вашим username
```bash
# Замените YOUR_USERNAME на ваш Docker Hub username
docker tag devsecops-tools-backend:1.0.0 YOUR_USERNAME/devsecops-backend:1.0.0
docker tag devsecops-tools-frontend:1.0.0 YOUR_USERNAME/devsecops-frontend:1.0.0
```

#### Шаг 3: Загрузите образы на Docker Hub
```bash
docker push YOUR_USERNAME/devsecops-backend:1.0.0
docker push YOUR_USERNAME/devsecops-frontend:1.0.0
```

#### Шаг 4: Обновите docker-compose.nas.yml
Измените строки с `image:` на:
```yaml
services:
  backend:
    image: YOUR_USERNAME/devsecops-backend:1.0.0

  frontend:
    image: YOUR_USERNAME/devsecops-frontend:1.0.0
```

#### Шаг 5: На NAS образы скачаются автоматически
Container Manager сам скачает образы из Docker Hub при запуске.

---

### Вариант 2: Прямой экспорт/импорт (быстрее, но только один раз)

#### Шаг 1: Экспортируйте образы в файлы
```bash
docker save devsecops-tools-backend:1.0.0 -o devsecops-backend-1.0.0.tar
docker save devsecops-tools-frontend:1.0.0 -o devsecops-frontend-1.0.0.tar
```

Это создаст два файла:
- `devsecops-backend-1.0.0.tar` (~428 MB)
- `devsecops-frontend-1.0.0.tar` (~81 MB)

#### Шаг 2: Скопируйте файлы на NAS
Используйте один из способов:
- **File Station**: загрузите файлы в `/volume1/docker/devsecops/images/`
- **SMB/CIFS**: скопируйте через сетевую папку
- **SCP**: `scp devsecops-*.tar admin@192.168.0.233:/volume1/docker/devsecops/images/`

#### Шаг 3: Импортируйте образы на NAS через SSH
```bash
# Подключитесь по SSH к NAS
ssh admin@dso.deone37.synology.me

# Перейдите в директорию с образами
cd /volume1/docker/devsecops/images

# Импортируйте образы
docker load -i devsecops-backend-1.0.0.tar
docker load -i devsecops-frontend-1.0.0.tar

# Проверьте, что образы загружены
docker images | grep devsecops
```

Вы должны увидеть:
```
devsecops-tools-backend    1.0.0     1eab67b98a11   428MB
devsecops-tools-frontend   1.0.0     e449498569ff   80.8MB
```

#### Шаг 4: Запустите через Container Manager
Теперь Container Manager найдет образы локально и запустит контейнеры.

---

### Вариант 3: Сборка на NAS (НЕ рекомендуется)

**Почему не рекомендуется:**
- Долгая сборка на NAS (20-40 минут)
- Потребляет ресурсы NAS
- Нагружает процессор

Используйте `docker-compose.yml` с секцией `build:` вместо `docker-compose.nas.yml`.

---

## Рекомендация

**Для первого запуска**: Используйте **Вариант 2** (экспорт/импорт) - это быстрее всего.

**Для будущих обновлений**: Используйте **Вариант 1** (Docker Hub) - просто обновите версию образа и NAS автоматически скачает новую версию.

---

## Проверка развертывания

После импорта образов и запуска контейнеров:

1. Проверьте логи в Container Manager
2. Откройте https://dso.deone37.synology.me/
3. Протестируйте загрузку SBOM файлов

## Структура папок на NAS

```
/volume1/docker/devsecops/
├── project/              # Ваша текущая структура
│   ├── .env             # Переменные окружения
│   └── docker-compose.nas.yml
├── backend-data/        # Данные backend (если нужно)
├── backend-logs/        # Логи backend (если нужно)
└── images/              # Создайте для tar файлов (Вариант 2)
    ├── devsecops-backend-1.0.0.tar
    └── devsecops-frontend-1.0.0.tar
```
