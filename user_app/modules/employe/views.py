from user_app.models import employe, contrat, document
from asgiref.sync import sync_to_async
from adrf.viewsets import ModelViewSet
from .serializers import J_employeSerializers, I_employeSerializers
from user_app.modules.contrat.serializers import I_contratSerializers
from user_app.modules.document.serializers import I_documentSerializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import transaction
import json
import logging

logger = logging.getLogger(__name__)
UserModel = get_user_model()

class employeAPIView(ModelViewSet):
    queryset = employe.objects.all().order_by('-id')
    serializer_class_read = J_employeSerializers
    serializer_class_write = I_employeSerializers
    filterset_fields = ['poste_id','poste_id__service_id']
    search_fields = [
        'prenom', 'nom', 'postnom', 'sexe', 'statut_matrimonial', 'nationalite',
        'banque', 'numero_compte', 'niveau_etude', 'numero_inss',
        'email_personnel', 'email_professionnel',
        'telephone_personnel', 'telephone_professionnel',
        'adresse_ligne1', 'adresse_ligne2', 'ville', 'province', 'code_postal',
        'pays', 'matricule'
    ]
    permit_list_expands = ['poste_id','poste_id.service_id']

    async def acreate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        @sync_to_async
        @transaction.atomic
        def save_all():
            instance = serializer.save()
            employe_id = instance.id

            password = request.data.get('password', "12345")
            if password:
                nom = request.data.get('nom', f'utilisateur{employe_id}')
                prenom = request.data.get('prenom', f'utilisateur{employe_id}')
                user_instance = UserModel(
                    nom=nom,
                    prenom=prenom,
                    employe_id=instance,
                    photo=request.FILES.get('photo', None),
                    email=request.data.get('email_professionnel', request.data.get("email_personnel"),request.data.get('email', '')),
                    password=make_password(password),
                    is_active=True
                )
                user_instance.save()

            return serializer.data

        data = await save_all()
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'], url_path='create-complete')
    async def create_complete(self, request, *args, **kwargs):
        """
        Create a complete employee with contract, documents, and user account in a single atomic transaction.
        
        Expected payload:
        - employee: JSON string with employee data
        - contract: JSON string with contract data
        - documents[0].file: File upload
        - documents[0].metadata: JSON string with document metadata
        - documents[1].file: File upload (if multiple documents)
        - documents[1].metadata: JSON string with document metadata
        """
        try:
            # Parse employee data
            employee_data_str = request.data.get('employee')
            if not employee_data_str:
                return Response(
                    {'error': 'Employee data is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                employee_data = json.loads(employee_data_str)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid employee data format'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parse contract data
            contract_data_str = request.data.get('contract')
            if not contract_data_str:
                return Response(
                    {'error': 'Contract data is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                contract_data = json.loads(contract_data_str)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid contract data format'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parse documents data
            documents_data = []
            document_files = []
            
            # Extract document files and metadata
            for key, value in request.data.items():
                if key.startswith('documents[') and key.endswith('].file'):
                    # Extract index from key like 'documents[0].file'
                    index = key.split('[')[1].split(']')[0]
                    metadata_key = f'documents[{index}].metadata'
                    
                    if metadata_key in request.data:
                        try:
                            metadata = json.loads(request.data[metadata_key])
                            documents_data.append(metadata)
                            document_files.append(value)
                        except json.JSONDecodeError:
                            return Response(
                                {'error': f'Invalid document metadata format for document {index}'}, 
                                status=status.HTTP_400_BAD_REQUEST
                            )

            @sync_to_async
            @transaction.atomic
            def create_complete_employee():
                # 1. Create employee
                employee_serializer = I_employeSerializers(data=employee_data)
                if not employee_serializer.is_valid():
                    raise ValueError(f"Employee validation error: {employee_serializer.errors}")
                
                employee_instance = employee_serializer.save()
                
                # 2. Create contract
                contract_data['employe_id'] = employee_instance.id
                contract_serializer = I_contratSerializers(data=contract_data)
                if not contract_serializer.is_valid():
                    raise ValueError(f"Contract validation error: {contract_serializer.errors}")
                
                contract_instance = contract_serializer.save()
                
                # 3. Create documents
                created_documents = []
                for i, (doc_metadata, doc_file) in enumerate(zip(documents_data, document_files)):
                    doc_data = {
                        'employe_id': employee_instance.id,
                        'document_type': doc_metadata.get('document_type'),
                        'titre': doc_metadata.get('titre'),
                        'description': doc_metadata.get('description', ''),
                        'expiry_date': doc_metadata.get('expiry_date'),
                        'uploaded_by': request.user.email if request.user.is_authenticated else 'System',
                        'file': doc_file
                    }
                    
                    document_serializer = I_documentSerializers(data=doc_data)
                    if not document_serializer.is_valid():
                        raise ValueError(f"Document {i} validation error: {document_serializer.errors}")
                    
                    document_instance = document_serializer.save()
                    created_documents.append(document_instance)
                
                # 4. Create user account
                password = "12345"  # Default password, should be changed on first login
                user_email = employee_data.get('email_professionnel') or employee_data.get('email_personnel')
                
                if user_email:
                    user_instance = UserModel(
                        nom=employee_data.get('nom', ''),
                        prenom=employee_data.get('prenom', ''),
                        employe_id=employee_instance,
                        email=user_email,
                        password=make_password(password),
                        is_active=True
                    )
                    user_instance.save()
                else:
                    user_instance = None
                
                return {
                    'employee': employee_instance,
                    'contract': contract_instance,
                    'documents': created_documents,
                    'user': user_instance
                }

            # Execute the transaction
            result = await create_complete_employee()
            
            # Prepare response data
            response_data = {
                'success': True,
                'message': 'Employee created successfully with contract, documents, and user account',
                'data': {
                    'employee': {
                        'id': result['employee'].id,
                        'nom': result['employee'].nom,
                        'prenom': result['employee'].prenom,
                        'email_professionnel': result['employee'].email_professionnel,
                        'matricule': result['employee'].matricule,
                        'statut_emploi': result['employee'].statut_emploi,
                    },
                    'contract': {
                        'id': result['contract'].id,
                        'type_contrat': result['contract'].type_contrat,
                        'salaire_base': float(result['contract'].salaire_base),
                        'devise': result['contract'].devise,
                        'date_debut': result['contract'].date_debut.isoformat(),
                        'date_fin': result['contract'].date_fin.isoformat() if result['contract'].date_fin else None,
                    },
                    'documents': [
                        {
                            'id': doc.id,
                            'titre': doc.titre,
                            'document_type': doc.document_type,
                            'file': doc.file.url if doc.file else None,
                        }
                        for doc in result['documents']
                    ],
                    'user': {
                        'id': result['user'].id,
                        'email': result['user'].email,
                        'is_active': result['user'].is_active,
                    } if result['user'] else None,
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.error(f"Validation error in create_complete: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_complete: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred during employee creation'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
