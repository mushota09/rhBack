from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import ForeignKey, OneToOneField, CharField, TextField

class Command(BaseCommand):
    help = "Génère permit_list_expands, filterset_fields et search_fields pour un modèle"

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str, help='Nom de l\'app')
        parser.add_argument('model_name', type=str, help='Nom du modèle')
        parser.add_argument('--max-depth', type=int, default=6, help='Profondeur max des relations')

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        max_depth = options['max_depth']

        model = apps.get_model(app_label, model_name)
        permit_list_expands = []
        filterset_fields = []
        search_fields = []
        def explore(model, prefix='', depth=0):
            if depth > max_depth:
                return
            for field in model._meta.get_fields():
                # ForeignKey / OneToOneField → expansions et filtre
                if isinstance(field, (ForeignKey, OneToOneField)):
                    dot_path = f"{prefix}{field.name}"
                    permit_list_expands.append(dot_path)
                    filterset_fields.append(dot_path.replace('.', '__'))
                    # récursion
                    explore(field.related_model, prefix=dot_path + ".", depth=depth+1)
                # CharField pour search
                elif isinstance(field, CharField) and not isinstance(field, TextField):
                    search_path = f"{prefix}{field.name}".replace('.', '__')
                    search_fields.append(search_path)

        explore(model)

        # Affichage final
        

        print("filterset_fields = [")
        for f in filterset_fields:
            print(f"    '{f}',")
        print("]\n")
        
        
        print("permit_list_expands = [")
        for p in permit_list_expands:
            print(f"    '{p}',")
        print("]\n")

        print("search_fields = [")
        for s in search_fields:
            print(f"    '{s}',")
        print("]")
