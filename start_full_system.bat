@echo off
echo ========================================
echo   Kaiwhakarite Rawa - Full System Start
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and ensure it's in your PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Starting Backend Server...
echo.

REM Delete the old database file
del kaiwhakarite_rawa.db

REM Start backend server in background
start "Kaiwhakarite Rawa Backend" cmd /k "python backend/run_server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
echo.

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

REM Start frontend server in background
start "Kaiwhakarite Rawa Frontend" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo   System Starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Demo Credentials:
echo - Admin:   admin / admin123
echo - Manager: manager / manager123
echo - User:    user / user123
echo.
echo Press any key to exit this window...
pause >nul

REM Run the script to list users and their hashed passwords
echo Running script to list users and their hashed passwords...
python -c "import sqlite3; conn = sqlite3.connect('kaiwhakarite_rawa.db'); cursor = conn.cursor(); cursor.execute('SELECT username, email, hashed_password FROM users'); users = cursor.fetchall(); for user in users: print(user); conn.close()"

REM [DEBUG] Received item_data: ...