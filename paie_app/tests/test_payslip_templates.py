"""
Tests unitaires pour les templates de bulletins de paie.
"""
from decimal import Decimal
from datetime import date, datetime
from django.test import TestCase
from django.template.loader import render_to_string


class PayslipTemplateTests(TestCase):
    """Tests unitaires pour les templates de bulletins de paie"""

    def setUp(self):
        """Configuration des tests"""
        # Données de test complètes
        self.complete_data = {
            'company': {
                'nom': 'Test Company SARL',
                'adresse': '123 Avenue Test, Kinshasa',
                'telephone': '+243 123 456 789',
                'email': 'contact@testcompany.cd'
            },
            'employee': {
                'nom_complet': 'Employe Test',
                'email': 'employe@example.com',
                'numero_inss': '123456789',
                'date_embauche': date(2020, 1, 1),
                'banque': 'Test Bank',
                'numero_compte': '123456789',
                'nombre_enfants': 2
            },
            'period': {
                'annee': 2024,
                'mois': 1,
                'date_debut': date(2024, 1, 1),
                'date_fin': date(2024, 1, 31)
            },
            'salary_components': {
                'salaire_base': Decimal('500000'),
                'indemnite_logement': Decimal('50000'),
                'allocation_familiale': Decimal('10000'),
                'salaire_brut': Decimal('560000')
            },
            'contributions': {
                'cotisations_patronales': {'inss_pension': '27000'},
                'cotisations_salariales': {'inss': '18000'},
                'retenues_diverses': {'avance_salaire': '50000'}
            },
            'totals': {
                'total_charge_salariale': Decimal('68000'),
                'salaire_net': Decimal('492000')
            },
            'generated_at': datetime.now(),
            'entree_id': 1
        }

    def test_default_template_renders(self):
        """Test que le template par défaut se rend correctement"""
        html_content = render_to_string('payslips/default.html', self.complete_data)

        # Vérifier la présence des éléments essentiels
        self.assertIn('Test Company SARL', html_content)
        self.assertIn('BULLETIN DE PAIE', html_content)
        self.assertIn('Employe Test', html_content)
        self.assertIn('01/2024', html_content)
        self.assertIn('500000', html_content)  # Salaire de base
        self.assertIn('492000', html_content)  # Salaire net

    def test_simple_template_renders(self):
        """Test que le template simple se rend correctement"""
        html_content = render_to_string('payslips/simple.html', self.complete_data)

        self.assertIn('Test Company SARL', html_content)
        self.assertIn('BULLETIN DE PAIE', html_content)
        self.assertIn('Employe Test', html_content)
        self.assertIn('492000', html_content)

    def test_premium_template_renders(self):
        """Test que le template premium se rend correctement"""
        html_content = render_to_string('payslips/premium.html', self.complete_data)

        self.assertIn('Test Company SARL', html_content)
        self.assertIn('BULLETIN DE PAIE', html_content)
        self.assertIn('Employe Test', html_content)

    def test_template_with_minimal_data(self):
        """Test du template avec données minimales"""
        minimal_data = {
            'company': {'nom': 'Test Company'},
            'employee': {'nom_complet': 'Employe Test'},
            'period': {'annee': 2024, 'mois': 1},
            'salary_components': {'salaire_base': Decimal('500000'), 'salaire_brut': Decimal('500000')},
            'contributions': {'cotisations_patronales': {}, 'cotisations_salariales': {}, 'retenues_diverses': {}},
            'totals': {'salaire_net': Decimal('500000')},
            'generated_at': datetime.now()
        }

        html_content = render_to_string('payslips/default.html', minimal_data)
        self.assertIn('Test Company', html_content)
        self.assertIn('BULLETIN DE PAIE', html_content)

    def test_html_structure(self):
        """Test de la structure HTML"""
        html_content = render_to_string('payslips/default.html', self.complete_data)

        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('<html', html_content)
        self.assertIn('<head>', html_content)
        self.assertIn('<body>', html_content)
        self.assertIn('<style>', html_content)
        self.assertIn('</html>', html_content)
