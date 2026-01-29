from user_app.models import User as user
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_userSerializers, I_userSerializers

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from utilities.jwt_utils import create_access_token, create_refresh_token, verify_token
from utilities.auth import *


class userAPIView(FlexFieldsModelViewSet):
    queryset = user.objects.all().order_by('-id')
    serializer_class_read = J_userSerializers
    serializer_class_write = I_userSerializers 
    filterset_fields = ['employe_id',"employe_id__poste_id","employe_id__poste_id__service_id"]
    search_fields = []
    permit_list_expands = ["employe_id","employe_id.poste_id","employe_id.poste_id.service_id"]


User = get_user_model()

class LoginView(APIView):

    async def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Veuillez fournir un email et un mot de passe'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = await User.objects.aget(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Aucun utilisateur correspondant à cette adresse email'},status=status.HTTP_401_UNAUTHORIZED)

        check_password = sync_to_async(user.check_password)
        if not await check_password(password):
            return Response({'error': 'Mot de passe incorrect'},status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Ce compte est désactivé. Veuillez contacter un administrateur pour procéder à l\'activation'},status=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            }
        })

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

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

    async def post(self, request):
        return Response({'message': 'Déconnecté avec succès. Supprimez les tokens côté client.'})

class ProtectedView(APIView):
    authentication_classes = [JWT_AUTH]
    # permission_classes = [IsAuthenticated]

    async def get(self, request):
        return Response({'message': f'Bonjour {request.user.username}','user_id': request.user.id})

  