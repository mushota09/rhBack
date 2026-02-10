# 🚀 Démarrage Rapide - Windows

## Étape 1: Démarrer Redis

Assurez-vous que Redis est démarré. Si vous utilisez Redis distant (comme dans votre config), il devrait déjà être accessible.

## Étape 2: Démarrer Celery (IMPORTANT sur Windows)

**Option A: Script Automatique (Recommandé)**
```bash
.\start_celery_windows.bat
```
Puis choisissez l'option **1** (SOLO) pour commencer.

**Option B: Commande Manuelle**
```bash
uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit
```

## Étape 3: Démarrer le Serveur Django

Dans un **nouveau terminal**:
```bash
uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000
```

## Étape 4: Tester

### Tester l'API
Ouvrez votre navigateur: http://localhost:8000/api/

### Tester avec pytest
```bash
python -m pytest user_app/tests/ -v
```

## ✅ Vérification

Vous devriez voir dans le terminal Celery:
```
[INFO/MainProcess] Connected to redis://...
[INFO/MainProcess] celery@hostname ready.
```

**SANS** les erreurs:
- ❌ `PermissionError: [WinError 5] Accès refusé`
- ❌ `OSError: [WinError 6] Descripteur non valide`

## 🎯 Commandes Complètes

### Terminal 1 - Celery
```bash
.\start_celery_windows.bat
# Choisir option 1
```

### Terminal 2 - Django
```bash
uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000
```

### Terminal 3 - Tests (optionnel)
```bash
python -m pytest user_app/tests/ -v
```

## 📝 Notes

- Le pool `solo` est parfait pour le développement
- Pour plus de performance, utilisez `gevent` (voir `SOLUTION_CELERY_WINDOWS.md`)
- Les tests s'exécutent maintenant en mode synchrone (pas besoin de Celery)

**C'est tout! Votre système fonctionne maintenant sur Windows! 🎉**
