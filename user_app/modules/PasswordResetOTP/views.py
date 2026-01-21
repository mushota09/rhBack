# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from gestionUtilisateur.models import admin_user as User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db import transaction
from .models import PasswordResetOTP
from .serialisers import (
    ForgotPasswordRequestSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    ResetPasswordSerializer
)
from .utils import generate_otp, send_otp_email

@api_view(['POST'])
# @permission_classes([AllowAny])
def forgot_password_request(request):
    """
    Step 1: Request password reset - Send OTP to email
    """
    serializer = ForgotPasswordRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(log_in=email)
            
            # Invalidate any existing OTPs for this user
            PasswordResetOTP.objects.filter(
                user_id=user, 
                is_used=False
            ).update(is_used=True)
            
            # Generate new OTP
            otp = generate_otp()
            
            # Create new OTP record
            otp_record = PasswordResetOTP.objects.create(
                user_id=user,
                email=email,
                otp=otp
            )
            
            # Send OTP email
            user_name = f"{user.nom} {user.prenom}".strip()
            email_sent = send_otp_email(email, otp, user_name)
            
            if email_sent:
                return Response({
                    'message': 'Code OTP envoyé avec succès',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                otp_record.delete()
                return Response({
                    'detail': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({
                'detail': 'Aucun compte associé à cette adresse email'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Une erreur est survenue. Veuillez réessayer.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([AllowAny])
def verify_otp(request):
    """
    Step 2: Verify OTP code
    """
    serializer = VerifyOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(log_in=email)

            otp_record = PasswordResetOTP.objects.filter(
                user_id=user,
                email=email,
                otp=otp,
                is_used=False,
                is_verified=False
            ).first()
            
            if not otp_record:
                return Response({
                    'detail': 'Code OTP invalide ou expiré'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_record.is_expired():
                return Response({
                    'detail': 'Code OTP expiré. Veuillez demander un nouveau code.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            otp_record.is_verified = True
            otp_record.verified_at = timezone.now()
            otp_record.save()
            return Response({
                'message': 'Code OTP vérifié avec succès',
                'reset_token': otp_record.reset_token
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'detail': 'Aucun compte associé à cette adresse email'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Une erreur est survenue. Veuillez réessayer.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP code
    """
    serializer = ResendOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(log_in=email)

            recent_otp = PasswordResetOTP.objects.filter(
                user_id=user,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).exists()
            
            if recent_otp:
                return Response({
                    'detail': 'Veuillez attendre 1 minute avant de demander un nouveau code'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Invalidate existing OTPs
            PasswordResetOTP.objects.filter(
                user_id=user,
                is_used=False
            ).update(is_used=True)
            
            # Generate new OTP
            otp = generate_otp()
            
            # Create new OTP record
            otp_record = PasswordResetOTP.objects.create(
                user_id=user,
                email=email,
                otp=otp
            )
            
            # Send OTP email
            user_name = f"{user.nom} {user.prenom}".strip()
            email_sent = send_otp_email(email, otp, user_name)
            
            if email_sent:

                return Response({
                    'message': 'Nouveau code OTP envoyé avec succès'
                }, status=status.HTTP_200_OK)
            else:
                otp_record.delete()
                return Response({
                    'detail': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({
                'detail': 'Aucun compte associé à cette adresse email'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Une erreur est survenue. Veuillez réessayer.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([AllowAny])
def reset_password(request):
    """
    Step 3: Reset password with verified OTP
    """
    serializer = ResetPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(log_in=email)
            
            otp_record = PasswordResetOTP.objects.filter(
                user_id=user,
                email=email,
                otp=otp,
                reset_token=reset_token,
                is_verified=True,
                is_used=False
            ).first()
            
            if not otp_record:
                return Response({
                    'detail': 'Token de réinitialisation invalide ou expiré'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_record.is_expired():
                return Response({
                    'detail': 'Session expirée. Veuillez recommencer le processus.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Reset password with transaction for safety
            with transaction.atomic():
                # Update user password
                user.password = make_password(new_password)
                user.save()
                
                # Mark OTP as used
                otp_record.is_used = True
                otp_record.save()
                
                # Invalidate all other OTPs for this user
                PasswordResetOTP.objects.filter(
                    user_id=user,
                    is_used=False
                ).exclude(id=otp_record.id).update(is_used=True)
            
            return Response({
                'message': 'Mot de passe réinitialisé avec succès'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'detail': 'Aucun compte associé à cette adresse email'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'detail': 'Une erreur est survenue. Veuillez réessayer.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)