# Configuration Système

Ce guide détaille la configuration initiale et la maintenance du système de paie, incluant les paramètres de base, la configuration de la base de données et les réglages de performance.

## Installation et Démarrage

### Prérequis Système

**Environnement de développement :**
- Python 3.11+
- PostgreSQL 14+
- Redis 6+ (pour le cache et les tâches asynchrones)
- Node.js 18+ (pour les outils de build frontend)

**Environnement de production :**
- Serveur Linux (Ubuntu 22.04 LTS recommandé)
- 4 CPU cores minimum
- 8 GB RAM minimum
- 100 GB stockage SSD
- Connexion internet stabl
 Démarrage du serveur
uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000
```

## Configuration de Base

### Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/paie_db
DATABASE_NAME=paie_db
DATABASE_USER=paie_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Sécurité
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (Cache et Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Stockage des fichiers
MEDIA_ROOT=/var/www/paie/media
STATIC_ROOT=/var/www/paie/static
FILE_UPLOAD_MAX_MEMORY_SIZE=10485760  # 10MB

# Email (pour les notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@company.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/paie/paie.log

# Performance
ASYNC_BATCH_SIZE=50
MAX_CONCURRENT_CALCULATIONS=10
CACHE_TIMEOUT=3600  # 1 heure
```

### Configuration Django (settings.py)

```python
# rhBack/settings.py

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'adrf',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'user_app',
    'paie_app',
    'conge_app',
    'utilities',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utilities.middleware.JWTAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utilities.middleware.AuditMiddleware',
]

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}

# Cache Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': config('CACHE_TIMEOUT', default=3600, cast=int),
    }
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Configuration des fichiers
MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')
STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

# Configuration spécifique à la paie
PAIE_CONFIG = {
    'ASYNC_BATCH_SIZE': config('ASYNC_BATCH_SIZE', default=50, cast=int),
    'MAX_CONCURRENT_CALCULATIONS': config('MAX_CONCURRENT_CALCULATIONS', default=10, cast=int),
    'PAYSLIP_TEMPLATE_DIR': BASE_DIR / 'templates' / 'payslips',
    'EXPORT_DIR': MEDIA_ROOT / 'exports',
    'BACKUP_DIR': MEDIA_ROOT / 'backups',
}
```

## Configuration de la Base de Données

### Optimisation PostgreSQL

```sql
-- Configuration recommandée pour PostgreSQL
-- Dans postgresql.conf

# Mémoire
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connexions
max_connections = 100
max_prepared_transactions = 100

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 4
max_parallel_workers_per_gather = 2

# Logging
log_statement = 'mod'
log_duration = on
log_min_duration_statement = 1000

# Checkpoint
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### Index de Performance

```sql
-- Index pour optimiser les requêtes fréquentes
CREATE INDEX CONCURRENTLY idx_entree_paie_periode_employe
ON paie_app_entree_paie(periode_paie_id, employe_id);

CREATE INDEX CONCURRENTLY idx_entree_paie_date_creation
ON paie_app_entree_paie(date_creation);

CREATE INDEX CONCURRENTLY idx_retenue_employe_active
ON paie_app_retenue_employe(employe_id, est_active, date_debut, date_fin);

CREATE INDEX CONCURRENTLY idx_periode_paie_statut_date
ON paie_app_periode_paie(statut, date_creation);

-- Index pour les recherches textuelles
CREATE INDEX CONCURRENTLY idx_employe_search
ON user_app_employe USING gin(to_tsvector('french', nom || ' ' || prenom));
```

### Partitioning (pour gros volumes)

```sql
-- Partitioning par année pour les entrées de paie
CREATE TABLE paie_app_entree_paie_2024 PARTITION OF paie_app_entree_paie
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE paie_app_entree_paie_2025 PARTITION OF paie_app_entree_paie
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## Configuration des Services

### Celery (Tâches Asynchrones)

```python
# rhBack/celery.py

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhBack.settings')

app = Celery('paie_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches
app.conf.update(
    task_routes={
        'paie_app.tasks.process_period': {'queue': 'payroll'},
        'paie_app.tasks.generate_payslips': {'queue': 'payslips'},
        'paie_app.tasks.send_notifications': {'queue': 'notifications'},
    },
    task_annotations={
        'paie_app.tasks.process_period': {'rate_limit': '10/m'},
        'paie_app.tasks.generate_payslips': {'rate_limit': '5/m'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)
```

### Démarrage des Services

```bash
# Script de démarrage des services (start_services.sh)
#!/bin/bash

# Démarrage de Redis
sudo systemctl start redis

# Démarrage de PostgreSQL
sudo systemctl start postgresql

# Démarrage de Celery Worker
celery -A rhBack worker --loglevel=info --queues=payroll,payslips,notifications &

# Démarrage de Celery Beat (tâches programmées)
celery -A rhBack beat --loglevel=info &

# Démarrage du serveur Django
uv run uvicorn rhBack.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration de Sécurité

### HTTPS et SSL

```nginx
# Configuration Nginx pour HTTPS
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /var/www/paie/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /static/ {
        alias /var/www/paie/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Firewall et Sécurité Réseau

```bash
# Configuration UFW (Ubuntu Firewall)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Autoriser SSH, HTTP et HTTPS
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Autoriser PostgreSQL et Redis uniquement en local
sudo ufw allow from 127.0.0.1 to any port 5432
sudo ufw allow from 127.0.0.1 to any port 6379
```

## Monitoring et Logging

### Configuration des Logs

```python
# Configuration logging dans settings.py
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
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': config('LOG_FILE', default='paie.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'paie_app': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Monitoring avec Prometheus

```python
# Métriques personnalisées
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
payroll_calculations = Counter('payroll_calculations_total', 'Total payroll calculations')
payslip_generations = Counter('payslip_generations_total', 'Total payslip generations')
api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])

# Histogrammes pour les temps de réponse
calculation_duration = Histogram('payroll_calculation_duration_seconds', 'Payroll calculation duration')
api_response_time = Histogram('api_response_time_seconds', 'API response time', ['endpoint'])

# Jauges pour les métriques en temps réel
active_periods = Gauge('active_payroll_periods', 'Number of active payroll periods')
pending_calculations = Gauge('pending_calculations', 'Number of pending calculations')
```

## Sauvegarde et Restauration

### Script de Sauvegarde Automatique

```bash
#!/bin/bash
# backup_paie.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/paie"
DB_NAME="paie_db"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Sauvegarde des fichiers media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/paie/media/

# Nettoyage des anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Log de la sauvegarde
echo "$(date): Backup completed - $DATE" >> /var/log/paie_backup.log
```

### Cron Job pour Sauvegarde Automatique

```bash
# Ajouter au crontab
# crontab -e

# Sauvegarde quotidienne à 2h du matin
0 2 * * * /usr/local/bin/backup_paie.sh

# Sauvegarde hebdomadaire complète le dimanche à 1h
0 1 * * 0 /usr/local/bin/full_backup_paie.sh
```

## Optimisation des Performances

### Configuration du Cache

```python
# Cache pour les données de référence
CACHE_SETTINGS = {
    'EMPLOYEE_CONTRACTS': 3600,  # 1 heure
    'PAYROLL_PARAMETERS': 7200,  # 2 heures
    'TAX_BRACKETS': 86400,       # 24 heures
    'DEDUCTION_RULES': 3600,     # 1 heure
}

# Utilisation du cache
from django.core.cache import cache

def get_employee_contract(employee_id, period_date):
    cache_key = f"contract_{employee_id}_{period_date}"
    contract = cache.get(cache_key)

    if contract is None:
        contract = fetch_contract_from_db(employee_id, period_date)
        cache.set(cache_key, contract, CACHE_SETTINGS['EMPLOYEE_CONTRACTS'])

    return contract
```

### Optimisation des Requêtes

```python
# Utilisation de select_related et prefetch_related
def get_payroll_entries_optimized(period_id):
    return entree_paie.objects.filter(
        periode_paie_id=period_id
    ).select_related(
        'employe_id',
        'employe_id__contrat_set',
        'periode_paie_id'
    ).prefetch_related(
        'employe_id__retenue_employe_set'
    )
```

## Maintenance Régulière

### Tâches de Maintenance Hebdomadaires

```python
# management/commands/weekly_maintenance.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Nettoyage des logs anciens
        self.cleanup_old_logs()

        # Optimisation de la base de données
        self.optimize_database()

        # Vérification de l'intégrité des données
        self.check_data_integrity()

        # Mise à jour des statistiques
        self.update_statistics()
```

### Monitoring de la Santé du Système

```python
# Health check endpoint
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    checks = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'celery': check_celery_workers(),
        'disk_space': check_disk_space(),
        'memory': check_memory_usage(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }, status=status_code)
```

---

*Pour plus d'informations sur la configuration des paramètres de paie, consultez le [Guide des Paramètres de Paie](payroll-parameters.md).*
