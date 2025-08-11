@echo off
ECHO Starting Development Environment for HydroML...

ECHO.
ECHO [1/3] Starting Redis Server in WSL...
REM Inicia WSL en segundo plano y ejecuta el comando para arrancar Redis.
wsl sudo service redis-server start

ECHO [2/3] Starting Django Development Server...
REM Abre una nueva ventana de PowerShell, activa el venv y corre el servidor.
start "Django Server" powershell -NoExit -Command "& { .\.venv\Scripts\Activate.ps1; python manage.py runserver }"

ECHO [3/3] Starting Celery Worker...
REM Abre otra ventana de PowerShell, activa el venv y corre el worker de Celery.
start "Celery Worker" powershell -NoExit -Command "& { .\.venv\Scripts\Activate.ps1; celery -A hydroML worker -l info -P eventlet }"

ECHO.
ECHO Done! Your terminals are starting up.