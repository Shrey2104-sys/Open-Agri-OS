@echo off
cd /d "%~dp0"
echo Starting Open-Agri OS Backend (Flask)...
echo Please keep this window open!
set FLASK_APP=frontend/app.py
set FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
pause
