#!/bin/bash
# Скрипт обновления DevSecOps Tools с Docker Hub
# Выполняется на Synology NAS

echo "=========================================="
echo "DevSecOps Tools - Обновление с Docker Hub"
echo "=========================================="
echo ""

PROJECT_DIR="/volume1/docker/devsecops/project"

echo "1. Переходим в директорию проекта..."
cd "$PROJECT_DIR" || exit 1

echo "2. Останавливаем контейнеры..."
sudo docker-compose -f docker-compose.dockerhub.yml down

echo "3. Скачиваем обновленные образы с Docker Hub..."
sudo docker pull deone37/devsecops-backend:latest
sudo docker pull deone37/devsecops-frontend:latest

echo "4. Запускаем контейнеры с новыми образами..."
sudo docker-compose -f docker-compose.dockerhub.yml up -d

echo ""
echo "5. Проверяем статус..."
sleep 3
sudo docker ps | grep devsecops

echo ""
echo "=========================================="
echo "✅ Обновление завершено!"
echo "=========================================="
echo ""
echo "Проверьте логи:"
echo "  sudo docker logs devsecops-backend"
echo "  sudo docker logs devsecops-frontend"
echo ""
echo "Откройте: https://dso.deone37.synology.me/"
echo ""
