"""
Commande Django pour charger les fixtures du système de paie.
Usage: python manage.py load_paie_fixtures [--clear]
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model

from paie_app.fixtures.base_fixtures import BaseFixtures
from paie_app.models import periode_paie, retenue_employe, Alert
from user_app.models import employe, contrat, service, poste

User = get_user_model()


class Command(BaseCommand):
    help = 'Charge les fixtures de test pour le système de paie'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant de charger les fixtures',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affiche des informations détaillées pendant le chargement',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(
                self.style.WARNING('Suppression des données existantes...')
            )
            self.clear_existing_data()

        try:
            with transaction.atomic():
                fixtures = BaseFixtures()

                if verbose:
                    self.stdout.write('Chargement des fixtures...')

                data = fixtures.create_all_fixtures()

                # Affichage des statistiques
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixtures chargées avec succès!\n'
                        f'- Utilisateurs: {len(data["users"])}\n'
                        f'- Services: {len(data["services"])}\n'
                        f'- Postes: {len(data["postes"])}\n'
                        f'- Employés: {len(data["employes"])}\n'
                        f'- Contrats: {len(data["contrats"])}\n'
                        f'- Périodes de paie: {len(data["periodes"])}\n'
                        f'- Retenues: {len(data["retenues"])}\n'
                        f'- Alertes: {len(data["alerts"])}'
                    )
                )

                if verbose:
                    self.display_detailed_info(data)

        except Exception as e:
            raise CommandError(f'Erreur lors du chargement des fixtures: {str(e)}')

    def clear_existing_data(self):
        """Supprime toutes les données existantes"""
        models_to_clear = [
            Alert,
            retenue_employe,
            periode_paie,
            contrat,
            employe,
            poste,
            service,
        ]

        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  - {model.__name__}: {count} enregistrements supprimés')

        # Supprimer les utilisateurs non-superuser
        user_count = User.objects.filter(is_superuser=False).count()
        if user_count > 0:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'  - Users (non-superuser): {user_count} enregistrements supprimés')

    def display_detailed_info(self, data):
        """Affiche des informations détaillées sur les données créées"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('DÉTAILS DES FIXTURES CRÉÉES')
        self.stdout.write('='*50)

        # Utilisateurs
        self.stdout.write('\nUTILISATEURS:')
        for email, user in data['users'].items():
            role = 'Superuser' if user.is_superuser else 'Staff' if user.is_staff else 'User'
            self.stdout.write(f'  - {user.get_full_name()} ({email}) - {role}')

        # Employés par service
        self.stdout.write('\nEMPLOYÉS PAR SERVICE:')
        for service_code, service_obj in data['services'].items():
            employes_service = [
                emp for emp in data['employes'].values()
                if emp.poste_id and emp.poste_id.service_id == service_obj
            ]
            self.stdout.write(f'  - {service_obj.titre}: {len(employes_service)} employés')

        # Contrats par type
        self.stdout.write('\nCONTRATS PAR TYPE:')
        contrat_types = {}
        for contrat_obj in data['contrats'].values():
            type_contrat = contrat_obj.type_contrat
            contrat_types[type_contrat] = contrat_types.get(type_contrat, 0) + 1

        for type_contrat, count in contrat_types.items():
            self.stdout.write(f'  - {type_contrat}: {count} contrats')

        # Retenues par type
        self.stdout.write('\nRETENUES PAR TYPE:')
        retenue_types = {}
        for retenue_obj in data['retenues'].values():
            type_retenue = retenue_obj.type_retenue
            retenue_types[type_retenue] = retenue_types.get(type_retenue, 0) + 1

        for type_retenue, count in retenue_types.items():
            self.stdout.write(f'  - {type_retenue}: {count} retenues')

        # Périodes par statut
        self.stdout.write('\nPÉRIODES PAR STATUT:')
        periode_statuts = {}
        for periode_obj in data['periodes'].values():
            statut = periode_obj.statut
            periode_statuts[statut] = periode_statuts.get(statut, 0) + 1

        for statut, count in periode_statuts.items():
            self.stdout.write(f'  - {statut}: {count} périodes')

        # Alertes par sévérité
        self.stdout.write('\nALERTES PAR SÉVÉRITÉ:')
        alert_severities = {}
        for alert_obj in data['alerts'].values():
            severity = alert_obj.severity
            alert_severities[severity] = alert_severities.get(severity, 0) + 1

        for severity, count in alert_severities.items():
            self.stdout.write(f'  - {severity}: {count} alertes')

        self.stdout.write('\n' + '='*50)
