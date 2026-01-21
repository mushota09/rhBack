# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets

class PasswordResetOTP(models.Model):
    id=models.BigAutoField(primary_key=True, db_column="id")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,db_column="user_id")
    email = models.EmailField(db_column="email")
    otp = models.CharField(max_length=6,db_column="otp")
    reset_token = models.CharField(max_length=100, unique=True,db_column="reset_token")
    is_verified = models.BooleanField(default=False,db_column="is_verified")
    is_used = models.BooleanField(default=False,db_column="is_used")
    created_at = models.DateTimeField(auto_now_add=True,db_column="created_at")
    verified_at = models.DateTimeField(null=True, blank=True,db_column="verified_at")
    expires_at = models.DateTimeField(db_column="expires_at")
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'password_reset_otp'
    
    def save(self, *args, **kwargs):
        if not self.reset_token:
            self.reset_token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"