@echo off
cd /d "%~dp0"
start "" http://127.0.0.1:8765
set "NODE_EXE=node"
where node >nul 2>nul || set "NODE_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
"%NODE_EXE%" server.mjs
