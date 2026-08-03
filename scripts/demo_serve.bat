@echo off
REM Moodify demo backend launcher (DSK-MFY-DEMO-001)
REM Starts the real v01 pipeline API on 0.0.0.0:8000.
chcp 65001 >nul
set ROOT=%~dp0..
cd /d "%ROOT%"
set PYTHONPATH=%ROOT%\moodify-core-package\src;%ROOT%\moodify_runtime;%PYTHONPATH%
echo Starting Moodify demo API on http://0.0.0.0:8000 (docs: /docs)
python -m uvicorn moodify.api.main:app --host 0.0.0.0 --port 8000
