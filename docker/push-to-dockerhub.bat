@echo off
echo ================================================
echo DevSecOps Tools - Push to Docker Hub
echo ================================================
echo.

echo Step 1: Login to Docker Hub...
docker login
if %errorlevel% neq 0 (
    echo ERROR: Docker login failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Tagging backend images...
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:1.0.0
docker tag devsecops-tools-backend:1.0.0 deone37/devsecops-backend:latest

echo Step 3: Tagging frontend images...
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:1.0.0
docker tag devsecops-tools-frontend:1.0.0 deone37/devsecops-frontend:latest

echo.
echo Step 4: Pushing backend to Docker Hub...
docker push deone37/devsecops-backend:1.0.0
docker push deone37/devsecops-backend:latest

echo.
echo Step 5: Pushing frontend to Docker Hub...
docker push deone37/devsecops-frontend:1.0.0
docker push deone37/devsecops-frontend:latest

echo.
echo ================================================
echo SUCCESS! Images published to Docker Hub
echo ================================================
echo.
echo Backend: https://hub.docker.com/r/deone37/devsecops-backend
echo Frontend: https://hub.docker.com/r/deone37/devsecops-frontend
echo.
echo Pull on NAS with:
echo   docker pull deone37/devsecops-backend:latest
echo   docker pull deone37/devsecops-frontend:latest
echo.
pause
