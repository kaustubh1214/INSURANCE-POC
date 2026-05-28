@echo off
title InsureBridge — Backend Server
color 0A
echo.
echo  ========================================
echo   InsureBridge Backend (FastAPI)
echo   http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo  ========================================
echo.

cd /d "%~dp0backend"

:: Create .env from example if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env
    echo [INFO] .env created. Edit it if needed.
    echo.
)

:: Create virtual environment if it doesn't exist
if not exist "venv_linux\Scripts\activate.bat" (
    if not exist "venv\Scripts\activate.bat" (
        echo [INFO] Creating Python virtual environment...
        python -m venv venv
        echo [INFO] Virtual environment created.
        echo.
    )
)

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Could not find venv. Using system Python.
)

:: Install dependencies
echo [INFO] Installing/checking Python dependencies...
pip install -r requirements.txt -q
echo [INFO] Dependencies ready.
echo.

:: Start the server
echo [INFO] Starting FastAPI server on http://localhost:8000 ...
echo [INFO] Press Ctrl+C to stop.
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
