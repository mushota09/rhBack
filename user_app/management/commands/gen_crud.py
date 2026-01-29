
import ast
from pathlib import Path
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import ForeignKey, OneToOneField, ManyToManyField, CharField, TextField, DateTimeField

class Command(BaseCommand):
    help = "Auto-génère serializers.py, views.py, filter.py avec détection intelligente des noms de fichiers"

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str, help='Nom de l\'app')
        parser.add_argument('model_name', type=str, help='Nom du modèle')
        parser.add_argument('--max-depth', type=int, default=6, help='Profondeur max des relations')

    # -----------------------------
    # Détecter le fichier serializer existant
    # -----------------------------
    def detect_serializer_file(self, directory_path: Path):
        """Détecte le fichier serializer dans un dossier donné"""
        # Liste des noms possibles de fichiers serializer
        possible_names = [
            'serializers.py',
            'serialisers.py', 
            'serializer.py',
            'serialiser.py'
        ]
        
        for filename in possible_names:
            file_path = directory_path / filename
            if file_path.exists():
                return filename, file_path
        
        return None, None

    # -----------------------------
    # Détection du serializer via AST
    # -----------------------------
    def detect_serializer_class(self, file_path: Path, related_model_name: str):
        """Détecte la classe du serializer dans un fichier donné"""
        model_lower = related_model_name.lower()
        candidates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    cls_name = node.name
                    cls_lower = cls_name.lower()
                    
                    # Priorité 1: J_ + nom du modèle
                    if cls_lower.startswith("j_") and model_lower in cls_lower:
                        return cls_name
                    # Priorité 2: I_ + nom du modèle
                    elif cls_lower.startswith("i_") and model_lower in cls_lower:
                        candidates.append(cls_name)
                    # Priorité 3: contient le nom du modèle
                    elif model_lower in cls_lower:
                        candidates.append(cls_name)
                    # Priorité 4: termine par Serializer ou Serializers
                    elif cls_lower.endswith("serializer") or cls_lower.endswith("serializers"):
                        candidates.append(cls_name)
        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {e}")
        
        if candidates:
            return candidates[0]
        
        # Fallback: générer un nom par défaut
        return f"J_{related_model_name}Serializers"

    # -----------------------------
    # Détection du chemin du serializer pour une relation
    # -----------------------------
    def get_related_serializer_info(self, field):
        """Retourne le chemin d'import et le nom du serializer pour un champ relation"""
        related_model = field.related_model
        app_label = related_model._meta.app_label
        model_name = related_model._meta.model_name
        
        # Obtenir le chemin de l'application
        app_config = apps.get_app_config(app_label)
        app_path = Path(app_config.path)
        
        # CAS SPÉCIAL: admin_user dans gestionUtilisateur
        if app_label == 'gestionUtilisateur' and model_name == 'admin_user':
            # Chercher dans gestionUtilisateur/modules/admin_user/
            module_path = app_path / 'modules' / model_name
            
            if not module_path.exists():
                # Créer le dossier s'il n'existe pas
                module_path.mkdir(parents=True, exist_ok=True)
            
            # Détecter le fichier serializer
            serializer_filename, serializer_filepath = self.detect_serializer_file(module_path)
            
            if serializer_filename and serializer_filepath:
                # Détecter la classe
                serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
                # Nom du fichier sans extension
                module_name = serializer_filename.replace('.py', '')
                import_path = f"{app_label}.modules.{model_name}.{module_name}"
                return import_path, serializer_class
            else:
                # Fichier non trouvé, utiliser valeurs par défaut
                import_path = f"{app_label}.modules.{model_name}.serializers"
                return import_path, f"J_{model_name}Serializers"
        
        # CAS NORMAL: autres modèles
        else:
            # Chercher d'abord dans app_label/modules/model_name/
            modules_model_path = app_path / 'modules' / model_name
            
            if modules_model_path.exists():
                # Détecter le fichier serializer
                serializer_filename, serializer_filepath = self.detect_serializer_file(modules_model_path)
                
                if serializer_filename and serializer_filepath:
                    # Détecter la classe
                    serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
                    # Nom du fichier sans extension
                    module_name = serializer_filename.replace('.py', '')
                    import_path = f"{app_label}.modules.{model_name}.{module_name}"
                    return import_path, serializer_class
            
            # Si pas trouvé dans modules/model_name, chercher dans app_label directement
            serializer_filename, serializer_filepath = self.detect_serializer_file(app_path)
            
            if serializer_filename and serializer_filepath:
                # Détecter la classe
                serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
                # Nom du fichier sans extension
                module_name = serializer_filename.replace('.py', '')
                import_path = f"{app_label}.{module_name}"
                return import_path, serializer_class
            
            # Si aucun fichier trouvé, utiliser valeurs par défaut
            import_path = f"{app_label}.modules.{model_name}.serializers"
            return import_path, f"J_{model_name}Serializers"

    # -----------------------------
    # Vérifier si le modèle a des relations
    # -----------------------------
    def has_foreign_keys(self, model):
        """Vérifie si le modèle a des ForeignKey ou OneToOneField"""
        for field in model._meta.get_fields():
            if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
                return True
        return False

    # -----------------------------
    # Génération des expansions récursives
    # -----------------------------
    def generate_expansions(self, model, max_depth=6):
        """Génère les expansions récursives pour permit_list_expands"""
        expansions = []
        filterset_fields = []
        search_fields = []
        
        def explore(model, prefix='', depth=0, visited=None):
            if visited is None:
                visited = set()
            
            if depth >= max_depth:
                return
            
            model_key = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_key in visited:
                return
            visited.add(model_key)
            
            for field in model._meta.get_fields():
                if isinstance(field, (ForeignKey, OneToOneField)):
                    dot_path = f"{prefix}{field.name}"
                    expansions.append(dot_path)
                    filterset_fields.append(dot_path.replace('.', '__'))
                    
                    # Explorer le modèle lié
                    if field.related_model:
                        explore(field.related_model, f"{dot_path}.", depth + 1, visited.copy())
                
                # CharField pour search (uniquement au niveau racine)
                elif depth == 0 and isinstance(field, CharField) and not isinstance(field, TextField):
                    search_fields.append(field.name)
        
        explore(model)
        return expansions, filterset_fields, search_fields

    # -----------------------------
    # Génération du fichier serializers.py
    # -----------------------------
    def generate_serializers(self, model, module_path, expansions):
        """Génère le fichier serializers.py"""
        model_name = model.__name__
        
        # Vérifier si le modèle a des relations
        has_relations = self.has_foreign_keys(model)
        
        # Détecter si le fichier existe déjà et son format
        serializer_filename, _ = self.detect_serializer_file(module_path)
        
        # Déterminer les noms des serializers en fonction du format existant
        if serializer_filename and serializer_filename.endswith('.py'):
            # Lire le fichier existant pour détecter le format
            existing_file_path = module_path / serializer_filename
            try:
                with open(existing_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Détecter le format des noms de classe
                if f"J_{model_name}Serializers" in content:
                    serializer_read = f"J_{model_name}Serializers"
                    serializer_write = f"I_{model_name}Serializers"
                elif f"J_{model_name}Serializer" in content:
                    serializer_read = f"J_{model_name}Serializer"
                    serializer_write = f"I_{model_name}Serializer"
                else:
                    # Par défaut
                    serializer_read = f"J_{model_name}Serializers"
                    serializer_write = f"I_{model_name}Serializers"
            except:
                # En cas d'erreur, utiliser le format par défaut
                serializer_read = f"J_{model_name}Serializers"
                serializer_write = f"I_{model_name}Serializers"
        else:
            # Nouveau fichier, utiliser le format par défaut
            serializer_read = f"J_{model_name}Serializers"
            serializer_write = f"I_{model_name}Serializers"
        
        # Préparer le contenu
        content = [
            "from rest_framework import serializers",
            "from rest_flex_fields import FlexFieldsModelSerializer",
            f"from .models import {model_name}",
            ""
        ]
        
        # Si le modèle a des relations, générer le serializer J_ avec expandable_fields
        if has_relations:
            # Collecter les imports des serializers liés
            imports_set = set()
            expandable_fields = {}
            
            # Pour chaque relation, déterminer quel champ inclure dans expandable_fields
            for field in model._meta.get_fields():
                if isinstance(field, (ForeignKey, OneToOneField)):
                    import_path, serializer_class = self.get_related_serializer_info(field)
                    
                    # Ajouter l'import
                    import_line = f"from {import_path} import {serializer_class}"
                    if import_line not in imports_set:
                        # Insérer après les imports de base
                        content.insert(len(content) - 1, import_line)
                        imports_set.add(import_line)
                    
                    # Ajouter au expandable_fields
                    expandable_fields[field.name] = serializer_class
        
        # Réorganiser le contenu pour avoir les imports au début
        imports = []
        other_lines = []
        
        for line in content:
            if line.startswith("from ") or line.startswith("import "):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Trier les imports (optionnel, pour la lisibilité)
        imports.sort()
        
        # Reconstruire le contenu final
        final_content = imports + other_lines
        
        # Si le modèle a des relations, générer les deux serializers
        if has_relations:
            # Serializer Read (J_)
            final_content.append(f"class {serializer_read}(FlexFieldsModelSerializer):")
            
            # Ajouter les PrimaryKeyRelatedField pour les champs d'expansion
            for field_name in expandable_fields.keys():
                final_content.append(f"    {field_name} = serializers.PrimaryKeyRelatedField(read_only=True)")
            
            final_content.extend([
                "    class Meta:",
                f"        model = {model_name}",
                '        fields = "__all__"',
            ])
            
            if expandable_fields:
                final_content.append("        expandable_fields = {")
                for field_name, serializer in expandable_fields.items():
                    final_content.append(f"            '{field_name}': {serializer},")
                final_content.append("        }")
            
            final_content.append("")
            
            # Serializer Write (I_)
            final_content.append(f"class {serializer_write}(FlexFieldsModelSerializer):")
            final_content.extend([
                "    class Meta:",
                f"        model = {model_name}",
                '        fields = "__all__"',
            ])
        
        # Si le modèle n'a pas de relations, générer seulement le serializer I_
        else:
            final_content.append(f"class {serializer_write}(FlexFieldsModelSerializer):")
            final_content.extend([
                "    class Meta:",
                f"        model = {model_name}",
                '        fields = "__all__"',
            ])
            # Pour un modèle sans relations, on utilise le même serializer pour lecture et écriture
            serializer_read = serializer_write
        
        # Écrire le fichier
        # Utiliser le nom de fichier détecté ou "serializers.py" par défaut
        output_filename = serializer_filename or "serializers.py"
        file_path = module_path / output_filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(final_content))
        
        return serializer_read, serializer_write, output_filename.replace('.py', '')

    # -----------------------------
    # Génération du fichier filter.py
    # -----------------------------
    def generate_filter(self, model, module_path, filterset_fields):
        """Génère le fichier filter.py"""
        model_name = model.__name__
        
        content = [
            "import django_filters",
            f"from .models import {model_name}",
            "",
            "",
            f"class {model_name}Filter(django_filters.FilterSet):",
        ]
        
        # Ajouter les filtres de date pour les DateTimeField
        date_fields_added = False
        for field in model._meta.get_fields():
            if isinstance(field, DateTimeField):
                content.append(f'    {field.name}_date = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date")')
                content.append(f'    {field.name}_min = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date__gte")')
                content.append(f'    {field.name}_max = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date__lte")')
                date_fields_added = True
        
        if date_fields_added:
            content.append("")
        
        content.extend([
            "    class Meta:",
            f"        model = {model_name}",
            "        fields = [",
        ])
        
        # Ajouter les champs de filtre
        if filterset_fields:
            for field_name in filterset_fields:
                content.append(f"            '{field_name}',")
        else:
            # Si pas de filtres de relation, on peut mettre une liste vide
            # Ou ajouter d'autres filtres si nécessaire
            content.append("            # Aucun filtre de relation")
        
        content.extend([
            "        ]",
            "",
        ])
        
        # Écrire le fichier
        file_path = module_path / "filter.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

    # -----------------------------
    # Génération du fichier views.py
    # -----------------------------
    def generate_views(self, model, module_path, expansions, search_fields, serializer_read, serializer_write, serializer_module_name):
        """Génère le fichier views.py"""
        model_name = model.__name__
        
        # Vérifier si le modèle a des relations
        has_relations = self.has_foreign_keys(model)
        
        content = [
            "from gestionUtilisateur.utils import DynamicExpandMixin, CustomPagination",
            "from django_filters.rest_framework import DjangoFilterBackend as FB",
            "from rest_flex_fields.views import FlexFieldsModelViewSet",
            "from rest_framework.filters import SearchFilter as SF",
            f"from .filter import {model_name}Filter",
            f"from .models import {model_name}",
        ]
        
        # Ajouter l'import du serializer approprié
        if serializer_read == serializer_write:
            # Si c'est le même serializer (pas de relations)
            content.append(f"from .{serializer_module_name} import {serializer_write}")
        else:
            # Si deux serializers différents (avec relations)
            content.append(f"from .{serializer_module_name} import {serializer_read}, {serializer_write}")
        
        content.append("")
        content.append("")
        content.append(f"class {model_name}APIView(DynamicExpandMixin, FlexFieldsModelViewSet):")
        content.append(f"    queryset = {model_name}.objects.all().order_by('-id')")
        
        # Définir les serializers
        if serializer_read == serializer_write:
            # Pas de relations, utiliser le même serializer
            content.append(f"    serializer_class = {serializer_write}")
            # Pour FlexFieldsModelViewSet, on peut définir serializer_class directement
            content.append(f"    # Note: Pas de relations, donc un seul serializer utilisé")
        else:
            # Avec relations, utiliser deux serializers
            content.append(f"    serializer_class_read = {serializer_read}")
            content.append(f"    serializer_class_write = {serializer_write}")
        
        content.extend([
            "    filter_backends = [FB, SF]",
            "    pagination_class = CustomPagination",
            f"    filterset_class = {model_name}Filter",
            "",
        ])
        
        # Ajouter permit_list_expands seulement si le modèle a des relations
        if has_relations and expansions:
            content.append("    permit_list_expands = [")
            for expand in expansions:
                content.append(f"        '{expand}',")
            content.append("    ]")
            content.append("")
        else:
            content.append("    # Pas d'expansions nécessaires (modèle sans relations)")
            content.append("")
        
        # Ajouter search_fields
        if search_fields:
            content.append("    search_fields = [")
            for search in search_fields:
                content.append(f"        '{search}',")
            content.append("    ]")
        else:
            content.append("    # Pas de champs de recherche définis")
        
        content.append("")
        
        # Écrire le fichier
        file_path = module_path / "views.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

    # -----------------------------
    # Point d'entrée principal
    # -----------------------------
    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        max_depth = options['max_depth']
        
        # Récupérer le modèle
        model = apps.get_model(app_label, model_name)
        
        # Vérifier si le modèle a des relations
        has_relations = self.has_foreign_keys(model)
        
        # Déterminer le chemin du module
        app_config = apps.get_app_config(app_label)
        app_path = Path(app_config.path)
        
        # CAS SPÉCIAL : admin_user
        if app_label == 'gestionUtilisateur' and model_name == 'admin_user':
            module_path = app_path / 'modules' / model_name
        else:
            # Structure normale : app_label/modules/model_name/
            module_path = app_path / 'modules' / model_name
        
        # Créer le dossier s'il n'existe pas
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Générer les listes d'expansions, filtres et recherche
        expansions, filterset_fields, search_fields = self.generate_expansions(model, max_depth)
        
        # Générer les fichiers
        serializer_read, serializer_write, serializer_module_name = self.generate_serializers(model, module_path, expansions)
        self.generate_filter(model, module_path, filterset_fields)
        self.generate_views(model, module_path, expansions, search_fields, serializer_read, serializer_write, serializer_module_name)
        
        # Afficher les résultats
        self.stdout.write(self.style.SUCCESS(f"✅ Fichiers générés pour {model_name}"))
        self.stdout.write(self.style.SUCCESS(f"📁 Dossier : {module_path}"))
        self.stdout.write("")
        self.stdout.write("📄 Fichiers créés/mis à jour :")
        
        # Afficher les noms réels des fichiers
        serializer_filename, _ = self.detect_serializer_file(module_path)
        if serializer_filename:
            self.stdout.write(f"  • {module_path / serializer_filename}")
        else:
            self.stdout.write(f"  • {module_path / 'serializers.py'}")
        
        self.stdout.write(f"  • {module_path / 'views.py'}")
        self.stdout.write(f"  • {module_path / 'filter.py'}")
        self.stdout.write("")
        self.stdout.write("🔍 Détection automatique :")
        self.stdout.write(f"  • Fichier serializer détecté : {serializer_filename or 'Nouveau fichier créé'}")
        self.stdout.write(f"  • Module serializer utilisé : {serializer_module_name}")
        
        if has_relations:
            self.stdout.write(f"  • Classe de lecture : {serializer_read}")
            self.stdout.write(f"  • Classe d'écriture : {serializer_write}")
        else:
            self.stdout.write(f"  • Classe unique (pas de relations) : {serializer_write}")
        
        self.stdout.write("")
        self.stdout.write("📊 Statistiques :")
        self.stdout.write(f"  • A des relations : {'Oui' if has_relations else 'Non'}")
        self.stdout.write(f"  • Expansions générées : {len(expansions)}")
        self.stdout.write(f"  • Filtres générés : {len(filterset_fields)}")
        self.stdout.write(f"  • Champs de recherche : {len(search_fields)}")



































# import ast
# from pathlib import Path
# import os
# from django.core.management.base import BaseCommand
# from django.apps import apps
# from django.db.models import ForeignKey, OneToOneField, CharField, TextField, DateTimeField

# class Command(BaseCommand):
#     help = "Auto-génère serializers.py, views.py, filter.py avec détection intelligente des noms de fichiers"

#     def add_arguments(self, parser):
#         parser.add_argument('app_label', type=str, help='Nom de l\'app')
#         parser.add_argument('model_name', type=str, help='Nom du modèle')
#         parser.add_argument('--max-depth', type=int, default=6, help='Profondeur max des relations')

#     # -----------------------------
#     # Détecter le fichier serializer existant
#     # -----------------------------
#     def detect_serializer_file(self, directory_path: Path):
#         """Détecte le fichier serializer dans un dossier donné"""
#         # Liste des noms possibles de fichiers serializer
#         possible_names = [
#             'serializers.py',
#             'serialisers.py', 
#             'serializer.py',
#             'serialiser.py'
#         ]
        
#         for filename in possible_names:
#             file_path = directory_path / filename
#             if file_path.exists():
#                 return filename, file_path
        
#         return None, None

#     # -----------------------------
#     # Détection du serializer via AST
#     # -----------------------------
#     def detect_serializer_class(self, file_path: Path, related_model_name: str):
#         """Détecte la classe du serializer dans un fichier donné"""
#         model_lower = related_model_name.lower()
#         candidates = []
        
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 tree = ast.parse(f.read(), filename=str(file_path))
            
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.ClassDef):
#                     cls_name = node.name
#                     cls_lower = cls_name.lower()
                    
#                     # Priorité 1: J_ + nom du modèle
#                     if cls_lower.startswith("j_") and model_lower in cls_lower:
#                         return cls_name
#                     # Priorité 2: I_ + nom du modèle
#                     elif cls_lower.startswith("i_") and model_lower in cls_lower:
#                         candidates.append(cls_name)
#                     # Priorité 3: contient le nom du modèle
#                     elif model_lower in cls_lower:
#                         candidates.append(cls_name)
#                     # Priorité 4: termine par Serializer ou Serializers
#                     elif cls_lower.endswith("serializer") or cls_lower.endswith("serializers"):
#                         candidates.append(cls_name)
#         except Exception as e:
#             print(f"Erreur lors de la lecture de {file_path}: {e}")
        
#         if candidates:
#             return candidates[0]
        
#         # Fallback: générer un nom par défaut
#         return f"J_{related_model_name}Serializers"

#     # -----------------------------
#     # Détection du chemin du serializer pour une relation
#     # -----------------------------
#     def get_related_serializer_info(self, field):
#         """Retourne le chemin d'import et le nom du serializer pour un champ relation"""
#         related_model = field.related_model
#         app_label = related_model._meta.app_label
#         model_name = related_model._meta.model_name
        
#         # Obtenir le chemin de l'application
#         app_config = apps.get_app_config(app_label)
#         app_path = Path(app_config.path)
        
#         # CAS SPÉCIAL: admin_user dans gestionUtilisateur
#         if app_label == 'gestionUtilisateur' and model_name == 'admin_user':
#             # Chercher dans gestionUtilisateur/modules/admin_user/
#             module_path = app_path / 'modules' / model_name
            
#             if not module_path.exists():
#                 # Créer le dossier s'il n'existe pas
#                 module_path.mkdir(parents=True, exist_ok=True)
            
#             # Détecter le fichier serializer
#             serializer_filename, serializer_filepath = self.detect_serializer_file(module_path)
            
#             if serializer_filename and serializer_filepath:
#                 # Détecter la classe
#                 serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
#                 # Nom du fichier sans extension
#                 module_name = serializer_filename.replace('.py', '')
#                 import_path = f"{app_label}.modules.{model_name}.{module_name}"
#                 return import_path, serializer_class
#             else:
#                 # Fichier non trouvé, utiliser valeurs par défaut
#                 import_path = f"{app_label}.modules.{model_name}.serializers"
#                 return import_path, f"J_{model_name}Serializers"
        
#         # CAS NORMAL: autres modèles
#         else:
#             # Chercher d'abord dans app_label/modules/model_name/
#             modules_model_path = app_path / 'modules' / model_name
            
#             if modules_model_path.exists():
#                 # Détecter le fichier serializer
#                 serializer_filename, serializer_filepath = self.detect_serializer_file(modules_model_path)
                
#                 if serializer_filename and serializer_filepath:
#                     # Détecter la classe
#                     serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
#                     # Nom du fichier sans extension
#                     module_name = serializer_filename.replace('.py', '')
#                     import_path = f"{app_label}.modules.{model_name}.{module_name}"
#                     return import_path, serializer_class
            
#             # Si pas trouvé dans modules/model_name, chercher dans app_label directement
#             serializer_filename, serializer_filepath = self.detect_serializer_file(app_path)
            
#             if serializer_filename and serializer_filepath:
#                 # Détecter la classe
#                 serializer_class = self.detect_serializer_class(serializer_filepath, model_name)
#                 # Nom du fichier sans extension
#                 module_name = serializer_filename.replace('.py', '')
#                 import_path = f"{app_label}.{module_name}"
#                 return import_path, serializer_class
            
#             # Si aucun fichier trouvé, utiliser valeurs par défaut
#             import_path = f"{app_label}.modules.{model_name}.serializers"
#             return import_path, f"J_{model_name}Serializers"

#     # -----------------------------
#     # Génération des expansions récursives
#     # -----------------------------
#     def generate_expansions(self, model, max_depth=6):
#         """Génère les expansions récursives pour permit_list_expands"""
#         expansions = []
#         filterset_fields = []
#         search_fields = []
        
#         def explore(model, prefix='', depth=0, visited=None):
#             if visited is None:
#                 visited = set()
            
#             if depth >= max_depth:
#                 return
            
#             model_key = f"{model._meta.app_label}.{model._meta.model_name}"
#             if model_key in visited:
#                 return
#             visited.add(model_key)
            
#             for field in model._meta.get_fields():
#                 if isinstance(field, (ForeignKey, OneToOneField)):
#                     dot_path = f"{prefix}{field.name}"
#                     expansions.append(dot_path)
#                     filterset_fields.append(dot_path.replace('.', '__'))
                    
#                     # Explorer le modèle lié
#                     if field.related_model:
#                         explore(field.related_model, f"{dot_path}.", depth + 1, visited.copy())
                
#                 # CharField pour search (uniquement au niveau racine)
#                 elif depth == 0 and isinstance(field, CharField) and not isinstance(field, TextField):
#                     search_fields.append(field.name)
        
#         explore(model)
#         return expansions, filterset_fields, search_fields

#     # -----------------------------
#     # Génération du fichier serializers.py
#     # -----------------------------
#     def generate_serializers(self, model, module_path, expansions):
#         """Génère le fichier serializers.py"""
#         model_name = model.__name__
        
#         # Détecter si le fichier existe déjà et son format
#         serializer_filename, _ = self.detect_serializer_file(module_path)
        
#         # Déterminer les noms des serializers en fonction du format existant
#         if serializer_filename and serializer_filename.endswith('.py'):
#             # Lire le fichier existant pour détecter le format
#             existing_file_path = module_path / serializer_filename
#             try:
#                 with open(existing_file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
                    
#                 # Détecter le format des noms de classe
#                 if f"J_{model_name}Serializers" in content:
#                     serializer_read = f"J_{model_name}Serializers"
#                     serializer_write = f"I_{model_name}Serializers"
#                 elif f"J_{model_name}Serializer" in content:
#                     serializer_read = f"J_{model_name}Serializer"
#                     serializer_write = f"I_{model_name}Serializer"
#                 else:
#                     # Par défaut
#                     serializer_read = f"J_{model_name}Serializers"
#                     serializer_write = f"I_{model_name}Serializers"
#             except:
#                 # En cas d'erreur, utiliser le format par défaut
#                 serializer_read = f"J_{model_name}Serializers"
#                 serializer_write = f"I_{model_name}Serializers"
#         else:
#             # Nouveau fichier, utiliser le format par défaut
#             serializer_read = f"J_{model_name}Serializers"
#             serializer_write = f"I_{model_name}Serializers"
        
#         # Préparer le contenu
#         content = [
#             "from rest_framework import serializers",
#             "from rest_flex_fields import FlexFieldsModelSerializer",
#             f"from .models import {model_name}",
#             ""
#         ]
        
#         # Collecter les imports des serializers liés
#         imports_set = set()
#         expandable_fields = {}
        
#         # Pour chaque relation, déterminer quel champ inclure dans expandable_fields
#         for field in model._meta.get_fields():
#             if isinstance(field, (ForeignKey, OneToOneField)):
#                 import_path, serializer_class = self.get_related_serializer_info(field)
                
#                 # Ajouter l'import
#                 import_line = f"from {import_path} import {serializer_class}"
#                 if import_line not in imports_set:
#                     # Insérer après les imports de base
#                     content.insert(len(content) - 1, import_line)
#                     imports_set.add(import_line)
                
#                 # Ajouter au expandable_fields
#                 expandable_fields[field.name] = serializer_class
        
#         # Réorganiser le contenu pour avoir les imports au début
#         imports = []
#         other_lines = []
        
#         for line in content:
#             if line.startswith("from ") or line.startswith("import "):
#                 imports.append(line)
#             else:
#                 other_lines.append(line)
        
#         # Trier les imports (optionnel, pour la lisibilité)
#         imports.sort()
        
#         # Reconstruire le contenu final
#         final_content = imports + other_lines
        
#         # Serializer Read (J_)
#         final_content.append(f"class {serializer_read}(FlexFieldsModelSerializer):")
        
#         # Ajouter les PrimaryKeyRelatedField pour les champs d'expansion
#         for field_name in expandable_fields.keys():
#             final_content.append(f"    {field_name} = serializers.PrimaryKeyRelatedField(read_only=True)")
        
#         final_content.extend([
#             "    class Meta:",
#             f"        model = {model_name}",
#             '        fields = "__all__"',
#         ])
        
#         if expandable_fields:
#             final_content.append("        expandable_fields = {")
#             for field_name, serializer in expandable_fields.items():
#                 final_content.append(f"            '{field_name}': {serializer},")
#             final_content.append("        }")
        
#         final_content.append("")
        
#         # Serializer Write (I_)
#         final_content.append(f"class {serializer_write}(FlexFieldsModelSerializer):")
#         final_content.extend([
#             "    class Meta:",
#             f"        model = {model_name}",
#             '        fields = "__all__"',
#         ])
        
#         # Écrire le fichier
#         # Utiliser le nom de fichier détecté ou "serializers.py" par défaut
#         output_filename = serializer_filename or "serializers.py"
#         file_path = module_path / output_filename
        
#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write("\n".join(final_content))
        
#         return serializer_read, serializer_write, output_filename.replace('.py', '')

#     # -----------------------------
#     # Génération du fichier filter.py
#     # -----------------------------
#     def generate_filter(self, model, module_path, filterset_fields):
#         """Génère le fichier filter.py"""
#         model_name = model.__name__
        
#         content = [
#             "import django_filters",
#             f"from .models import {model_name}",
#             "",
#             "",
#             f"class {model_name}Filter(django_filters.FilterSet):",
#         ]
        
#         # Ajouter les filtres de date pour les DateTimeField
#         for field in model._meta.get_fields():
#             if isinstance(field, DateTimeField):
#                 content.append(f'    {field.name}_date = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date")')
#                 content.append(f'    {field.name}_min = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date__gte")')
#                 content.append(f'    {field.name}_max = django_filters.DateFilter(field_name="{field.name}", lookup_expr="date__lte")')
        
#         content.extend([
#             "",
#             "    class Meta:",
#             f"        model = {model_name}",
#             "        fields = [",
#         ])
        
#         # Ajouter les champs de filtre
#         for field_name in filterset_fields:
#             content.append(f"            '{field_name}',")
        
#         content.extend([
#             "        ]",
#             "",
#         ])
        
#         # Écrire le fichier
#         file_path = module_path / "filter.py"
#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write("\n".join(content))

#     # -----------------------------
#     # Génération du fichier views.py
#     # -----------------------------
#     def generate_views(self, model, module_path, expansions, search_fields, serializer_read, serializer_write, serializer_module_name):
#         """Génère le fichier views.py"""
#         model_name = model.__name__
        
#         content = [
#             "from gestionUtilisateur.utils import DynamicExpandMixin, CustomPagination",
#             "from django_filters.rest_framework import DjangoFilterBackend as FB",
#             "from rest_flex_fields.views import FlexFieldsModelViewSet",
#             "from rest_framework.filters import SearchFilter as SF",
#             f"from .filter import {model_name}Filter",
#             f"from .models import {model_name}",
#             f"from .{serializer_module_name} import {serializer_read}, {serializer_write}",
#             "",
#             "",
#             f"class {model_name}APIView(DynamicExpandMixin, FlexFieldsModelViewSet):",
#             f"    queryset = {model_name}.objects.all().order_by('-id')",
#             f"    serializer_class_read = {serializer_read}",
#             f"    serializer_class_write = {serializer_write}",
#             "    filter_backends = [FB, SF]",
#             "    pagination_class = CustomPagination",
#             f"    filterset_class = {model_name}Filter",
#             "",
#             "    permit_list_expands = [",
#         ]
        
#         # Ajouter les expansions
#         for expand in expansions:
#             content.append(f"        '{expand}',")
        
#         content.extend([
#             "    ]",
#             "",
#             "    search_fields = [",
#         ])
        
#         # Ajouter les champs de recherche
#         for search in search_fields:
#             content.append(f"        '{search}',")
        
#         content.extend([
#             "    ]",
#             "",
#         ])
        
#         # Écrire le fichier
#         file_path = module_path / "views.py"
#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write("\n".join(content))

#     # -----------------------------
#     # Point d'entrée principal
#     # -----------------------------
#     def handle(self, *args, **options):
#         app_label = options['app_label']
#         model_name = options['model_name']
#         max_depth = options['max_depth']
        
#         # Récupérer le modèle
#         model = apps.get_model(app_label, model_name)
        
#         # Déterminer le chemin du module
#         app_config = apps.get_app_config(app_label)
#         app_path = Path(app_config.path)
        
#         # CAS SPÉCIAL : admin_user
#         if app_label == 'gestionUtilisateur' and model_name == 'admin_user':
#             module_path = app_path / 'modules' / model_name
#         else:
#             # Structure normale : app_label/modules/model_name/
#             module_path = app_path / 'modules' / model_name
        
#         # Créer le dossier s'il n'existe pas
#         module_path.mkdir(parents=True, exist_ok=True)
        
#         # Générer les listes d'expansions, filtres et recherche
#         expansions, filterset_fields, search_fields = self.generate_expansions(model, max_depth)
        
#         # Générer les fichiers
#         serializer_read, serializer_write, serializer_module_name = self.generate_serializers(model, module_path, expansions)
#         self.generate_filter(model, module_path, filterset_fields)
#         self.generate_views(model, module_path, expansions, search_fields, serializer_read, serializer_write, serializer_module_name)
        
#         # Afficher les résultats
#         self.stdout.write(self.style.SUCCESS(f"✅ Fichiers générés pour {model_name}"))
#         self.stdout.write(self.style.SUCCESS(f"📁 Dossier : {module_path}"))
#         self.stdout.write("")
#         self.stdout.write("📄 Fichiers créés/mis à jour :")
        
#         # Afficher les noms réels des fichiers
#         serializer_filename, _ = self.detect_serializer_file(module_path)
#         if serializer_filename:
#             self.stdout.write(f"  • {module_path / serializer_filename}")
#         else:
#             self.stdout.write(f"  • {module_path / 'serializers.py'}")
        
#         self.stdout.write(f"  • {module_path / 'views.py'}")
#         self.stdout.write(f"  • {module_path / 'filter.py'}")
#         self.stdout.write("")
#         self.stdout.write("🔍 Détection automatique :")
#         self.stdout.write(f"  • Fichier serializer détecté : {serializer_filename or 'Nouveau fichier créé'}")
#         self.stdout.write(f"  • Module serializer utilisé : {serializer_module_name}")
#         self.stdout.write(f"  • Classe de lecture : {serializer_read}")
#         self.stdout.write(f"  • Classe d'écriture : {serializer_write}")
#         self.stdout.write("")
#         self.stdout.write("📊 Statistiques :")
#         self.stdout.write(f"  • Expansions générées : {len(expansions)}")
#         self.stdout.write(f"  • Filtres générés : {len(filterset_fields)}")
#         self.stdout.write(f"  • Champs de recherche : {len(search_fields)}")
