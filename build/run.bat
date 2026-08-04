@echo off
cd /d "%~dp0"
set "NODE_EXE=node"
where node >nul 2>nul || set "NODE_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%NODE_EXE%" where node >nul 2>nul || (echo Node.js 22+ is required & pause & exit /b 1)
start "AIsle Server" /min "%NODE_EXE%" server.mjs
timeout /t 1 /nobreak >nul
start "" msedge.exe --app=http://127.0.0.1:8765 --start-maximized
