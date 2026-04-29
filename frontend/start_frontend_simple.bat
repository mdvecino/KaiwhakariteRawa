@echo off
echo ========================================
echo   Starting Kaiwhakarite Rawa Frontend
echo ========================================
echo.

echo Checking Node.js environment...
node --version
npm --version

echo.
echo Changing to frontend directory...
cd frontend

echo.
echo Installing/Updating dependencies...
npm install

echo.
echo Starting frontend server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

npm start 