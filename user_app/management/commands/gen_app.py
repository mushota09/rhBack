from django.core.management.base import BaseCommand
from django.apps import apps
import json
from pathlib import Path

class Command(BaseCommand):
    help = "Liste toutes les applications et leurs modèles dans le projet"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'text', 'dict'],
            help="Format de sortie: json, text ou dict"
        )
        parser.add_argument(
            '--output',
            type=str,
            help="Chemin du fichier de sortie (par défaut: affichage console)"
        )
        parser.add_argument(
            '--exclude-third-party',
            action='store_true',
            help="Exclure les applications tierces (django.contrib, etc.)"
        )
        parser.add_argument(
            '--app-only',
            action='store_true',
            help="Liste uniquement les noms des applications"
        )

    def handle(self, *args, **options):
        format_output = options['format']
        output_file = options['output']
        exclude_third_party = options['exclude_third_party']
        app_only = options['app_only']
        
        # Obtenir toutes les configurations d'applications
        app_configs = apps.get_app_configs()
        
        # Applications tierces à exclure (si demandé)
        third_party_prefixes = [
            'django.',
            'rest_framework',
            'corsheaders',
            'drf_',
            'debug_toolbar',
            'admin_',
            'auth',
            'contenttypes',
            'sessions',
            'messages',
            'staticfiles',
        ]
        
        data = {}
        app_count = 0
        model_count = 0
        
        for app_config in app_configs:
            app_name = app_config.name
            
            # Exclure les applications tierces si demandé
            if exclude_third_party:
                if any(app_name.startswith(prefix) for prefix in third_party_prefixes):
                    continue
            
            # Obtenir tous les modèles de l'application
            models = []
            for model in app_config.get_models():
                model_name = model.__name__
                models.append(model_name)
                model_count += 1
            
            # Ajouter au dictionnaire
            if models or not app_only:
                data[app_name] = models if not app_only else []
                app_count += 1
        
        # Trier les données par nom d'application
        sorted_data = dict(sorted(data.items()))
        
        # Préparer les statistiques
        stats = {
            "total_apps": app_count,
            "total_models": model_count,
            "apps": sorted_data
        }
        
        # Format de sortie
        if format_output == 'json':
            output = json.dumps(stats, indent=2, ensure_ascii=False)
        elif format_output == 'dict':
            output = str(sorted_data)
        else:  # format text
            output = self.format_text_output(sorted_data, app_only)
        
        # Écrire dans un fichier ou afficher
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format_output == 'json':
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                else:
                    f.write(output)
            self.stdout.write(self.style.SUCCESS(f"✅ Données enregistrées dans {output_file}"))
        else:
            self.stdout.write(output)
            
            # Afficher les statistiques en format texte
            if format_output == 'text':
                self.stdout.write("\n" + "="*50)
                self.stdout.write(self.style.SUCCESS(f"📊 STATISTIQUES:"))
                self.stdout.write(f"   • Applications: {app_count}")
                self.stdout.write(f"   • Modèles: {model_count}")
                self.stdout.write("="*50)

    def format_text_output(self, data, app_only=False):
        """Format texte pour l'affichage console"""
        output_lines = []
        output_lines.append("📁 APPLICATIONS ET MODÈLES DU PROJET")
        output_lines.append("="*50)
        
        for app_name, models in data.items():
            output_lines.append(f"\n📦 {app_name}")
            output_lines.append("─" * (len(app_name) + 2))
            
            if app_only:
                output_lines.append("  (Modèles non listés - option --app-only activée)")
            elif models:
                for i, model in enumerate(models, 1):
                    output_lines.append(f"  {i:2d}. {model}")
            else:
                output_lines.append("  (Aucun modèle trouvé)")
        
        return "\n".join(output_lines)


# Version alternative avec détection des applications locales
class CommandLocalApps(BaseCommand):
    help = "Liste uniquement les applications locales (non Django) et leurs modèles"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--project-root',
            type=str,
            default='.',
            help="Racine du projet Django (par défaut: répertoire courant)"
        )
    
    def handle(self, *args, **options):
        project_root = Path(options['project_root'])
        
        # Détecter les applications locales en cherchant dans le projet
        app_configs = apps.get_app_configs()
        
        local_apps = {}
        
        for app_config in app_configs:
            app_path = Path(app_config.path)
            
            # Vérifier si l'application est dans le projet racine
            # (c'est une façon simple de détecter les applications locales)
            try:
                # Chercher si le chemin de l'app est sous le projet
                if project_root in app_path.parents:
                    app_name = app_config.name
                    models = [model.__name__ for model in app_config.get_models()]
                    local_apps[app_name] = models
            except:
                continue
        
        # Afficher les résultats
        self.stdout.write("📁 APPLICATIONS LOCALES")
        self.stdout.write("="*40)
        
        for app_name, models in sorted(local_apps.items()):
            self.stdout.write(f"\n📦 {app_name}")
            self.stdout.write("─" * (len(app_name) + 2))
            
            if models:
                for i, model in enumerate(models, 1):
                    self.stdout.write(f"  {i:2d}. {model}")
            else:
                self.stdout.write("  (Aucun modèle trouvé)")
        
        # Statistiques
        self.stdout.write("\n" + "="*40)
        self.stdout.write(self.style.SUCCESS(f"📊 STATISTIQUES:"))
        self.stdout.write(f"   • Applications locales: {len(local_apps)}")
        self.stdout.write(f"   • Modèles totaux: {sum(len(models) for models in local_apps.values())}")
        
        # Retourner les données pour utilisation dans d'autres scripts
        return local_apps


# Version qui génère un fichier Python avec le dictionnaire
class CommandGenerateDataPy(BaseCommand):
    help = "Génère un fichier Python avec le dictionnaire des applications et modèles"
    
    def handle(self, *args, **options):
        app_configs = apps.get_app_configs()
        
        # Filtrer les applications tierces
        third_party_prefixes = ['django.', 'rest_framework', 'corsheaders']
        
        apps_data = {}
        
        for app_config in app_configs:
            app_name = app_config.name
            
            # Sauter les applications tierces
            if any(app_name.startswith(prefix) for prefix in third_party_prefixes):
                continue
            
            # Récupérer les modèles
            models = [model.__name__ for model in app_config.get_models()]
            if models:  # Ne garder que les applications avec des modèles
                apps_data[app_name] = models
        
        # Trier par nom d'application
        sorted_apps_data = dict(sorted(apps_data.items()))
        
        # Générer le contenu du fichier Python
        content = '''"""
Fichier généré automatiquement listant les applications et modèles du projet.
Généré le: {date_generated}
"""

APPS_AND_MODELS = {apps_data}

# Statistiques
TOTAL_APPS = {total_apps}
TOTAL_MODELS = {total_models}

# Fonction utilitaire pour obtenir les modèles d'une application
def get_models_for_app(app_name):
    """
    Retourne la liste des modèles pour une application donnée.
    
    Args:
        app_name (str): Nom de l'application Django
        
    Returns:
        list: Liste des noms de modèles ou liste vide si l'application n'existe pas
    """
    return APPS_AND_MODELS.get(app_name, [])

# Fonction utilitaire pour vérifier si un modèle existe
def model_exists(app_name, model_name):
    """
    Vérifie si un modèle existe dans une application.
    
    Args:
        app_name (str): Nom de l'application
        model_name (str): Nom du modèle
        
    Returns:
        bool: True si le modèle existe, False sinon
    """
    return model_name in APPS_AND_MODELS.get(app_name, [])

if __name__ == "__main__":
    print("Applications et modèles du projet:")
    print("=" * 50)
    for app, models in APPS_AND_MODELS.items():
        print(f"\\n📦 {app}")
        for model in models:
            print(f"  • {model}")
    print("\\n" + "=" * 50)
    print(f"Total: {TOTAL_APPS} applications, {TOTAL_MODELS} modèles")
'''.format(
    date_generated=self.get_current_datetime(),
    apps_data=json.dumps(sorted_apps_data, indent=4, ensure_ascii=False),
    total_apps=len(sorted_apps_data),
    total_models=sum(len(models) for models in sorted_apps_data.values())
)

        # Écrire le fichier
        output_file = Path('project_apps_models.py')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.stdout.write(self.style.SUCCESS(f"✅ Fichier généré: {output_file}"))
        self.stdout.write(f"📊 Contient: {len(sorted_apps_data)} applications, "
                         f"{sum(len(models) for models in sorted_apps_data.values())} modèles")
    
    def get_current_datetime(self):
        from django.utils import timezone
        return timezone.now().strftime("%Y-%m-%d %H:%M:%S")