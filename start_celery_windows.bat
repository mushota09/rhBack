@echo off
echo ========================================
echo Demarrage de Celery pour Windows
echo ========================================
echo.
echo IMPORTANT: Celery sur Windows necessite le pool 'solo' ou 'gevent'
echo.
echo Option 1: Pool SOLO (simple, un seul worker)
echo Option 2: Pool GEVENT (parallele, necessite: uv pip install gevent)
echo.
set /p choice="Choisissez (1 ou 2): "

if "%choice%"=="1" (
    echo.
    echo Demarrage avec pool SOLO...
    echo.
    uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit
) else if "%choice%"=="2" (
    echo.
    echo Verification de gevent...
    uv pip show gevent >nul 2>&1
    if errorlevel 1 (
        echo gevent n'est pas installe. Installation...
        uv pip install gevent
    )
    echo.
    echo Demarrage avec pool GEVENT...
    echo.
    uv run celery -A rhBack worker -l info --pool=gevent --concurrency=10 -Q payroll,payslips,exports,audit
) else (
    echo Choix invalide. Utilisation du pool SOLO par defaut...
    echo.
    uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit
)

pause
