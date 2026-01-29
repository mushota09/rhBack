import jwt
from datetime import datetime, timedelta
from django.conf import settings

def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token, token_type='access'):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != token_type:
            raise ValueError('Type de token incorrect')
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expiré')
    except jwt.InvalidTokenError:
        raise ValueError('Token invalide')