@echo off
echo =========================================================================
echo   CLEANING ALL SYSTEM CACHES (SQLite DB, Python __pycache__, Vite Cache)
echo =========================================================================

if exist backend\finance_controller.db (
    del /f /q backend\finance_controller.db 2>nul
    echo  [+] Removed backend\finance_controller.db
)

for /d /r . %%d in (__pycache__ .pytest_cache) do (
    if exist "%%d" (
        rd /s /q "%%d" 2>nul
        echo  [+] Removed %%d
    )
)

if exist frontend\node_modules\.vite (
    rd /s /q frontend\node_modules\.vite 2>nul
    echo  [+] Removed frontend\node_modules\.vite
)

echo =========================================================================
echo   SUCCESS: All caches deleted! Server will start with a fresh state.
echo =========================================================================
