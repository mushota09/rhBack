import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp, user_name=None):
    """Send OTP via email"""
    try:
        subject = 'Code de vérification - Réinitialisation mot de passe'
        
        # HTML email template
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #3f3128; margin-bottom: 10px;">Réinitialisation de mot de passe</h1>
                    <p style="color: #666; font-size: 16px;">ODECA - Système de traçabilité du café</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #3f3128; text-align: center; margin-bottom: 15px;">Votre code de vérification</h2>
                    <div style="text-align: center; font-size: 32px; font-weight: bold; color: #3f3128; letter-spacing: 8px; background-color: white; padding: 15px; border-radius: 5px; border: 2px solid #3f3128;">
                        {otp}
                    </div>
                </div>
                
                <div style="margin: 25px 0;">
                    <p style="color: #333; font-size: 16px; line-height: 1.5;">
                        {"Bonjour " + user_name + "," if user_name else "Bonjour,"}
                    </p>
                    <p style="color: #333; font-size: 16px; line-height: 1.5;">
                        Vous avez demandé la réinitialisation de votre mot de passe. 
                        Veuillez utiliser le code de vérification ci-dessus pour continuer.
                    </p>
                    <p style="color: #333; font-size: 16px; line-height: 1.5;">
                        <strong>Ce code expire dans 15 minutes.</strong>
                    </p>
                </div>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="color: #856404; font-size: 14px; margin: 0;">
                        <strong>Attention:</strong> Si vous n'avez pas demandé cette réinitialisation, 
                        veuillez ignorer cet email et votre mot de passe restera inchangé.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px;">
                        Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Réinitialisation de mot de passe - ODECA
        
        {"Bonjour " + user_name + "," if user_name else "Bonjour,"}
        
        Vous avez demandé la réinitialisation de votre mot de passe.
        Voici votre code de vérification:
        
        {otp}
        
        Ce code expire dans 15 minutes.
        
        Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.
        
        Cordialement,
        L'équipe ODECA
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        return False