Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  CLEANING ALL SYSTEM CACHES (SQLite DB, Python __pycache__, Vite Cache)" -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan

if (Test-Path "backend\finance_controller.db") {
    Remove-Item -Path "backend\finance_controller.db" -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] Removed backend\finance_controller.db" -ForegroundColor Green
}

Get-ChildItem -Path . -Include "__pycache__", ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] Removed $($_.FullName)" -ForegroundColor Green
}

if (Test-Path "frontend\node_modules\.vite") {
    Remove-Item -Path "frontend\node_modules\.vite" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] Removed frontend\node_modules\.vite" -ForegroundColor Green
}

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  SUCCESS: All caches deleted! System is ready with fresh state." -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Cyan
