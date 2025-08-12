@echo off
REM EduRec Development Setup Script for Windows
REM This script sets up a Python virtual environment and installs dependencies

echo 🚀 Setting up EduRec development environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Check if poetry is available
poetry --version >nul 2>&1
if errorlevel 1 (
    echo 📚 Installing dependencies with pip...
    pip install -r requirements.txt
) else (
    echo 📚 Installing dependencies with Poetry...
    poetry install
)

echo.
echo 🎉 Setup complete! To activate the environment, run:
echo    venv\Scripts\activate.bat
echo.
echo 📖 Next steps:
echo    1. Activate the environment: venv\Scripts\activate.bat
echo    2. Generate sample data: python -m src.edurec.data.generate_sample
echo    3. Run the API: python -m uvicorn src.edurec.api.main:app --reload
echo    4. Run tests: pytest src/edurec/tests/
echo.
pause 