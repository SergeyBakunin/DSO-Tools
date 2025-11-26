@echo off
REM =============================================================================
REM DevSecOps Tools - Quick Start Script
REM =============================================================================

echo.
echo ========================================================================
echo  DevSecOps Tools - Quick Start
echo ========================================================================
echo.

REM Check if Docker is available
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Docker found! Using Docker deployment...
    echo.

    REM Check if Docker is running
    docker ps >nul 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Docker is running
        echo.

        REM Start application
        cd docker
        echo [START] Starting DevSecOps Tools with Docker Compose...
        docker-compose up -d

        if %errorlevel% equ 0 (
            echo.
            echo ========================================================================
            echo  SUCCESS! Application is starting...
            echo ========================================================================
            echo.
            echo  Frontend: http://localhost:3000
            echo  Backend:  http://localhost:8000
            echo  API Docs: http://localhost:8000/docs
            echo.

            REM Get local IP
            echo  For access from local network, use your IP address:
            for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
                echo    - http://%%a:3000
            )
            echo.
            echo  To view logs: cd docker ^&^& docker-compose logs -f
            echo  To stop:      cd docker ^&^& docker-compose down
            echo ========================================================================
            echo.

            REM Ask to open browser
            choice /C YN /M "Open browser now"
            if %errorlevel% equ 1 (
                start http://localhost:3000
            )
        ) else (
            echo.
            echo [ERROR] Failed to start Docker containers
            echo [HINT] Try: docker-compose down ^&^& docker-compose up -d --build
        )

        cd ..
    ) else (
        echo [ERROR] Docker is not running!
        echo [ACTION] Please start Docker Desktop and try again
        echo.
        pause
        exit /b 1
    )
) else (
    echo [WARNING] Docker not found!
    echo.
    echo [INFO] Starting in Windows native mode...
    echo.

    REM Check Python
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found! Please install Python first.
        pause
        exit /b 1
    )

    REM Check Node.js
    where node >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Node.js not found! Please install Node.js first.
        pause
        exit /b 1
    )

    echo [INFO] Starting backend and frontend in separate windows...
    echo.

    REM Start backend in new window
    start "DevSecOps Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

    REM Wait a bit
    timeout /t 3 /nobreak >nul

    REM Start frontend in new window
    start "DevSecOps Frontend" cmd /k "cd frontend && serve -s build -l 3000"

    echo [OK] Backend and frontend started in separate windows
    echo.
    echo ========================================================================
    echo  Frontend: http://localhost:3000
    echo  Backend:  http://localhost:8000
    echo ========================================================================
    echo.

    timeout /t 3 /nobreak >nul
    start http://localhost:3000
)

pause
