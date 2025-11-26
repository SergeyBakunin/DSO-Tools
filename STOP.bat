@echo off
REM =============================================================================
REM DevSecOps Tools - Stop Script
REM =============================================================================

echo.
echo ========================================================================
echo  DevSecOps Tools - Stop
echo ========================================================================
echo.

REM Check if Docker is available and containers are running
where docker >nul 2>nul
if %errorlevel% equ 0 (
    docker ps >nul 2>nul
    if %errorlevel% equ 0 (
        echo [INFO] Stopping Docker containers...
        cd docker
        docker-compose down

        if %errorlevel% equ 0 (
            echo.
            echo [OK] Docker containers stopped successfully
        ) else (
            echo.
            echo [WARNING] Failed to stop some containers
        )
        cd ..
    )
)

REM Stop Windows processes
echo.
echo [INFO] Stopping Windows processes on ports 3000 and 8000...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>nul
)

echo [OK] Cleanup complete
echo.
echo ========================================================================

pause
