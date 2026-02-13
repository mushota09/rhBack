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




# *******************************************************************************************************
# POSTE                           POSTE                           POSTE                           POSTE
# *******************************************************************************************************
# class poste(models.Model):
#     titre = models.CharField(max_length=100)
#     code = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     service_id = models.ForeignKey(service, on_delete=models.CASCADE, related_name='postes')
#     class Meta:
#         db_table = 'rh_poste'

#     def __str__(self):
#         return self.titre


je viens de modifier mon systeme RBAC SYSTEM j'ai supprimer la table poste mais par contre j'ai ajoute serviceGroup (pour lier les services aux groupes)  et dans le model employe poste_id est devenu le foreinkey service_group pour faire le lien entre les employés et serviceGroupes. lors de la creation du group creer aussi  dans serviceGroup et lors de la suppression du serviceGroup supprimer aussi son group correspondant.  mais je veux que le systeme soit full asynchrone,avec adrf et adrf_flex_fields (l'adaptation de drf_flex_fields en version asynchrone) analyse et comprend d'abord comment fonctionne adrf_flex_fields

pour le point 1 (Lors de la création d'un Group, voulez-vous créer automatiquement un ServiceGroup pour TOUS les services existants, ou seulement pour des services spécifiques fournis dans la requête ?) je veux que Lors de la création d'un Group,  seulement pour des services spécifiques fournis dans la requête ? sinon les restes c bon


lors de la creation de l'employe assigner celui-ci directement a un groupe(userGroup) ,et  applique adrf_flex_fields pour tout le systeme RBAC
