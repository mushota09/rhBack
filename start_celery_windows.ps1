# Script PowerShell pour démarrer Celery sur Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage de Celery pour Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Celery sur Windows nécessite le pool 'solo' ou 'gevent'" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Pool SOLO (simple, un seul worker)" -ForegroundColor Green
Write-Host "Option 2: Pool GEVENT (parallèle, nécessite gevent)" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Choisissez (1 ou 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Démarrage avec pool SOLO..." -ForegroundColor Green
    Write-Host ""
    uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit
}
elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Vérification de gevent..." -ForegroundColor Yellow

    $geventInstalled = uv pip show gevent 2>$null
    if (-not $geventInstalled) {
        Write-Host "gevent n'est pas installé. Installation..." -ForegroundColor Yellow
        uv pip install gevent
    }

    Write-Host ""
    Write-Host "Démarrage avec pool GEVENT..." -ForegroundColor Green
    Write-Host ""
    uv run celery -A rhBack worker -l info --pool=gevent --concurrency=10 -Q payroll,payslips,exports,audit
}
else {
    Write-Host "Choix invalide. Utilisation du pool SOLO par défaut..." -ForegroundColor Red
    Write-Host ""
    uv run celery -A rhBack worker -l info --pool=solo -Q payroll,payslips,exports,audit
}

Write-Host ""
Write-Host "Appuyez sur une touche pour quitter..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
