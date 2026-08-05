@echo off
setlocal
cd /d "%~dp0"
set "NODE_EXE=node"
where node >nul 2>nul || set "NODE_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%NODE_EXE%" where node >nul 2>nul || (echo Node.js 22+ is required & pause & exit /b 1)
powershell -NoProfile -Command "try { Invoke-WebRequest 'http://127.0.0.1:8765/health' -UseBasicParsing -TimeoutSec 1 ^| Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  start "AIsle Backend" /min "%NODE_EXE%" backend\server.mjs
  timeout /t 1 /nobreak >nul
)
start "" "http://127.0.0.1:8765"
endlocal
