import json
import tempfile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from user_app.models import employe, contrat, document, service, poste

User = get_user_model()


class CompleteEmployeeCreationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a test user for authentication
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.admin_user)
        
        # Create test service and poste
        self.service = service.objects.create(
            titre='IT Department',
            code='IT',
            description='Information Technology Department'
        )
        
        self.poste = poste.objects.create(
            titre='Software Developer',
            code='DEV',
            description='Software Development Position',
            service_id=self.service
        )

    def test_create_complete_employee_success(self):
        """Test successful creation of complete employee with contract and documents"""
        
        # Prepare employee data
        employee_data = {
            'prenom': 'John',
            'nom': 'Doe',
            'postnom': 'Smith',
            'date_naissance': '1990-01-15',
            'sexe': 'M',
            'statut_matrimonial': 'S',
            'nationalite': 'American',
            'banque': 'Test Bank',
            'numero_compte': '123456789',
            'niveau_etude': 'Bachelor',
            'numero_inss': 'INSS123456',
            'email_personnel': 'john.doe@personal.com',
            'email_professionnel': 'john.doe@company.com',
            'telephone_personnel': '+1234567890',
            'telephone_professionnel': '+1234567891',
            'adresse_ligne1': '123 Main St',
            'adresse_ligne2': 'Apt 4B',
            'ville': 'New York',
            'province': 'NY',
            'code_postal': '10001',
            'pays': 'USA',
            'poste_id': self.poste.id,
            'date_embauche': '2024-01-01',
            'statut_emploi': 'ACTIVE',
            'nombre_enfants': 2,
            'nom_conjoint': 'Jane Doe',
            'biographie': 'Experienced software developer',
            'nom_contact_urgence': 'Emergency Contact',
            'lien_contact_urgence': 'Brother',
            'telephone_contact_urgence': '+1234567892'
        }
        
        # Prepare contract data
        contract_data = {
            'type_contrat': 'PERMANENT',
            'date_debut': '2024-01-01',
            'type_salaire': 'M',
            'salaire_base': 5000.00,
            'devise': 'USD',
            'indemnite_logement': 10.0,
            'indemnite_deplacement': 5.0,
            'prime_fonction': 15.0,
            'autre_avantage': 500.00,
            'assurance_patronale': 2.0,
            'assurance_salariale': 1.0,
            'fpc_patronale': 1.5,
            'fpc_salariale': 0.5,
            'commentaire': 'Initial contract'
        }
        
        # Prepare document data
        document_metadata_1 = {
            'document_type': 'CONTRACT',
            'titre': 'Employment Contract',
            'description': 'Initial employment contract',
            'expiry_date': '2025-01-01'
        }
        
        document_metadata_2 = {
            'document_type': 'ID',
            'titre': 'Identity Document',
            'description': 'Copy of ID card'
        }
        
        # Create test files
        test_file_1 = SimpleUploadedFile(
            "contract.pdf",
            b"fake contract content",
            content_type="application/pdf"
        )
        
        test_file_2 = SimpleUploadedFile(
            "id_card.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        # Prepare the payload
        payload = {
            'employee': json.dumps(employee_data),
            'contract': json.dumps(contract_data),
            'documents[0].file': test_file_1,
            'documents[0].metadata': json.dumps(document_metadata_1),
            'documents[1].file': test_file_2,
            'documents[1].metadata': json.dumps(document_metadata_2),
        }
        
        # Make the request
        url = reverse('employeAPIView-create-complete')
        response = self.client.post(url, payload, format='multipart')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('Employee created successfully', response.data['message'])
        
        # Verify employee was created
        self.assertTrue(employe.objects.filter(email_personnel='john.doe@personal.com').exists())
        created_employee = employe.objects.get(email_personnel='john.doe@personal.com')
        
        # Verify contract was created
        self.assertTrue(contrat.objects.filter(employe_id=created_employee).exists())
        created_contract = contrat.objects.get(employe_id=created_employee)
        self.assertEqual(created_contract.type_contrat, 'PERMANENT')
        self.assertEqual(float(created_contract.salaire_base), 5000.00)
        
        # Verify documents were created
        self.assertEqual(document.objects.filter(employe_id=created_employee).count(), 2)
        
        # Verify user account was created
        self.assertTrue(User.objects.filter(email='john.doe@company.com').exists())
        created_user = User.objects.get(email='john.doe@company.com')
        self.assertEqual(created_user.employe_id, created_employee)
        
        # Verify response data structure
        response_data = response.data['data']
        self.assertIn('employee', response_data)
        self.assertIn('contract', response_data)
        self.assertIn('documents', response_data)
        self.assertIn('user', response_data)
        
        self.assertEqual(response_data['employee']['nom'], 'Doe')
        self.assertEqual(response_data['employee']['prenom'], 'John')
        self.assertEqual(len(response_data['documents']), 2)

    def test_create_complete_employee_missing_employee_data(self):
        """Test error when employee data is missing"""
        payload = {
            'contract': json.dumps({'type_contrat': 'PERMANENT'}),
        }
        
        url = reverse('employeAPIView-create-complete')
        response = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Employee data is required', response.data['error'])

    def test_create_complete_employee_invalid_employee_data(self):
        """Test error when employee data is invalid JSON"""
        payload = {
            'employee': 'invalid json',
            'contract': json.dumps({'type_contrat': 'PERMANENT'}),
        }
        
        url = reverse('employeAPIView-create-complete')
        response = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid employee data format', response.data['error'])

    def test_create_complete_employee_missing_contract_data(self):
        """Test error when contract data is missing"""
        employee_data = {
            'prenom': 'John',
            'nom': 'Doe',
            'date_naissance': '1990-01-15',
            'sexe': 'M',
            'statut_matrimonial': 'S',
            'nationalite': 'American',
            'banque': 'Test Bank',
            'numero_compte': '123456789',
            'niveau_etude': 'Bachelor',
            'numero_inss': 'INSS123456',
            'email_personnel': 'john.doe@personal.com',
            'telephone_personnel': '+1234567890',
            'adresse_ligne1': '123 Main St',
            'date_embauche': '2024-01-01',
            'statut_emploi': 'ACTIVE',
            'nombre_enfants': 0,
            'nom_contact_urgence': 'Emergency Contact',
            'lien_contact_urgence': 'Brother',
            'telephone_contact_urgence': '+1234567892'
        }
        
        payload = {
            'employee': json.dumps(employee_data),
        }
        
        url = reverse('employeAPIView-create-complete')
        response = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Contract data is required', response.data['error'])

    def test_create_complete_employee_validation_error(self):
        """Test validation error handling"""
        # Employee data with missing required fields
        employee_data = {
            'prenom': 'John',
            # Missing required 'nom' field
            'date_naissance': '1990-01-15',
            'sexe': 'M',
            'statut_matrimonial': 'S',
            'nationalite': 'American',
            'email_personnel': 'john.doe@personal.com',
            'telephone_personnel': '+1234567890',
            'adresse_ligne1': '123 Main St',
            'date_embauche': '2024-01-01',
            'statut_emploi': 'ACTIVE',
            'nombre_enfants': 0,
            'nom_contact_urgence': 'Emergency Contact',
            'lien_contact_urgence': 'Brother',
            'telephone_contact_urgence': '+1234567892'
        }
        
        contract_data = {
            'type_contrat': 'PERMANENT',
            'date_debut': '2024-01-01',
            'type_salaire': 'M',
            'salaire_base': 5000.00,
            'devise': 'USD',
            'indemnite_logement': 10.0,
            'indemnite_deplacement': 5.0,
            'prime_fonction': 15.0,
            'autre_avantage': 500.00,
            'assurance_patronale': 2.0,
            'assurance_salariale': 1.0,
            'fpc_patronale': 1.5,
            'fpc_salariale': 0.5,
        }
        
        payload = {
            'employee': json.dumps(employee_data),
            'contract': json.dumps(contract_data),
        }
        
        url = reverse('employeAPIView-create-complete')
        response = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Employee validation error', response.data['error'])