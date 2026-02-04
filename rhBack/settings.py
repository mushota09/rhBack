from dotenv import load_dotenv as _env
from datetime import timedelta
from pathlib import Path
import sys
import os

_env()
sys.dont_write_bytecode = True
BASE_DIR = Path(__file__).resolve().parent.parent
CORS_ORIGIN_ALLOW_ALL = True

# Redis configuration for Celery
#REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_URL = os.getenv("REDIS_URL", "redis://:Rapha@1996...@31.97.217.126:6379/0")



# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://mon-frontend.com",
# ]

DEBUG = True
ALLOWED_HOSTS = ["rapha.pythonanywhere.com","127.0.0.1"]

# ************************* SECRET KEY *********************************
SECRET_KEY = os.getenv("SECRET_KEY")
DB_NAME = os.getenv("DB_NAME", "biashara")
DB_USER = os.getenv("DB_USER", "neondb_owner")
DB_PASSWORD = os.getenv("DB_PASSWORD", "npg_gZ4eYlSdwr3o")
DB_HOST = os.getenv("DB_HOST", "ep-tiny-sound-agslibpd-pooler.c-2.eu-central-1.aws.neon.tech")
DB_PORT = os.getenv("DB_PORT", "5432")

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_PORT = 587

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "corsheaders",
    "django_filters",
    "adrf",
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',

    'paie_app',
    'user_app',
    'conge_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utilities.middleware.JWTAuthenticationMiddleware',  # JWT auth middleware
    'utilities.middleware.AuditMiddleware',  # Audit logging middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rhBack.urls'
AUTH_USER_MODEL = 'user_app.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rhBack.wsgi.application'

# ****************************************************************
# REST FRAMEWORK CONFIGURATION
# ****************************************************************

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'utilities.pagination.GlobalPagination',
    'PAGE_SIZE': 7,

    'DEFAULT_FILTER_BACKENDS': [
        'adrf_flex_fields.filter_backends.FlexFieldsFilterBackend',
        # 'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'utilities.auth.PayrollJWTAuthentication',  # Enhanced JWT authentication
        'utilities.auth.JWT_AUTH',  # Custom async JWT authentication
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_RENDERER_CLASSES': (
        [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ] if DEBUG else [
            "rest_framework.renderers.JSONRenderer",
        ]
    ),

    'DEFAULT_SCHEMA_CLASS': "drf_spectacular.openapi.AutoSchema",
}


# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
#     "ROTATE_REFRESH_TOKENS": False,
#     "BLACKLIST_AFTER_ROTATION": False,
#     "ALGORITHM": "HS256",
#     "SIGNING_KEY": SECRET_KEY,
#     "VERIFYING_KEY": None,
#     "AUDIENCE": None,
#     "ISSUER": None,
#     "AUTH_HEADER_TYPES": ("Bearer",),
#     "USER_ID_FIELD": "id",
#     "USER_ID_CLAIM": "id",
#     "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
#     "TOKEN_TYPE_CLAIM": "token_type",
#     "JTI_CLAIM": "jti",
# }

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Système de Gestion de Paie - API Documentation",
    "DESCRIPTION": """
    API complète pour le système de gestion de paie permettant:

    ## Fonctionnalités principales
    - **Gestion des périodes de paie**: Création, traitement et approbation des périodes mensuelles
    - **Calculs salariaux automatisés**: Calcul automatique des salaires, cotisations et retenues
    - **Génération de bulletins de paie**: Création de bulletins PDF professionnels
    - **Gestion des retenues**: Administration des retenues salariales et prêts employés
    - **Exports et rapports**: Export Excel et rapports d'audit détaillés

    ## Authentification
    Cette API utilise l'authentification JWT. Incluez le token dans l'en-tête:
    ```
    Authorization: Bearer <votre_token_jwt>
    ```

    ## Permissions
    - **Employés**: Consultation de leurs propres données de paie
    - **RH**: Gestion complète des données de paie
    - **Administrateurs**: Accès complet et approbation des périodes

    ## Formats de données
    - Toutes les dates sont au format ISO 8601 (YYYY-MM-DD)
    - Les montants sont en décimales avec 2 chiffres après la virgule
    - Les réponses sont paginées par défaut (7 éléments par page)
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    "SERVERS": [
        {
            "url": "http://localhost:8000",
            "description": "Serveur de développement"
        }
    ],
    "TAGS": [
        {
            "name": "Périodes de Paie",
            "description": "Gestion des périodes mensuelles de traitement de paie"
        },
        {
            "name": "Entrées de Paie",
            "description": "Consultation et gestion des calculs salariaux individuels"
        },
        {
            "name": "Retenues Employés",
            "description": "Gestion des retenues salariales et prêts employés"
        },
        {
            "name": "Rapports d'Audit",
            "description": "Génération de rapports et statistiques de paie"
        },
        {
            "name": "Authentification",
            "description": "Endpoints d'authentification et gestion des utilisateurs"
        }
    ],
    "EXTERNAL_DOCS": {
        "description": "Documentation utilisateur complète",
        "url": "/docs/"
    }
}


# ***********************************************************************************
# CONFIGURATION DE LA BASE DE DONNEES
# ***********************************************************************************

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

# Use SQLite for tests to avoid PostgreSQL connection issues
# if 'test' in sys.argv:
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:',
#     }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "odeca_conakry",
#         "USER": "root",
#         "PASSWORD": "",
#         "HOST": "localhost",
#         "PORT": 3306,
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': DB_NAME,
#         'USER': DB_USER,
#         'PASSWORD': DB_PASSWORD,
#         'HOST': DB_HOST,
#         'PORT': DB_PORT,
#         'CONN_MAX_AGE': None,
#     }
# }

# ***********************************************************************************
# PARAMETRAGE DES ENVOIS D'EMAIL
# ***********************************************************************************
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = EMAIL_HOST
EMAIL_PORT = EMAIL_PORT
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = True

# ************************************************************************************
# PASSWORD VALIDATION
# *************************************************************************************

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ****************************************************************
# INTERNATIONALIZATION
# ****************************************************************

LANGUAGE_CODE = "fr-FR"
TIME_ZONE = 'Africa/Bujumbura'
USE_I18N = True
USE_TZ = True



STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ****************************************************************
# PAYROLL SYSTEM CONFIGURATION
# ****************************************************************

# File storage for payslips and exports
PAYSLIPS_ROOT = BASE_DIR / 'media' / 'payslips'
EXPORTS_ROOT = BASE_DIR / 'media' / 'exports'

# Ensure directories exist
PAYSLIPS_ROOT.mkdir(parents=True, exist_ok=True)
EXPORTS_ROOT.mkdir(parents=True, exist_ok=True)

# PDF Generation settings
PDF_SETTINGS = {
    'page_size': 'A4',
    'margin_top': '1cm',
    'margin_bottom': '1cm',
    'margin_left': '1cm',
    'margin_right': '1cm',
    'encoding': 'UTF-8',
}

# Payroll calculation constants
PAYROLL_CONSTANTS = {
    'INSS_PENSION_RATE': 0.06,
    'INSS_PENSION_CAP': 27000,
    'INSS_RISK_RATE': 0.06,
    'INSS_RISK_CAP': 2400,
    'INSS_EMPLOYEE_RATE': 0.04,
    'INSS_EMPLOYEE_CAP': 18000,
    'IRE_BRACKETS': [
        {'min': 0, 'max': 150000, 'rate': 0.0},
        {'min': 150000, 'max': 300000, 'rate': 0.2},
        {'min': 300000, 'max': float('inf'), 'rate': 0.3},
    ],
    'FAMILY_ALLOWANCE_SCALE': [
        {'children': 0, 'amount': 0},
        {'children': 1, 'amount': 5000},
        {'children': 2, 'amount': 10000},
        {'children': 3, 'amount': 15000},
        {'children_additional': 3000},  # Per child above 3
    ],
}

# ****************************************************************
# CELERY CONFIGURATION
# ****************************************************************

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery task routes
CELERY_TASK_ROUTES = {
    'paie_app.tasks.process_payroll_period': {'queue': 'payroll'},
    'paie_app.tasks.generate_payslip': {'queue': 'payslips'},
    'paie_app.tasks.generate_batch_payslips': {'queue': 'payslips'},
    'paie_app.tasks.export_payroll_data': {'queue': 'exports'},
}

# ****************************************************************
# CACHING CONFIGURATION
# ****************************************************************

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'rhback',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Cache timeouts for different data types
CACHE_TIMEOUTS = {
    'payroll_constants': 3600,  # 1 hour
    'employee_contracts': 1800,  # 30 minutes
    'period_statistics': 900,   # 15 minutes
}


# ****************************************************************
# LOGGING CONFIGURATION
# ****************************************************************

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'audit': {
            'format': '{asctime} {levelname} {module} {funcName} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'paie.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'audit',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'paie_app': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'paie_app.audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'paie_app.services': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
}

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
