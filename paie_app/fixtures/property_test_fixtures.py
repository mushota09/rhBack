"""
Fixtures spécialisées pour les tests de propriété.
Génère des données aléatoires mais valides pour les tests property-based.
"""
import random
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from user_app.models import employe, contrat, service, poste
from paie_app.models import periode_paie, retenue_employe

User = get_user_model()


class PropertyTestFixtures:
    """Générateur de fixtures pour les tests de propriété"""

    def __init__(self, seed=None):
        if seed:
            random.seed(seed)

        self.first_names = [
            'Jean', 'Marie', 'Pierre', 'Sylvie', 'Joseph', 'Beatrice',
            'Michel', 'Francine', 'Andre', 'Rosine', 'Paul', 'Grace',
            'Emmanuel', 'Patience', 'Dieudonne', 'Esperance', 'Claude',
            'Jolie', 'Clement', 'Consolee'
        ]

        self.last_names = [
            'Mukendi', 'Kabongo', 'Tshimanga', 'Mbuyi', 'Kasongo',
            'Ngoy', 'Ilunga', 'Kalala', 'Mwamba', 'Katende', 'Lumumba',
            'Tshisekedi', 'Kabila', 'Mobutu', 'Kimbangu', 'Kasa-Vubu'
        ]

        self.post_names = [
            'Claude', 'Grace', 'Emmanuel', 'Patience', 'Dieudonne',
            'Esperance', 'Jolie', 'Clement', 'Consolee', 'Patient'
        ]

    def generate_random_employe(self, matricule_suffix=None):
        """Génère un employé aléatoire avec des données valides"""
        if not matricule_suffix:
            matricule_suffix = random.randint(1000, 9999)

        birth_year = random.randint(1970, 2000)
        hire_year = random.randint(max(birth_year + 18, 2010), 2024)

        return {
            'nom': random.choice(self.last_names),
            'prenom': random.choice(self.first_names),
            'postnom': random.choice(self.post_names),
            'email_personnel': f'employe{matricule_suffix}@test.com',
            'date_naissance': date(
                birth_year,
                random.randint(1, 12),
                random.randint(1, 28)
            ),
            'sexe': random.choice(['M', 'F']),
            'statut_matrimonial': random.choice(['S', 'M', 'D', 'W']),
            'nationalite': 'Congolaise',
            'banque': random.choice([
                'Banque Commerciale du Congo',
                'BCDC',
                'Equity Bank',
                'Rawbank'
            ]),
            'numero_compte': f"ACC{matricule_suffix}001",
            'niveau_etude': random.choice([
                'Primaire', 'Secondaire', 'Universitaire', 'Post-universitaire'
            ]),
            'numero_inss': f"INSS{matricule_suffix}",
            'telephone_personnel': f"+243{random.randint(800000000, 999999999)}",
            'adresse_ligne1': f"Avenue Test {matricule_suffix}, Kinshasa",
            'ville': 'Kinshasa',
            'province': 'Kinshasa',
            'pays': 'République Démocratique du Congo',
            'matricule': f"EMP{matricule_suffix}",
            'date_embauche': date(
                hire_year,
                random.randint(1, 12),
                random.randint(1, 28)
            ),
            'statut_emploi': random.choice(['ACTIVE', 'INACTIVE', 'SUSPENDED']),
            'nombre_enfants': random.randint(0, 6),
            'nom_contact_urgence': f"Contact {random.choice(self.first_names)}",
            'lien_contact_urgence': random.choice(['Famille', 'Ami', 'Collègue']),
            'telephone_contact_urgence': f"+243{random.randint(800000000, 999999999)}"
        }

    def generate_random_contrat(self, employe_obj):
        """Génère un contrat aléatoire pour un employé"""
        # Salaires réalistes selon les postes
        salaire_ranges = {
            'EXECUTIVE': (1500000, 3000000),
            'MANAGER': (800000, 1500000),
            'SENIOR': (500000, 800000),
            'JUNIOR': (300000, 500000),
            'ENTRY': (200000, 300000)
        }

        level = random.choice(list(salaire_ranges.keys()))
        min_sal, max_sal = salaire_ranges[level]

        return {
            'type_contrat': random.choice(['PERMANENT', 'TEMPORARY', 'CONSULTANT']),
            'date_debut': employe_obj.date_embauche,
            'date_fin': None if random.random() > 0.3 else date(2025, 12, 31),
            'type_salaire': 'M',
            'salaire_base': Decimal(str(random.randint(min_sal, max_sal))),
            'devise': 'USD',
            'indemnite_logement': Decimal(str(random.randint(5, 25))),
            'indemnite_deplacement': Decimal(str(random.randint(3, 20))),
            'prime_fonction': Decimal(str(random.randint(5, 30))),
            'autre_avantage': Decimal(str(random.randint(10000, 100000))),
            'assurance_patronale': Decimal('3.5'),
            'assurance_salariale': Decimal('3.5'),
            'fpc_patronale': Decimal('0.2'),
            'fpc_salariale': Decimal('0.2'),
            'statut': random.choice(['en_cours', 'suspendu', 'termine'])
        }

    def generate_random_retenue(self, employe_obj):
        """Génère une retenue aléatoire pour un employé"""
        type_retenue = random.choice(['LOAN', 'ADVANCE', 'FINE', 'INSURANCE', 'UNION', 'OTHER'])

        # Montants selon le type
        montant_ranges = {
            'LOAN': (50000, 300000),
            'ADVANCE': (30000, 150000),
            'FINE': (10000, 50000),
            'INSURANCE': (15000, 60000),
            'UNION': (5000, 25000),
            'OTHER': (20000, 100000)
        }

        min_montant, max_montant = montant_ranges[type_retenue]
        montant_mensuel = Decimal(str(random.randint(min_montant, max_montant)))

        # Montant total pour certains types
        montant_total = None
        if type_retenue in ['LOAN', 'ADVANCE', 'FINE']:
            multiplicateur = random.randint(3, 24)  # 3 à 24 mois
            montant_total = montant_mensuel * multiplicateur

        return {
            'type_retenue': type_retenue,
            'description': f'{type_retenue.title()} - {employe_obj.matricule}',
            'montant_mensuel': montant_mensuel,
            'montant_total': montant_total,
            'date_debut': date(2024, random.randint(1, 12), 1),
            'date_fin': date(2025, random.randint(1, 12), 28) if montant_total else None,
            'est_active': random.choice([True, True, True, False]),  # 75% actives
            'est_recurrente': random.choice([True, True, False]),  # 66% récurrentes
            'banque_beneficiaire': random.choice([
                'BCC', 'BCDC', 'Equity', 'Rawbank', ''
            ]) if type_retenue in ['LOAN', 'INSURANCE'] else '',
            'compte_beneficiaire': f"COMP-{type_retenue}-{random.randint(1000, 9999)}"
                                 if type_retenue in ['LOAN', 'INSURANCE'] else ''
        }

    def generate_random_periode(self, annee=None, mois=None):
        """Génère une période de paie aléatoire"""
        if not annee:
            annee = random.choice([2023, 2024, 2025])
        if not mois:
            mois = random.randint(1, 12)

        statuts_weights = [
            ('DRAFT', 0.2),
            ('PROCESSING', 0.1),
            ('COMPLETED', 0.3),
            ('FINALIZED', 0.2),
            ('APPROVED', 0.2)
        ]

        statut = random.choices(
            [s[0] for s in statuts_weights],
            weights=[s[1] for s in statuts_weights]
        )[0]

        return {
            'annee': annee,
            'mois': mois,
            'statut': statut,
            'nombre_employes': random.randint(5, 50),
            'masse_salariale_brute': Decimal(str(random.randint(5000000, 50000000))),
            'total_cotisations_patronales': Decimal(str(random.randint(500000, 5000000))),
            'total_cotisations_salariales': Decimal(str(random.randint(300000, 3000000))),
            'total_net_a_payer': Decimal(str(random.randint(4000000, 40000000)))
        }

    def create_random_dataset(self, num_employes=10, num_retenues_per_employe=2):
        """Crée un jeu de données aléatoire complet"""
        # Créer un utilisateur de test
        user = User.objects.create(
            email=f'test{random.randint(1000, 9999)}@test.com',
            nom='Test',
            prenom='User'
        )
        user.set_password('testpass123')
        user.save()

        # Créer un service et poste de base
        service_obj = service.objects.create(
            titre='Service Test',
            code=f'TEST{random.randint(100, 999)}',
            description='Service de test'
        )

        poste_obj = poste.objects.create(
            titre='Poste Test',
            code=f'POST{random.randint(100, 999)}',
            service_id=service_obj
        )

        employes_created = []
        contrats_created = []
        retenues_created = []

        # Créer les employés et leurs contrats
        for i in range(num_employes):
            emp_data = self.generate_random_employe(1000 + i)
            employe_obj = employe.objects.create(
                poste_id=poste_obj,
                email_professionnel=f"test{1000 + i}@company.com",  # Unique email
                **emp_data
            )
            employes_created.append(employe_obj)

            # Créer un contrat pour chaque employé
            contrat_data = self.generate_random_contrat(employe_obj)
            contrat_obj = contrat.objects.create(
                employe_id=employe_obj,
                **contrat_data
            )
            contrats_created.append(contrat_obj)

            # Créer des retenues pour chaque employé
            for j in range(random.randint(0, num_retenues_per_employe)):
                retenue_data = self.generate_random_retenue(employe_obj)
                retenue_obj = retenue_employe.objects.create(
                    employe_id=employe_obj,
                    cree_par=user,
                    **retenue_data
                )
                retenues_created.append(retenue_obj)

        # Créer quelques périodes de paie
        periodes_created = []
        for annee in [2023, 2024]:
            for mois in random.sample(range(1, 13), 6):  # 6 mois aléatoires
                periode_data = self.generate_random_periode(annee, mois)
                try:
                    periode_obj = periode_paie.objects.create(
                        traite_par=user if periode_data['statut'] != 'DRAFT' else None,
                        **periode_data
                    )
                    periodes_created.append(periode_obj)
                except Exception:
                    # Ignorer les doublons (même année/mois)
                    pass

        return {
            'user': user,
            'service': service_obj,
            'poste': poste_obj,
            'employes': employes_created,
            'contrats': contrats_created,
            'retenues': retenues_created,
            'periodes': periodes_created
        }

    def create_minimal_dataset(self):
        """Crée un jeu de données minimal pour les tests rapides"""
        return self.create_random_dataset(num_employes=3, num_retenues_per_employe=1)

    def create_large_dataset(self):
        """Crée un jeu de données volumineux pour les tests de performance"""
        return self.create_random_dataset(num_employes=50, num_retenues_per_employe=3)
