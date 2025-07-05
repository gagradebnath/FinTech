@echo off
title FinGuard Auto Setup
color 0A

echo.
echo ===============================================
echo   🚀 FinGuard Automatic Setup v3.0
echo ===============================================
echo.
echo   This will automatically:
echo   ✅ Install MySQL (if needed)
echo   ✅ Install Python packages
echo   ✅ Create database and tables  
echo   ✅ Add test accounts
echo   ✅ Start the application
echo.
echo   📝 NOTE: You'll be asked for MySQL credentials
echo       during the setup process.
echo.
echo   Ready? Press any key to continue...
echo ===============================================
pause > nul

echo.
echo 🔄 Starting automatic setup...
echo.

python auto_setup.py

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo ✅ Setup completed successfully!
    echo ===============================================
    echo.
    echo 🌐 Open http://localhost:5000 in your browser
    echo 🔑 Login accounts:
    echo    admin/admin  (Administrator)
    echo    agent/agent  (Financial Agent)
    echo    user/user    (Regular User)
    echo.
) else (
    echo.
    echo ===============================================
    echo ❌ Setup encountered an error
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
