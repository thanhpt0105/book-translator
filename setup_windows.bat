@echo off
REM Windows setup script for book-translator
REM Run this to set up the project on Windows

echo ============================================================
echo Book Translator - Windows Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.13 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip (continuing anyway)
) else (
    echo [OK] pip upgraded
)
echo.

REM Install requirements
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try running manually:
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy env.example .env >nul
    echo [OK] .env file created
    echo Edit .env file to configure your settings
) else (
    echo [OK] .env file already exists
)
echo.

REM Test installation
echo Testing installation...
python test_setup.py
if errorlevel 1 (
    echo [WARNING] Some modules may be missing
) else (
    echo [OK] All modules installed successfully!
)
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To use this project:
echo   1. Activate virtual environment:
echo      .venv\Scripts\activate.bat
echo.
echo   2. Run commands:
echo      python main.py status
echo      python main.py crawl
echo.
echo   3. See README.md for full documentation
echo.
echo For troubleshooting, see WINDOWS_SETUP.md
echo ============================================================
pause
