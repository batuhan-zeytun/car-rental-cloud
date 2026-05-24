@echo off
cd /d "%~dp0\.."
if not exist logs mkdir logs
".\.venv\Scripts\python.exe" run.py > logs\server.out 2> logs\server.err
