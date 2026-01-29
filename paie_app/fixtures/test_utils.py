"""
Utilitaires pour faciliter l'utilisation des fixtures dans les tests.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from .base_fixtures import BaseFixtures
from .property_test_fixtures import PropertyTestFixtures

User = get_user_model()


class FixtureTestCase(TestCase):
    """Classe de base pour les tests utilisant les fixtures"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixtures = BaseFixtures()
        cls.fixture_data = cls.fixtures.create_all_fixtures()

    def get_user(self, email):
        """Récupère un utilisateur par email"""
        return self.fixture_data['users'].get(email)

    def get_employe(self, matricule):
        """Récupère un employé par matricule"""
        return self.fixture_data['employes'].get(matricule)

    def get_contrat(self, employe_matricule):
        """Récupère le contrat d'un employé"""
        return self.fixture_data['contrats'].get(employe_matricule)

    def get_periode(self, annee, mois):
        """Récupère une période de paie"""
        key = f"{annee}-{mois:02d}"
        return self.fixture_data['periodes'].get(key)

    def get_retenues_employe(self, employe_matricule):
        """Récupère toutes les retenues d'un employé"""
        return [
            retenue for key, retenue in self.fixture_data['retenues'].items()
            if key.startswith(employe_matricule)
        ]

    def get_active_employes(self):
        """Récupère tous les employés actifs"""
        return [
            emp for emp in self.fixture_data['employes'].values()
            if emp.statut_emploi == 'ACTIVE'
        ]

    def get_employes_with_retenues(self):
        """Récupère les employés qui ont des retenues"""
        employes_with_retenues = set()
        for retenue in self.fixture_data['retenues'].values():
            employes_with_retenues.add(retenue.employe_id)
        return list(employes_with_retenues)


class PropertyTestCase(TestCase):
    """Classe de base pour les tests de propriété avec données aléatoires"""

    def setUp(self):
        super().setUp()
        self.property_fixtures = PropertyTestFixtures()

    def create_random_dataset(self, **kwargs):
        """Crée un jeu de données aléatoire"""
        return self.property_fixtures.create_random_dataset(**kwargs)

    def create_minimal_dataset(self):
        """Crée un jeu de données minimal"""
        return self.property_fixtures.create_minimal_dataset()

    def create_large_dataset(self):
        """Crée un jeu de données volumineux"""
        return self.property_fixtures.create_large_dataset()


def get_test_user():
    """Crée ou récupère un utilisateur de test simple"""
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'nom': 'Test',
            'prenom': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    return user


def create_simple_employe_with_contrat():
    """Crée un employé simple avec contrat pour les tests rapides"""
    from decimal import Decimal
    from datetime import date
    from user_app.models import employe, contrat, service, poste

    # Créer service et poste
    service_obj, _ = service.objects.get_or_create(
        code='TEST',
        defaults={'titre': 'Service Test', 'description': 'Test'}
    )

    poste_obj, _ = poste.objects.get_or_create(
        code='TEST_POST',
        defaults={'titre': 'Poste Test', 'service_id': service_obj}
    )

    # Créer employé
    employe_obj = employe.objects.create(
        nom='Test',
        prenom='Employee',
        email_personnel='test.employee@test.com',
        date_naissance=date(1990, 1, 1),
        sexe='M',
        statut_matrimonial='S',
        nationalite='Congolaise',
        banque='Test Bank',
        numero_compte='TEST123',
        niveau_etude='Universitaire',
        numero_inss='INSS123',
        telephone_personnel='+243123456789',
        adresse_ligne1='Test Address',
        matricule='TEST001',
        poste_id=poste_obj,
        date_embauche=date(2020, 1, 1),
        statut_emploi='ACTIVE',
        nombre_enfants=1,
        nom_contact_urgence='Test Contact',
        lien_contact_urgence='Famille',
        telephone_contact_urgence='+243987654321'
    )

    # Créer contrat
    contrat_obj = contrat.objects.create(
        employe_id=employe_obj,
        type_contrat='PERMANENT',
        date_debut=date(2020, 1, 1),
        type_salaire='M',
        salaire_base=Decimal('500000'),
        devise='USD',
        indemnite_logement=Decimal('10'),
        indemnite_deplacement=Decimal('5'),
        prime_fonction=Decimal('8'),
        autre_avantage=Decimal('20000'),
        assurance_patronale=Decimal('3.5'),
        assurance_salariale=Decimal('3.5'),
        fpc_patronale=Decimal('0.2'),
        fpc_salariale=Decimal('0.2'),
        statut='en_cours'
    )

    return employe_obj, contrat_obj


class FixtureDataMixin:
    """Mixin pour accéder facilement aux données de fixtures"""

    def get_sample_employes(self, count=5):
        """Récupère un échantillon d'employés"""
        from user_app.models import employe
        return list(employe.objects.filter(statut_emploi='ACTIVE')[:count])

    def get_sample_contrats(self, count=5):
        """Récupère un échantillon de contrats"""
        from user_app.models import contrat
        return list(contrat.objects.filter(statut='en_cours')[:count])

    def get_sample_retenues(self, count=5):
        """Récupère un échantillon de retenues"""
        from paie_app.models import retenue_employe
        return list(retenue_employe.objects.filter(est_active=True)[:count])

    def get_sample_periodes(self, count=3):
        """Récupère un échantillon de périodes"""
        from paie_app.models import periode_paie
        return list(periode_paie.objects.all()[:count])

    def get_employe_with_high_salary(self):
        """Récupère un employé avec un salaire élevé"""
        from user_app.models import contrat
        contrat_obj = contrat.objects.filter(
            salaire_base__gte=1000000
        ).first()
        return contrat_obj.employe_id if contrat_obj else None

    def get_employe_with_children(self):
        """Récupère un employé avec des enfants"""
        from user_app.models import employe
        return employe.objects.filter(
            nombre_enfants__gt=0,
            statut_emploi='ACTIVE'
        ).first()

    def get_employe_with_retenues(self):
        """Récupère un employé qui a des retenues actives"""
        from paie_app.models import retenue_employe
        retenue = retenue_employe.objects.filter(est_active=True).first()
        return retenue.employe_id if retenue else None
