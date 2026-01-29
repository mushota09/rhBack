"""
Tests basiques pour PayslipGeneratorService.
Feature: paie-system
"""
from django.test import TestCase
from paie_app.services import PayslipGeneratorService


class PayslipGeneratorBasicTests(TestCase):
    """Tests basiques pour PayslipGeneratorService"""

    def test_service_initialization(self):
        """Test d'initialisation du service"""
        service = PayslipGeneratorService()
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.styles)

    def test_service_methods_exist(self):
        """Test que les méthodes du service existent"""
        service = PayslipGeneratorService()

        # Vérifier que les méthodes principales existent
        self.assertTrue(hasattr(service, 'generate_payslip'))
        self.assertTrue(hasattr(service, 'render_payslip_pdf'))
        self.assertTrue(hasattr(service, 'save_payslip_file'))

        # Vérifier que les méthodes privées existent
        self.assertTrue(hasattr(service, '_prepare_payslip_data'))
        self.assertTrue(hasattr(service, '_render_html_template'))
        self.assertTrue(hasattr(service, '_generate_pdf_from_html'))
