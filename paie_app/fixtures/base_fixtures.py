"""
Fixtures de base pour les tests du système de paie.
Crée des employés avec différents profils, contrats et retenues.
"""
from decimal import Decimal
from datetime import date, datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

from user_app.models import employe, contrat, service, poste
from paie_app.models import periode_paie, retenue_employe, Alert

User = get_user_model()


class BaseFixtures:
    """Classe pour créer les fixtures de base"""

    def __init__(self):
        self.users = {}
        self.services = {}
        self.postes = {}
        self.employes = {}
        self.contrats = {}
        self.periodes = {}
        self.retenues = {}
        self.alerts = {}

    def create_users(self):
        """Crée des utilisateurs de test"""
        users_data = [
            {
                'email': 'admin@company.com',
                'nom': 'Admin',
                'prenom': 'System',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'hr.manager@company.com',
                'nom': 'Manager',
                'prenom': 'HR',
                'is_staff': True
            },
            {
                'email': 'payroll.clerk@company.com',
                'nom': 'Clerk',
                'prenom': 'Payroll',
                'is_staff': True
            },
            {
                'email': 'supervisor@company.com',
                'nom': 'Supervisor',
                'prenom': 'Department',
                'is_staff': False
            }
        ]

        for user_data in users_data:
            user = User.objects.create(
                email=user_data['email'],
                nom=user_data['nom'],
                prenom=user_data['prenom'],
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False)
            )
            user.set_password('testpass123')
            user.save()
            self.users[user_data['email']] = user

        return self.users

    def create_services_and_postes(self):
        """Crée les services et postes"""
        services_data = [
            {'titre': 'Direction Générale', 'code': 'DG', 'description': 'Direction générale'},
            {'titre': 'Ressources Humaines', 'code': 'RH', 'description': 'Service RH'},
            {'titre': 'Comptabilité', 'code': 'COMPTA', 'description': 'Service comptabilité'},
            {'titre': 'Informatique', 'code': 'IT', 'description': 'Service informatique'},
            {'titre': 'Commercial', 'code': 'COMM', 'description': 'Service commercial'},
            {'titre': 'Production', 'code': 'PROD', 'description': 'Service production'}
        ]

        for service_data in services_data:
            service_obj = service.objects.create(**service_data)
            self.services[service_data['code']] = service_obj

        postes_data = [
            {'titre': 'Directeur Général', 'code': 'DG', 'service': 'DG'},
            {'titre': 'Responsable RH', 'code': 'RH_RESP', 'service': 'RH'},
            {'titre': 'Assistant RH', 'code': 'RH_ASS', 'service': 'RH'},
            {'titre': 'Comptable', 'code': 'COMPTA', 'service': 'COMPTA'},
            {'titre': 'Développeur Senior', 'code': 'DEV_SR', 'service': 'IT'},
            {'titre': 'Développeur Junior', 'code': 'DEV_JR', 'service': 'IT'},
            {'titre': 'Commercial Senior', 'code': 'COMM_SR', 'service': 'COMM'},
            {'titre': 'Technicien', 'code': 'TECH', 'service': 'PROD'},
            {'titre': 'Ouvrier', 'code': 'OUVR', 'service': 'PROD'}
        ]

        for poste_data in postes_data:
            service_obj = self.services[poste_data['service']]
            poste_obj = poste.objects.create(
                titre=poste_data['titre'],
                code=poste_data['code'],
                service_id=service_obj
            )
            self.postes[poste_data['code']] = poste_obj

        return self.services, self.postes

    def create_employes(self):
        """Crée des employés avec différents profils"""
        employes_data = [
            {
                'nom': 'Mukendi',
                'prenom': 'Jean',
                'postnom': 'Claude',
                'email_personnel': 'jean.mukendi@email.com',
                'date_naissance': date(1980, 5, 15),
                'sexe': 'M',
                'statut_matrimonial': 'M',
                'nationalite': 'Congolaise',
                'date_embauche': date(2015, 1, 15),
                'nombre_enfants': 3,
                'poste': 'DG',
                'matricule': 'EMP001',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Kabongo',
                'prenom': 'Marie',
                'postnom': 'Grace',
                'email_personnel': 'marie.kabongo@email.com',
                'date_naissance': date(1985, 8, 22),
                'sexe': 'F',
                'statut_matrimonial': 'M',
                'nationalite': 'Congolaise',
                'date_embauche': date(2018, 3, 1),
                'nombre_enfants': 2,
                'poste': 'RH_RESP',
                'matricule': 'EMP002',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Tshimanga',
                'prenom': 'Pierre',
                'postnom': 'Emmanuel',
                'email_personnel': 'pierre.tshimanga@email.com',
                'date_naissance': date(1990, 12, 10),
                'sexe': 'M',
                'statut_matrimonial': 'S',
                'nationalite': 'Congolaise',
                'date_embauche': date(2020, 6, 15),
                'nombre_enfants': 0,
                'poste': 'DEV_SR',
                'matricule': 'EMP003',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Mbuyi',
                'prenom': 'Sylvie',
                'postnom': 'Patience',
                'email_personnel': 'sylvie.mbuyi@email.com',
                'date_naissance': date(1992, 4, 8),
                'sexe': 'F',
                'statut_matrimonial': 'S',
                'nationalite': 'Congolaise',
                'date_embauche': date(2021, 9, 1),
                'nombre_enfants': 1,
                'poste': 'DEV_JR',
                'matricule': 'EMP004',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Kasongo',
                'prenom': 'Joseph',
                'postnom': 'Dieudonne',
                'email_personnel': 'joseph.kasongo@email.com',
                'date_naissance': date(1975, 11, 30),
                'sexe': 'M',
                'statut_matrimonial': 'M',
                'nationalite': 'Congolaise',
                'date_embauche': date(2010, 4, 1),
                'nombre_enfants': 5,
                'poste': 'COMPTA',
                'matricule': 'EMP005',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Ngoy',
                'prenom': 'Beatrice',
                'postnom': 'Esperance',
                'email_personnel': 'beatrice.ngoy@email.com',
                'date_naissance': date(1988, 7, 18),
                'sexe': 'F',
                'statut_matrimonial': 'D',
                'nationalite': 'Congolaise',
                'date_embauche': date(2019, 2, 15),
                'nombre_enfants': 2,
                'poste': 'COMM_SR',
                'matricule': 'EMP006',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Ilunga',
                'prenom': 'Michel',
                'postnom': 'Patient',
                'email_personnel': 'michel.ilunga@email.com',
                'date_naissance': date(1995, 3, 25),
                'sexe': 'M',
                'statut_matrimonial': 'S',
                'nationalite': 'Congolaise',
                'date_embauche': date(2022, 1, 10),
                'nombre_enfants': 0,
                'poste': 'TECH',
                'matricule': 'EMP007',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Kalala',
                'prenom': 'Francine',
                'postnom': 'Jolie',
                'email_personnel': 'francine.kalala@email.com',
                'date_naissance': date(1987, 9, 12),
                'sexe': 'F',
                'statut_matrimonial': 'M',
                'nationalite': 'Congolaise',
                'date_embauche': date(2017, 8, 1),
                'nombre_enfants': 4,
                'poste': 'RH_ASS',
                'matricule': 'EMP008',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Mwamba',
                'prenom': 'Andre',
                'postnom': 'Clement',
                'email_personnel': 'andre.mwamba@email.com',
                'date_naissance': date(1983, 1, 5),
                'sexe': 'M',
                'statut_matrimonial': 'M',
                'nationalite': 'Congolaise',
                'date_embauche': date(2016, 11, 15),
                'nombre_enfants': 3,
                'poste': 'OUVR',
                'matricule': 'EMP009',
                'statut_emploi': 'ACTIVE'
            },
            {
                'nom': 'Katende',
                'prenom': 'Rosine',
                'postnom': 'Consolee',
                'email_personnel': 'rosine.katende@email.com',
                'date_naissance': date(1991, 6, 20),
                'sexe': 'F',
                'statut_matrimonial': 'S',
                'nationalite': 'Congolaise',
                'date_embauche': date(2023, 5, 1),
                'nombre_enfants': 0,
                'poste': 'DEV_JR',
                'matricule': 'EMP010',
                'statut_emploi': 'SUSPENDED'  # Employé suspendu pour tests
            }
        ]

        for emp_data in employes_data:
            poste_obj = self.postes[emp_data['poste']]
            employe_obj = employe.objects.create(
                nom=emp_data['nom'],
                prenom=emp_data['prenom'],
                postnom=emp_data.get('postnom', ''),
                email_personnel=emp_data['email_personnel'],
                email_professionnel=f"{emp_data['matricule'].lower()}@company.com",  # Unique email
                date_naissance=emp_data['date_naissance'],
                sexe=emp_data['sexe'],
                statut_matrimonial=emp_data['statut_matrimonial'],
                nationalite=emp_data['nationalite'],
                banque='Banque Commerciale du Congo',
                numero_compte=f"BCC{emp_data['matricule']}001",
                niveau_etude='Universitaire',
                numero_inss=f"INSS{emp_data['matricule']}",
                telephone_personnel=f"+243{emp_data['matricule'][-3:]}123456",
                adresse_ligne1=f"Avenue {emp_data['nom']}, Kinshasa",
                ville='Kinshasa',
                province='Kinshasa',
                pays='République Démocratique du Congo',
                matricule=emp_data['matricule'],
                poste_id=poste_obj,
                date_embauche=emp_data['date_embauche'],
                statut_emploi=emp_data['statut_emploi'],
                nombre_enfants=emp_data['nombre_enfants'],
                nom_contact_urgence=f"Contact {emp_data['nom']}",
                lien_contact_urgence='Famille',
                telephone_contact_urgence=f"+243{emp_data['matricule'][-3:]}654321"
            )
            self.employes[emp_data['matricule']] = employe_obj

        return self.employes
    def create_contrats(self):
        """Crée des contrats avec différentes configurations"""
        contrats_data = [
            {
                'employe': 'EMP001',  # Directeur Général
                'type_contrat': 'PERMANENT',
                'date_debut': date(2015, 1, 15),
                'type_salaire': 'M',
                'salaire_base': Decimal('2000000'),  # 2M USD
                'devise': 'USD',
                'indemnite_logement': Decimal('25'),  # 25%
                'indemnite_deplacement': Decimal('15'),  # 15%
                'prime_fonction': Decimal('30'),  # 30%
                'autre_avantage': Decimal('100000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP002',  # Responsable RH
                'type_contrat': 'PERMANENT',
                'date_debut': date(2018, 3, 1),
                'type_salaire': 'M',
                'salaire_base': Decimal('1200000'),  # 1.2M USD
                'devise': 'USD',
                'indemnite_logement': Decimal('20'),
                'indemnite_deplacement': Decimal('10'),
                'prime_fonction': Decimal('20'),
                'autre_avantage': Decimal('50000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP003',  # Développeur Senior
                'type_contrat': 'PERMANENT',
                'date_debut': date(2020, 6, 15),
                'type_salaire': 'M',
                'salaire_base': Decimal('800000'),  # 800K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('15'),
                'indemnite_deplacement': Decimal('5'),
                'prime_fonction': Decimal('15'),
                'autre_avantage': Decimal('30000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP004',  # Développeur Junior
                'type_contrat': 'PERMANENT',
                'date_debut': date(2021, 9, 1),
                'type_salaire': 'M',
                'salaire_base': Decimal('500000'),  # 500K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('10'),
                'indemnite_deplacement': Decimal('5'),
                'prime_fonction': Decimal('10'),
                'autre_avantage': Decimal('20000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP005',  # Comptable
                'type_contrat': 'PERMANENT',
                'date_debut': date(2010, 4, 1),
                'type_salaire': 'M',
                'salaire_base': Decimal('700000'),  # 700K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('15'),
                'indemnite_deplacement': Decimal('8'),
                'prime_fonction': Decimal('12'),
                'autre_avantage': Decimal('25000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP006',  # Commercial Senior
                'type_contrat': 'PERMANENT',
                'date_debut': date(2019, 2, 15),
                'type_salaire': 'M',
                'salaire_base': Decimal('600000'),  # 600K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('12'),
                'indemnite_deplacement': Decimal('20'),  # Plus élevé pour commercial
                'prime_fonction': Decimal('25'),  # Commission élevée
                'autre_avantage': Decimal('40000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP007',  # Technicien
                'type_contrat': 'TEMPORARY',  # Contrat temporaire
                'date_debut': date(2022, 1, 10),
                'date_fin': date(2024, 12, 31),
                'type_salaire': 'M',
                'salaire_base': Decimal('400000'),  # 400K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('8'),
                'indemnite_deplacement': Decimal('5'),
                'prime_fonction': Decimal('5'),
                'autre_avantage': Decimal('15000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP008',  # Assistant RH
                'type_contrat': 'PERMANENT',
                'date_debut': date(2017, 8, 1),
                'type_salaire': 'M',
                'salaire_base': Decimal('450000'),  # 450K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('10'),
                'indemnite_deplacement': Decimal('5'),
                'prime_fonction': Decimal('8'),
                'autre_avantage': Decimal('18000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP009',  # Ouvrier
                'type_contrat': 'PERMANENT',
                'date_debut': date(2016, 11, 15),
                'type_salaire': 'M',
                'salaire_base': Decimal('300000'),  # 300K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('5'),
                'indemnite_deplacement': Decimal('3'),
                'prime_fonction': Decimal('5'),
                'autre_avantage': Decimal('10000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'en_cours'
            },
            {
                'employe': 'EMP010',  # Employé suspendu - contrat inactif
                'type_contrat': 'PERMANENT',
                'date_debut': date(2023, 5, 1),
                'type_salaire': 'M',
                'salaire_base': Decimal('480000'),  # 480K USD
                'devise': 'USD',
                'indemnite_logement': Decimal('10'),
                'indemnite_deplacement': Decimal('5'),
                'prime_fonction': Decimal('8'),
                'autre_avantage': Decimal('20000'),
                'assurance_patronale': Decimal('3.5'),
                'assurance_salariale': Decimal('3.5'),
                'fpc_patronale': Decimal('0.2'),
                'fpc_salariale': Decimal('0.2'),
                'statut': 'suspendu'  # Contrat suspendu
            }
        ]

        for contrat_data in contrats_data:
            employe_obj = self.employes[contrat_data['employe']]
            contrat_obj = contrat.objects.create(
                employe_id=employe_obj,
                type_contrat=contrat_data['type_contrat'],
                date_debut=contrat_data['date_debut'],
                date_fin=contrat_data.get('date_fin'),
                type_salaire=contrat_data['type_salaire'],
                salaire_base=contrat_data['salaire_base'],
                devise=contrat_data['devise'],
                indemnite_logement=contrat_data['indemnite_logement'],
                indemnite_deplacement=contrat_data['indemnite_deplacement'],
                prime_fonction=contrat_data['prime_fonction'],
                autre_avantage=contrat_data['autre_avantage'],
                assurance_patronale=contrat_data['assurance_patronale'],
                assurance_salariale=contrat_data['assurance_salariale'],
                fpc_patronale=contrat_data['fpc_patronale'],
                fpc_salariale=contrat_data['fpc_salariale'],
                statut=contrat_data['statut']
            )
            self.contrats[contrat_data['employe']] = contrat_obj

        return self.contrats

    def create_periodes_paie(self):
        """Crée des périodes de paie de test"""
        periodes_data = [
            {
                'annee': 2024,
                'mois': 1,
                'statut': 'APPROVED',
                'traite_par': 'hr.manager@company.com',
                'approuve_par': 'admin@company.com',
                'date_traitement': timezone.make_aware(datetime(2024, 2, 1, 10, 0, 0)),
                'date_approbation': timezone.make_aware(datetime(2024, 2, 2, 14, 30, 0))
            },
            {
                'annee': 2024,
                'mois': 2,
                'statut': 'COMPLETED',
                'traite_par': 'hr.manager@company.com',
                'date_traitement': timezone.make_aware(datetime(2024, 3, 1, 9, 30, 0))
            },
            {
                'annee': 2024,
                'mois': 3,
                'statut': 'PROCESSING',
                'traite_par': 'payroll.clerk@company.com'
            },
            {
                'annee': 2024,
                'mois': 4,
                'statut': 'DRAFT'
            },
            {
                'annee': 2024,
                'mois': 5,
                'statut': 'DRAFT'
            }
        ]

        for periode_data in periodes_data:
            traite_par = None
            if periode_data.get('traite_par'):
                traite_par = self.users[periode_data['traite_par']]

            approuve_par = None
            if periode_data.get('approuve_par'):
                approuve_par = self.users[periode_data['approuve_par']]

            periode = periode_paie.objects.create(
                annee=periode_data['annee'],
                mois=periode_data['mois'],
                statut=periode_data['statut'],
                traite_par=traite_par,
                approuve_par=approuve_par,
                date_traitement=periode_data.get('date_traitement'),
                date_approbation=periode_data.get('date_approbation')
            )
            key = f"{periode_data['annee']}-{periode_data['mois']:02d}"
            self.periodes[key] = periode

        return self.periodes

    def create_retenues(self):
        """Crée des retenues de test avec différents types"""
        retenues_data = [
            {
                'employe': 'EMP001',
                'type_retenue': 'LOAN',
                'description': 'Prêt véhicule de fonction',
                'montant_mensuel': Decimal('150000'),
                'montant_total': Decimal('1800000'),
                'date_debut': date(2024, 1, 1),
                'date_fin': date(2025, 12, 31),
                'est_active': True,
                'est_recurrente': True,
                'banque_beneficiaire': 'Banque Commerciale du Congo',
                'compte_beneficiaire': 'BCC-LOAN-001'
            },
            {
                'employe': 'EMP002',
                'type_retenue': 'ADVANCE',
                'description': 'Avance sur salaire - urgence familiale',
                'montant_mensuel': Decimal('100000'),
                'montant_total': Decimal('500000'),
                'date_debut': date(2024, 2, 1),
                'date_fin': date(2024, 6, 30),
                'est_active': True,
                'est_recurrente': True
            },
            {
                'employe': 'EMP003',
                'type_retenue': 'INSURANCE',
                'description': 'Assurance vie complémentaire',
                'montant_mensuel': Decimal('25000'),
                'date_debut': date(2024, 1, 1),
                'est_active': True,
                'est_recurrente': True,
                'banque_beneficiaire': 'SONAS',
                'compte_beneficiaire': 'SONAS-VIE-003'
            },
            {
                'employe': 'EMP004',
                'type_retenue': 'UNION',
                'description': 'Cotisation syndicale',
                'montant_mensuel': Decimal('15000'),
                'date_debut': date(2024, 1, 1),
                'est_active': True,
                'est_recurrente': True
            },
            {
                'employe': 'EMP005',
                'type_retenue': 'LOAN',
                'description': 'Prêt immobilier',
                'montant_mensuel': Decimal('200000'),
                'montant_total': Decimal('4800000'),
                'date_debut': date(2023, 6, 1),
                'date_fin': date(2025, 5, 31),
                'est_active': True,
                'est_recurrente': True,
                'banque_beneficiaire': 'BCDC',
                'compte_beneficiaire': 'BCDC-IMMO-005'
            },
            {
                'employe': 'EMP006',
                'type_retenue': 'FINE',
                'description': 'Pénalité retard répétés',
                'montant_mensuel': Decimal('30000'),
                'montant_total': Decimal('90000'),
                'date_debut': date(2024, 3, 1),
                'date_fin': date(2024, 5, 31),
                'est_active': True,
                'est_recurrente': True
            },
            {
                'employe': 'EMP007',
                'type_retenue': 'ADVANCE',
                'description': 'Avance formation professionnelle',
                'montant_mensuel': Decimal('50000'),
                'montant_total': Decimal('300000'),
                'date_debut': date(2024, 1, 1),
                'date_fin': date(2024, 6, 30),
                'est_active': True,
                'est_recurrente': True
            },
            {
                'employe': 'EMP008',
                'type_retenue': 'OTHER',
                'description': 'Remboursement matériel informatique',
                'montant_mensuel': Decimal('40000'),
                'montant_total': Decimal('240000'),
                'date_debut': date(2024, 2, 1),
                'date_fin': date(2024, 7, 31),
                'est_active': True,
                'est_recurrente': True
            },
            {
                'employe': 'EMP009',
                'type_retenue': 'INSURANCE',
                'description': 'Assurance maladie famille',
                'montant_mensuel': Decimal('35000'),
                'date_debut': date(2024, 1, 1),
                'est_active': True,
                'est_recurrente': True,
                'banque_beneficiaire': 'SONAS',
                'compte_beneficiaire': 'SONAS-MALADIE-009'
            },
            {
                'employe': 'EMP010',
                'type_retenue': 'LOAN',
                'description': 'Prêt équipement - INACTIF',
                'montant_mensuel': Decimal('60000'),
                'montant_total': Decimal('360000'),
                'date_debut': date(2024, 1, 1),
                'date_fin': date(2024, 6, 30),
                'est_active': False,  # Retenue inactive
                'est_recurrente': True
            }
        ]

        for retenue_data in retenues_data:
            employe_obj = self.employes[retenue_data['employe']]
            cree_par = self.users['hr.manager@company.com']

            retenue = retenue_employe.objects.create(
                employe_id=employe_obj,
                type_retenue=retenue_data['type_retenue'],
                description=retenue_data['description'],
                montant_mensuel=retenue_data['montant_mensuel'],
                montant_total=retenue_data.get('montant_total'),
                date_debut=retenue_data['date_debut'],
                date_fin=retenue_data.get('date_fin'),
                est_active=retenue_data['est_active'],
                est_recurrente=retenue_data['est_recurrente'],
                cree_par=cree_par,
                banque_beneficiaire=retenue_data.get('banque_beneficiaire', ''),
                compte_beneficiaire=retenue_data.get('compte_beneficiaire', '')
            )
            key = f"{retenue_data['employe']}-{retenue_data['type_retenue']}"
            self.retenues[key] = retenue

        return self.retenues

    def create_alerts(self):
        """Crée des alertes de test"""
        alerts_data = [
            {
                'alert_type': 'CONTRACT_MISSING',
                'severity': 'HIGH',
                'status': 'ACTIVE',
                'title': 'Contrat manquant pour employé suspendu',
                'message': 'L\'employé EMP010 est suspendu mais son contrat est toujours actif',
                'employe': 'EMP010',
                'created_by': 'hr.manager@company.com'
            },
            {
                'alert_type': 'DEDUCTION_ERROR',
                'severity': 'MEDIUM',
                'status': 'ACKNOWLEDGED',
                'title': 'Retenue inactive détectée',
                'message': 'Une retenue inactive a été trouvée pour EMP010',
                'employe': 'EMP010',
                'created_by': 'payroll.clerk@company.com',
                'acknowledged_by': 'hr.manager@company.com',
                'acknowledged_at': timezone.make_aware(datetime(2024, 3, 15, 10, 30, 0))
            },
            {
                'alert_type': 'REGULATORY_COMPLIANCE',
                'severity': 'CRITICAL',
                'status': 'ACTIVE',
                'title': 'Plafond INSS dépassé',
                'message': 'Le salaire du directeur général dépasse les plafonds INSS',
                'employe': 'EMP001',
                'created_by': 'payroll.clerk@company.com'
            },
            {
                'alert_type': 'PERIOD_PROCESSING',
                'severity': 'LOW',
                'status': 'RESOLVED',
                'title': 'Période mars en cours de traitement',
                'message': 'La période mars 2024 est en cours de traitement depuis plus de 2 heures',
                'periode_paie': '2024-03',
                'created_by': 'payroll.clerk@company.com',
                'resolved_by': 'hr.manager@company.com',
                'resolved_at': timezone.make_aware(datetime(2024, 3, 20, 16, 45, 0))
            },
            {
                'alert_type': 'VALIDATION_ERROR',
                'severity': 'MEDIUM',
                'status': 'ACTIVE',
                'title': 'Erreur de validation salaire',
                'message': 'Erreur dans le calcul des cotisations pour plusieurs employés',
                'periode_paie': '2024-03',
                'created_by': 'payroll.clerk@company.com'
            }
        ]

        for alert_data in alerts_data:
            employe_obj = None
            if alert_data.get('employe'):
                employe_obj = self.employes[alert_data['employe']]

            periode_obj = None
            if alert_data.get('periode_paie'):
                periode_obj = self.periodes[alert_data['periode_paie']]

            created_by = self.users[alert_data['created_by']]
            acknowledged_by = None
            if alert_data.get('acknowledged_by'):
                acknowledged_by = self.users[alert_data['acknowledged_by']]

            resolved_by = None
            if alert_data.get('resolved_by'):
                resolved_by = self.users[alert_data['resolved_by']]

            alert = Alert.objects.create(
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                status=alert_data['status'],
                title=alert_data['title'],
                message=alert_data['message'],
                employe_id=employe_obj,
                periode_paie_id=periode_obj,
                created_by=created_by,
                acknowledged_by=acknowledged_by,
                acknowledged_at=alert_data.get('acknowledged_at'),
                resolved_by=resolved_by,
                resolved_at=alert_data.get('resolved_at')
            )
            key = f"{alert_data['alert_type']}-{alert.id}"
            self.alerts[key] = alert

        return self.alerts

    def create_all_fixtures(self):
        """Crée toutes les fixtures en une seule fois"""
        print("Création des utilisateurs...")
        self.create_users()

        print("Création des services et postes...")
        self.create_services_and_postes()

        print("Création des employés...")
        self.create_employes()

        print("Création des contrats...")
        self.create_contrats()

        print("Création des périodes de paie...")
        self.create_periodes_paie()

        print("Création des retenues...")
        self.create_retenues()

        print("Création des alertes...")
        self.create_alerts()

        print("Toutes les fixtures ont été créées avec succès!")

        return {
            'users': self.users,
            'services': self.services,
            'postes': self.postes,
            'employes': self.employes,
            'contrats': self.contrats,
            'periodes': self.periodes,
            'retenues': self.retenues,
            'alerts': self.alerts
        }
