@echo off
echo ========================================
echo   Starting Kaiwhakarite Rawa Backend
echo ========================================
echo.

echo Checking Python environment...
python --version

echo.
echo Installing/Updating requirements...
pip install -r requirements.txt

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

python start_backend.py 