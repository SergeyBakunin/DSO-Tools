#!/bin/bash
# Быстрое исправление для запуска на Synology NAS
# Использует упрощенную версию docker-compose БЕЗ CPU лимитов

echo "=== DevSecOps Tools - Быстрое развертывание на NAS ==="
echo ""

# Переходим в директорию nas-deployment
cd /volume1/docker/devsecops/nas-deployment

echo "1. Копируем упрощенный docker-compose..."
sudo cp docker-compose.nas-simple.yml /volume1/docker/devsecops/project/docker-compose.nas.yml

echo "2. Останавливаем старые контейнеры (если есть)..."
cd /volume1/docker/devsecops/project
sudo docker-compose -f docker-compose.nas.yml down 2>/dev/null || true

echo "3. Удаляем старую сеть (если есть)..."
sudo docker network rm devsecops-network 2>/dev/null || true

echo "4. Запускаем контейнеры..."
sudo docker-compose -f docker-compose.nas.yml up -d

echo ""
echo "=== Проверка ==="
sleep 3
sudo docker ps

echo ""
echo "=== Готово! ==="
echo "Frontend: https://dso.deone37.synology.me/"
echo "Backend API: https://dso.deone37.synology.me/docs"
echo ""
echo "Проверить логи:"
echo "  sudo docker logs devsecops-backend"
echo "  sudo docker logs devsecops-frontend"
