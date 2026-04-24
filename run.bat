@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv || goto :err
)

call ".venv\Scripts\activate.bat" || goto :err

python -m pip install --upgrade pip >nul
pip install -r requirements.txt || goto :err

if not exist ".env" (
  echo WARNING: .env not found. Copy .env.example to .env and add your OPENAI_API_KEY.
)

echo.
echo Starting server at http://localhost:8000
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
goto :eof

:err
echo.
echo Startup failed.
exit /b 1
