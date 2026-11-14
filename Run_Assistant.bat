@echo off
cd /d "%~dp0AI_Assistant"
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "main.py"
) else if exist "venv\Scripts\python.exe" (
    start "" "venv\Scripts\python.exe" "main.py"
) else (
    start "" pythonw "main.py"
)
exit
