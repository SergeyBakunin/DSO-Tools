# Multi-stage build для оптимизации размера образа

# Stage 1: Build
FROM node:22-alpine AS builder

# Метаданные образа
LABEL maintainer="Sergey Bakunin"
LABEL description="DevSecOps Tools Frontend - React application"
LABEL version="1.0.0"

# Установка рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей (включая dev для сборки)
RUN npm install

# Копирование исходного кода
COPY public ./public
COPY src ./src

# Сборка production версии
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Копирование собранного приложения из builder
COPY --from=builder /app/build /usr/share/nginx/html

# Копирование кастомной конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открытие порта
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]
