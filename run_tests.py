#!/usr/bin/env python
"""
Script pour lancer les tests en forçant le rechargement des modules
"""
import sys
import os

# Bloquer la génération de .pyc
sys.dont_write_bytecode = True

# Forcer le rechargement des modules
if 'adrf_flex_fields' in sys.modules:
    del sys.modules['adrf_flex_fields']
if 'adrf_flex_fields.views' in sys.modules:
    del sys.modules['adrf_flex_fields.views']

# Lancer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhBack.settings')

import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    django.setup()
    execute_from_command_line(['manage.py', 'test', 'user_app.tests.test_rbac_flexfields', '--keepdb', '-v', '2'])
