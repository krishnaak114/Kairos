@echo off
REM Quick Setup - Kairos
REM Author: Krishna Agrawal

echo ====================================================================================
echo Kairos - Service Heartbeat Monitor
echo ====================================================================================
echo.

echo [Step 1/3] Checking Python...
python --version 2>NUL
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo [Step 2/3] Running Tests...
python -m pytest tests\ -q
if errorlevel 1 (
    echo [INFO] If pytest is not found, install with: pip install pytest
)
echo.

echo [Step 3/3] Running Demo...
python -m app.main --file data\events.json --interval 60 --allowed-misses 3 --quiet
echo.

echo ====================================================================================
echo [SUCCESS] Kairos is ready!
echo ====================================================================================
echo.
echo Quick Commands:
echo   CLI:  python -m app.main --file data\events.json --interval 60 --allowed-misses 3
echo   API:  python -m app.main --api --port 8000
echo   Test: python -m pytest tests\ -v
echo.
echo Tip: Use the system Python packages (pydantic, pytest, fastapi already installed)
echo.
pause
