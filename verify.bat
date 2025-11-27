@echo off
REM Comprehensive Verification Script for Windows
REM Validates the entire Kairos setup

setlocal enabledelayedexpansion
set PASSED=0
set FAILED=0

chcp 65001 >nul
echo ==================================
echo Kairos Verification
echo ==================================
echo.

REM 1. Check Python version
echo 1. Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] FAILED: Python not found
    set /a FAILED+=1
) else (
    python --version
    echo [OK] PASSED: Python installation
    set /a PASSED+=1
)
echo.

REM 2. Check virtual environment
echo 2. Checking virtual environment...
if exist "venv\" (
    echo [OK] Virtual environment exists
    set /a PASSED+=1
) else (
    echo [!] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [X] FAILED: Virtual environment creation
        set /a FAILED+=1
    ) else (
        echo [OK] PASSED: Virtual environment creation
        set /a PASSED+=1
    )
)
echo.

REM 3. Activate virtual environment
echo 3. Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [X] FAILED: Virtual environment activation
    set /a FAILED+=1
) else (
    echo [OK] PASSED: Virtual environment activation
    set /a PASSED+=1
)
echo.

REM 4. Check project structure
echo 4. Checking project structure...
set DIRS=app tests data docs .github
for %%d in (%DIRS%) do (
    if exist "%%d\" (
        echo   [+] %%d\
    ) else (
        echo   [-] %%d\ MISSING
        set /a FAILED+=1
    )
)
echo.

REM 5. Check required files
echo 5. Checking required files...
set FILES=README.md LICENSE requirements.txt Dockerfile docker-compose.yml app\main.py app\models.py app\monitor.py tests\test_monitor.py data\events.json
for %%f in (%FILES%) do (
    if exist "%%f" (
        echo   [+] %%f
    ) else (
        echo   [-] %%f MISSING
        set /a FAILED+=1
    )
)
echo.

REM 6. Check if modules are installed
echo 6. Checking Python packages...
python -c "import pydantic" 2>nul
if errorlevel 1 (
    echo [!] WARNING: pydantic not installed
    echo [INFO] Installing dependencies...
    python -m pip install "pydantic>=2.0,<3.0" pydantic-settings python-dateutil pytest --quiet
)
echo [OK] Python packages checked
echo.

REM 7. Run tests
echo 7. Running test suite...
python -m pytest tests\ -v --tb=short
if errorlevel 1 (
    echo [X] FAILED: Test suite
    set /a FAILED+=1
) else (
    echo [OK] PASSED: Test suite
    set /a PASSED+=1
)
echo.

REM 8. Test CLI functionality
echo 8. Testing CLI functionality...
python -m app.main --file data\events.json --interval 60 --allowed-misses 3 --quiet
if errorlevel 1 (
    echo [X] FAILED: CLI execution
    set /a FAILED+=1
) else (
    echo [OK] PASSED: CLI execution
    set /a PASSED+=1
)
echo.

REM 9. Test JSON output
echo 9. Testing JSON output...
python -m app.main --file data\events.json --interval 60 --allowed-misses 3 --json --quiet > nul
if errorlevel 1 (
    echo [X] FAILED: JSON output
    set /a FAILED+=1
) else (
    echo [OK] PASSED: JSON output
    set /a PASSED+=1
)
echo.

REM Summary
echo ==================================
echo Verification Summary
echo ==================================
echo [OK] Passed: %PASSED%
echo [X] Failed: %FAILED%
echo.

if %FAILED% equ 0 (
    echo [SUCCESS] All checks passed! Project is ready.
    echo.
    echo Next steps:
    echo   1. Run CLI: python -m app.main --file data\events.json
    echo   2. Run API: python -m app.main --api --port 8000
    echo   3. Run tests: pytest tests\ -v
    echo   4. Build Docker: docker build -t kairos .
    echo   5. Deploy: docker-compose up -d
    echo.
    exit /b 0
) else (
    echo [WARNING] Some checks failed. Please review the output above.
    echo.
    exit /b 1
)
