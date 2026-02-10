from user_app.models import User as user
from adrf.viewsets import ModelViewSet
from .serializers import J_userSerializers, I_userSerializers

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from utilities.jwt_utils import create_access_token, create_refresh_token, verify_token
from utilities.auth import *
from utilities.audit_service import AuditService
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)
from drf_spectacular.types import OpenApiTypes


from user_app.models import User as user
from adrf.viewsets import ModelViewSet
from .serializers import J_userSerializers, I_userSerializers

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from utilities.jwt_utils import create_access_token, create_refresh_token, verify_token
from utilities.auth import *
from utilities.audit_service import AuditService
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)
from drf_spectacular.types import OpenApiTypes


class userAPIView(ModelViewSet):
    """
    ViewSet for user management with filtering, expansion capabilities.

    L'audit est AUTOMATIQUE via le middleware - aucune configuration nécessaire !

    Provides CRUD operations for users with:
    - Filtering by employee, position, service
    - Expansion of related objects
    - Ordering by ID (descending)
    - Automatic async audit logging (via middleware)
    """
    queryset = user.objects.all().order_by('-id')
    serializer_class_read = J_userSerializers
    serializer_class_write = I_userSerializers
    filterset_fields = ['employe_id',"employe_id__poste_id","employe_id__poste_id__service_id"]
    search_fields = []
    permit_list_expands = ["employe_id","employe_id.poste_id","employe_id.poste_id.service_id"]


User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Connexion utilisateur",
        description="""
        Authentifie un utilisateur avec email et mot de passe.
        Retourne les tokens JWT d'accès et de rafraîchissement.

        **Validations:**
        - Email et mot de passe requis
        - Utilisateur doit exister et être actif
        - Mot de passe doit être correct
        """,
        tags=["Authentification"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Adresse email de l\'utilisateur'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Mot de passe de l\'utilisateur'
                    }
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Connexion réussie",
                examples=[
                    OpenApiExample(
                        "Tokens JWT",
                        value={
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "username": "user"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données manquantes",
                examples=[
                    OpenApiExample(
                        "Email/mot de passe manquant",
                        value={"error": "Veuillez fournir un email et un mot de passe"}
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Erreur d'authentification",
                examples=[
                    OpenApiExample(
                        "Utilisateur inexistant",
                        value={"error": "Aucun utilisateur correspondant à cette adresse email"}
                    ),
                    OpenApiExample(
                        "Mot de passe incorrect",
                        value={"error": "Mot de passe incorrect"}
                    ),
                    OpenApiExample(
                        "Compte désactivé",
                        value={"error": "Ce compte est désactivé. Veuillez contacter un administrateur pour procéder à l'activation"}
                    )
                ]
            )
        }
    )
    async def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            # Log failed login attempt
            AuditService.log_login(None, request, success=False)
            return Response({'error': 'Veuillez fournir un email et un mot de passe'},status=status.HTTP_400_BAD_REQUEST)

        try:
            user = await User.objects.aget(email=email)
        except User.DoesNotExist:
            # Log failed login attempt
            AuditService.log_login(None, request, success=False)
            return Response({'error': 'Aucun utilisateur correspondant à cette adresse email'},status=status.HTTP_401_UNAUTHORIZED)

        check_password = sync_to_async(user.check_password)
        if not await check_password(password):
            # Log failed login attempt
            AuditService.log_login(user, request, success=False)
            return Response({'error': 'Mot de passe incorrect'},status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            # Log failed login attempt
            AuditService.log_login(user, request, success=False)
            return Response({'error': 'Ce compte est désactivé. Veuillez contacter un administrateur pour procéder à l\'activation'},status=status.HTTP_401_UNAUTHORIZED)

        # Log successful login
        AuditService.log_login(user, request, success=True)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.nom,
                'prenom': user.prenom,
            }
        })

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Rafraîchir le token d'accès",
        description="""
        Génère un nouveau token d'accès à partir d'un token de rafraîchissement valide.
        Utilisé pour maintenir la session utilisateur sans redemander les identifiants.
        """,
        tags=["Authentification"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh_token': {
                        'type': 'string',
                        'description': 'Token de rafraîchissement JWT'
                    }
                },
                'required': ['refresh_token']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Token rafraîchi avec succès",
                examples=[
                    OpenApiExample(
                        "Nouveau token d'accès",
                        value={"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Token de rafraîchissement manquant",
                examples=[
                    OpenApiExample(
                        "Token manquant",
                        value={"error": "Refresh token requis"}
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Token invalide ou expiré",
                examples=[
                    OpenApiExample(
                        "Token invalide",
                        value={"error": "Token invalide ou expiré"}
                    )
                ]
            )
        }
    )
    async def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token requis'},status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = verify_token(refresh_token, 'refresh')
            new_access_token = create_access_token(payload['user_id'])
            return Response({'access_token': new_access_token})
        except ValueError as e:
            return Response({'error': str(e)},status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    authentication_classes = [JWT_AUTH]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Déconnexion utilisateur",
        description="""
        Déconnecte l'utilisateur authentifié.
        Note: Les tokens JWT sont stateless, donc la déconnexion effective
        doit être gérée côté client en supprimant les tokens.
        """,
        tags=["Authentification"],
        responses={
            200: OpenApiResponse(
                description="Déconnexion réussie",
                examples=[
                    OpenApiExample(
                        "Message de déconnexion",
                        value={"message": "Déconnecté avec succès. Supprimez les tokens côté client."}
                    )
                ]
            ),
            401: OpenApiResponse(description="Non authentifié")
        }
    )
    async def post(self, request):
        # Log logout action
        if hasattr(request, 'user') and request.user.is_authenticated:
            AuditService.log_logout(request.user, request)

        return Response({'message': 'Déconnecté avec succès. Supprimez les tokens côté client.'})

class ProtectedView(APIView):
    authentication_classes = [JWT_AUTH]
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Endpoint protégé de test",
        description="""
        Endpoint de test pour vérifier l'authentification JWT.
        Retourne les informations de l'utilisateur authentifié.
        """,
        tags=["Authentification"],
        responses={
            200: OpenApiResponse(
                description="Accès autorisé",
                examples=[
                    OpenApiExample(
                        "Informations utilisateur",
                        value={
                            "message": "Bonjour user",
                            "user_id": 1
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description="Non authentifié")
        }
    )
    async def get(self, request):
        return Response({'message': f'Bonjour {request.user.username}','user_id': request.user.id})

