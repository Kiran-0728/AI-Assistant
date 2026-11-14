@echo off
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" "Assistant.py"
) else (
    python "Assistant.py"
)
pause
