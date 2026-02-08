@echo off
echo Starting Backend...
start /B python manage.py runserver
timeout /t 5
echo Starting Desktop App...
python desktop_app/main.py
pause
