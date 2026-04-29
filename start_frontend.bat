@echo off
echo Starting Kaiwhakarite Rawa Frontend Server...
echo.
cd frontend
echo Installing dependencies...
npm install
echo.
echo Starting frontend on http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
npm start
pause 