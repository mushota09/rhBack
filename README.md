<!-- ************************************* -->
1. INSTALLATION
<!-- ************************************* -->

SOUS MAC/LINUX
curl -LsSf https://astral.sh/uv/install.sh | sh

SOUS WINDOWS
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

<!-- **************************************************** -->
2.PACKAGES
<!-- **************************************************** -->
deplaces-toi dans le meme dossier que manage.py puis tapes:
uv sync

<!-- **************************************************** -->
DEMARRER PROJET
<!-- **************************************************** -->
deplaces-toi dans le meme dossier que manage.py puis tapes:

## Démarrer le serveur Django
uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000

## Démarrer Celery

### Sur Linux/Mac:
uv run celery -A rhBack worker -l info -Q payroll,payslips,exports,audit

### Sur Windows (IMPORTANT):
# Option 1: Utiliser le script automatique
.\start_celery_windows.bat
# OU
.\start_celery_windows.ps1

# Option 2: Commande manuelle avec pool solo (simple)
uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit

# Option 3: Commande manuelle avec pool gevent (parallèle, nécessite: uv pip install gevent)
uv run celery -A rhBack worker -l info --pool=gevent --concurrency=10 -Q payroll,payslips,exports,audit

## Tests
python manage.py test paie_app.tests.test_fixtures_simple.SimpleFixturesTest.test_base_fixtures_creation -v 2

# Ou avec pytest
python -m pytest user_app/tests/ -v


