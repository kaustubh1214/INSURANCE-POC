@echo off
title InsureBridge — Launcher
echo.
echo  ========================================
echo   InsureBridge — Starting All Services
echo  ========================================
echo.
echo  [1/2] Launching Backend in new window...
start "InsureBridge Backend" cmd /k "cd /d "%~dp0" && start-backend.bat"

echo  Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

echo  [2/2] Launching Frontend in new window...
start "InsureBridge Frontend" cmd /k "cd /d "%~dp0" && start-frontend.bat"

echo.
echo  ========================================
echo   Both services are starting up!
echo.
echo   Backend  →  http://localhost:8000
echo   API Docs →  http://localhost:8000/docs
echo   Frontend →  http://localhost:5173
echo  ========================================
echo.
echo  Opening frontend in browser in 10 seconds...
timeout /t 10 /nobreak > nul
start http://localhost:5173

echo  Done! Close this window.
pause
