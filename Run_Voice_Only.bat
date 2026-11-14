@echo off
cd /d "%~dp0AI_Assistant"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" "Assistant.py"
) else (
    python "Assistant.py"
)
pause
