@echo off
title InsureBridge — Frontend (React + Vite)
color 0B
echo.
echo  ========================================
echo   InsureBridge Frontend (React + Vite)
echo   http://localhost:5173
echo  ========================================
echo.

cd /d "%~dp0frontend"

:: Install node modules if missing
if not exist "node_modules" (
    echo [INFO] node_modules not found. Running npm install...
    npm install
    echo.
)

:: Start Vite dev server
echo [INFO] Starting Vite dev server on http://localhost:5173 ...
echo [INFO] Press Ctrl+C to stop.
echo.
npm run dev

pause
