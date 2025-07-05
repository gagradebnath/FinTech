@echoecho.
echo ===============================================
echo   [ROCKET] FinGuard Automatic Setup v3.0
echo ===============================================
echo.
echo   This will automatically:
echo   [OK] Install MySQL (if needed)
echo   [OK] Install Python packages
echo   [REFRESH] Create fresh database (removes existing)
echo   [OK] Add test accounts
echo   [OK] Start the application
echo.
echo   [WARNING] This will delete any existing
echo       fin_guard database for a clean setup!
echo.
echo   [NOTE] You'll be asked for MySQL credentials
echo       during the setup process.
echo.
echo   Ready? Press any key to continue...ul 2>&1
title FinGuard Auto Setup
color 0A

echo.
echo ===============================================
echo   🚀 FinGuard Automatic Setup v3.0
echo ===============================================
echo.
echo   This will automatically:
echo   Install MySQL (if needed)
echo   Install Python packages
echo   Create fresh database (removes existing)
echo   Add test accounts
echo   Start the application
echo.
echo   WARNING: This will delete any existing
echo       fin_guard database for a clean setup!
echo.
echo   NOTE: You'll be asked for MySQL credentials
echo       during the setup process.
echo.
echo   Ready? Press any key to continue...
echo ===============================================
pause > nul

echo.
echo  Starting automatic setup...
echo.

set PYTHONIOENCODING=utf-8
python auto_setup.py

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo [OK] Setup completed successfully!
    echo ===============================================
    echo.
    echo [WEB] Open http://localhost:5000 in your browser
    echo [KEY] Login accounts:
    echo    admin/admin  (Administrator)
    echo    agent/agent  (Financial Agent)
    echo    user/user    (Regular User)
    echo.
) else (
    echo.
    echo ===============================================
    echo [ERROR] Setup encountered an error
    echo ===============================================
    echo.
    echo Please check the error messages above and:
    echo 1. Ensure you have internet connection
    echo 2. Run as Administrator if needed
    echo 3. Install MySQL manually if auto-install failed
    echo.
)

echo Press any key to exit...
pause > nul
