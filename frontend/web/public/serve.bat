@echo off
REM JARVIS Frontend Server Launcher (Windows)

setlocal enabledelayedexpansion

set PORT=8000

echo.
echo ╔═══════════════════════════════════════════╗
echo ║       JARVIS Web Dashboard Server         ║
echo ╚═══════════════════════════════════════════╝
echo.
echo 📡 Starting server on port %PORT%
echo 📁 Serving from: %CD%
echo.
echo 🔗 Open in browser:
echo    http://localhost:%PORT%
echo.
echo ⚠️  Make sure backend is running:
echo    cd backend ^& python server.py
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
python -m http.server %PORT%

pause
