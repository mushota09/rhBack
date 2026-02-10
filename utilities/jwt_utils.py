"""
Utilitaires JWT pour l'authentification.
"""
from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings


def create_access_token(user_id):
    """Crée un token d'accès JWT"""
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=120),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def create_refresh_token(user_id):
    """Crée un token de rafraîchissement JWT"""
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def verify_token(token, token_type='access'):
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != token_type:
            raise ValueError('Type de token incorrect')
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise ValueError('Token expiré') from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError('Token invalide') from exc


def generate_token(user, token_type='access'):
    """
    Fonction helper pour générer un token à partir d'un objet User.
    Utilisée principalement pour les tests.
    """
    if token_type == 'access':
        return create_access_token(user.id)
    elif token_type == 'refresh':
        return create_refresh_token(user.id)
    else:
        raise ValueError(f'Type de token inconnu: {token_type}')
