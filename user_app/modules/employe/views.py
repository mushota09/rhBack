from user_app.models import employe
from asgiref.sync import sync_to_async
from adrf.viewsets import ModelViewSet
from .serializers import J_employeSerializers, I_employeSerializers
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import transaction

UserModel=get_user_model()

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
