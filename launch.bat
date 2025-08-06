@echo off
echo 🧪 API Testing Suite - Quick Launch
echo ====================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Error creating virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing requirements
    pause
    exit /b 1
)

echo ✅ Setup complete!
echo 🚀 Starting Streamlit application...
echo 📖 The application will open in your browser at http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the application
echo.

REM Launch Streamlit
streamlit run app.py

pause
