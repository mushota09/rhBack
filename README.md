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

uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000




python manage.py test paie_app.tests.test_fixtures_simple.SimpleFixturesTest.test_base_fixtures_creation -v 2
