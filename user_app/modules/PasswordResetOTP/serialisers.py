# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re

class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Adresse email invalide")

        if not User.objects.filter(log_in=value).exists():
            raise serializers.ValidationError("Aucun compte associé à cette adresse email")
        
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("Le code OTP doit contenir exactement 6 chiffres")
        return value


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(log_in=value).exists():
            raise serializers.ValidationError("Aucun compte associé à cette adresse email")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    reset_token = serializers.CharField(max_length=100)
    password = serializers.CharField(min_length=8)
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères")
        
        # Additional password strength validation can be added here
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre")
        
        return value