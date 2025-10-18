# Инструкция по загрузке проекта на GitHub через VS Code

## ✅ Подготовка завершена

Git репозиторий инициализирован и готов к загрузке на GitHub!

**Информация:**
- ✅ Git репозиторий инициализирован
- ✅ Создан .gitignore (исключает node_modules, __pycache__, .env и др.)
- ✅ Создан .gitattributes (нормализация переводов строк)
- ✅ Сделан первый commit (30 файлов, 4996 строк)
- ✅ Commit ID: `54eea35`
- ✅ Ветка: `master`

---

## 📤 Загрузка на GitHub через VS Code

### Вариант 1: Через встроенный интерфейс VS Code (рекомендуется)

#### Шаг 1: Откройте панель Source Control
1. Нажмите на иконку "Source Control" в левой панели VS Code (или `Ctrl+Shift+G`)
2. Вы должны увидеть надпись "master" и "1 commit"

#### Шаг 2: Publish to GitHub
1. Нажмите на кнопку **"Publish to GitHub"** (три точки → Publish to GitHub)
2. VS Code предложит выбрать тип репозитория:
   - **Public** - публичный репозиторий (доступен всем)
   - **Private** - приватный репозиторий (доступен только вам)
3. Выберите нужный тип и нажмите "OK"

#### Шаг 3: Выберите имя репозитория
- VS Code предложит имя: `sbom-tools`
- Можете изменить или оставить как есть
- Нажмите "Enter"

#### Шаг 4: Выберите файлы для загрузки
- VS Code покажет список файлов
- **Оставьте все файлы отмеченными**
- Нажмите "OK"

#### Шаг 5: Авторизация (если требуется)
- Если это первая загрузка, VS Code попросит авторизоваться в GitHub
- Нажмите "Allow" и войдите в ваш GitHub аккаунт
- Разрешите VS Code доступ к GitHub

#### Шаг 6: Готово!
- VS Code автоматически создаст репозиторий и загрузит все файлы
- В правом нижнем углу появится уведомление с ссылкой на репозиторий
- Нажмите на ссылку, чтобы открыть репозиторий в браузере

---

### Вариант 2: Через командную строку Git (альтернативный)

Если предпочитаете командную строку:

```bash
# 1. Создайте репозиторий на GitHub.com вручную
#    Название: sbom-tools
#    НЕ инициализируйте с README, .gitignore или лицензией

# 2. Добавьте remote origin
git remote add origin https://github.com/YOUR_USERNAME/sbom-tools.git

# 3. Переименуйте ветку в main (если хотите)
git branch -M main

# 4. Загрузите код на GitHub
git push -u origin main
```

**Замените `YOUR_USERNAME`** на ваш GitHub username!

---

## 📋 Рекомендуемые настройки репозитория на GitHub

После загрузки рекомендую настроить:

### 1. Description (описание репозитория)
```
DevSecOps Tools - Набор инструментов для работы с SBOM и управления уязвимостями
```

### 2. Topics (теги)
Добавьте теги для лучшей видимости:
- `devsecops`
- `sbom`
- `vex`
- `cyclonedx`
- `vulnerability-management`
- `fastapi`
- `react`
- `python`
- `security-tools`

### 3. About
- ✅ Website: (можете добавить ссылку на документацию)
- ✅ Include in the home page: ✓

### 4. GitHub Pages (опционально)
Можете настроить GitHub Pages для документации:
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /docs (или создайте отдельную ветку gh-pages)

---

## 🎯 Что будет загружено

### Backend
- `backend/app/main.py` - FastAPI приложение
- `backend/requirements.txt` - Python зависимости
- `backend/Dockerfile` - Docker образ

### Frontend
- `frontend/src/` - React компоненты
- `frontend/public/` - Статические файлы
- `frontend/package.json` - Node.js зависимости

### Документация
- `README.md` - Главная документация
- `VEX_CONVERTER_README.md` - Документация VEX конвертера
- `VEX_QUICK_START.md` - Быстрый старт VEX
- `VEX_IMPLEMENTATION_SUMMARY.md` - Детали реализации
- `VERIFICATION_REPORT.md` - Отчёт о проверке
- `PROJECT_STATUS.md` - Статус проекта
- `TECHNICAL_NOTES.md` - Технические заметки
- `QUICK_START.md` - Быстрый старт
- `CHANGELOG.md` - История изменений
- `DOCS_INDEX.md` - Индекс документации

### Тесты
- `test_vex_converter.py` - Базовый тест
- `compare_sbom_vex.py` - Сравнение SBOM vs VEX
- `test_large_sbom.py` - Нагрузочный тест

### Скрипты
- `start-backend.bat` - Запуск backend (Windows)
- `start-frontend.bat` - Запуск frontend (Windows)

### Конфигурация
- `.gitignore` - Исключения для Git
- `.gitattributes` - Настройки переводов строк

---

## 🚫 Что НЕ будет загружено (благодаря .gitignore)

- ❌ `node_modules/` - зависимости Node.js
- ❌ `__pycache__/` - кэш Python
- ❌ `.env` - файлы с секретами
- ❌ `venv/` - виртуальное окружение Python
- ❌ `test_vex_output.json` - тестовые файлы
- ❌ `.vscode/` - локальные настройки VS Code

---

## 📝 Рекомендуемые действия после загрузки

### 1. Создайте Release
Создайте первый релиз v1.0.0:
1. Перейдите в Releases на GitHub
2. Нажмите "Create a new release"
3. Tag: `v1.0.0`
4. Title: `DevSecOps Tools v1.0.0 - Initial Release`
5. Description: Скопируйте из CHANGELOG.md
6. Нажмите "Publish release"

### 2. Настройте Issues
Создайте шаблоны для Issues:
- Bug report
- Feature request
- Question

### 3. Добавьте LICENSE
Выберите лицензию:
1. Add file → Create new file
2. Имя: `LICENSE`
3. GitHub предложит шаблоны (например, MIT)

### 4. Настройте GitHub Actions (опционально)
Можете добавить CI/CD для автоматического тестирования

---

## 🎉 Поздравляю!

После загрузки ваш репозиторий будет доступен по адресу:
```
https://github.com/YOUR_USERNAME/sbom-tools
```

### Что дальше?

1. ⭐ Поставьте звезду своему репозиторию
2. 📢 Поделитесь с коллегами
3. 📝 Напишите статью/пост о проекте
4. 🔄 Продолжайте развивать функциональность
5. 📚 Добавляйте примеры использования

---

## 💡 Полезные команды Git

```bash
# Проверить статус
git status

# Посмотреть историю
git log --oneline

# Посмотреть remote
git remote -v

# Обновить remote репозиторий
git push

# Создать новую ветку
git checkout -b feature/new-feature

# Переключиться на другую ветку
git checkout master
```

---

## 🆘 Проблемы?

### Проблема: VS Code не показывает кнопку "Publish to GitHub"
**Решение:**
1. Установите расширение "GitHub Pull Requests and Issues"
2. Перезапустите VS Code
3. Войдите в GitHub через VS Code

### Проблема: Ошибка авторизации
**Решение:**
1. VS Code → Settings → Extensions → GitHub
2. Sign out
3. Sign in снова

### Проблема: Repository already exists
**Решение:**
1. Используйте другое имя репозитория
2. ИЛИ удалите существующий репозиторий на GitHub

---

**Дата создания:** 18 октября 2025
**Версия проекта:** 1.0.0
**Автор:** Sergey Bakunin (при поддержке Claude AI)

Made with ❤️ using FastAPI, React, and Claude AI
