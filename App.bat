@echo off
title Imprest App Launcher
cd /d "%~dp0"

echo ============================================
echo      Railway Imprest Automator
echo ============================================
echo.

echo Checking app structure...
echo.

if not exist "app.py" (
    echo [ERROR] Missing: app.py
    goto :error_structure
)

if not exist "config.py" (
    echo [ERROR] Missing: config.py
    goto :error_structure
)

if not exist "core\balance_store.py" (
    echo [ERROR] Missing folder/files: core\
    goto :error_structure
)

if not exist "docx_engine\annexure1.py" (
    echo [ERROR] Missing folder/files: docx_engine\
    goto :error_structure
)

if not exist "ui\tab_generate.py" (
    echo [ERROR] Missing folder/files: ui\
    goto :error_structure
)

echo App structure OK.
echo.

echo Checking templates...
echo.

if not exist "templates\ANNEXURE 1 WITH 3 VOUCHERS.docx" (
    echo [ERROR] Missing:
    echo ANNEXURE 1 WITH 3 VOUCHERS.docx
    goto :error_templates
)

if not exist "templates\ANNEXURE 1 WITH 4 VOUCHERS With Stationery.docx" (
    echo [ERROR] Missing:
    echo ANNEXURE 1 WITH 4 VOUCHERS With Stationery.docx
    goto :error_templates
)

if not exist "templates\ANNEXURE 1 WITH 4 VOUCHERS Without Stationery.docx" (
    echo [ERROR] Missing:
    echo ANNEXURE 1 WITH 4 VOUCHERS Without Stationery.docx
    goto :error_templates
)

if not exist "templates\ANNEXTURE II LABOUR 3 VOUCHERS.docx" (
    echo [ERROR] Missing:
    echo ANNEXTURE II LABOUR 3 VOUCHERS.docx
    goto :error_templates
)

if not exist "templates\ANNEXTURE II LABOUR 4 VOUCHERS.docx" (
    echo [ERROR] Missing:
    echo ANNEXTURE II LABOUR 4 VOUCHERS.docx
    goto :error_templates
)

echo All templates found.
echo.

echo Checking Python packages...
echo.

python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [WARNING] streamlit is not installed.
    echo Installing dependencies from requirements.txt...
    echo.
    python -m pip install -r Requirements.txt
    echo.
)

python -c "import docx" 2>nul
if errorlevel 1 (
    echo [WARNING] python-docx is not installed.
    echo Installing dependencies from requirements.txt...
    echo.
    python -m pip install -r Requirements.txt
    echo.
)

echo Starting application...
echo.

python -m streamlit run app.py

goto :end

:error_structure
echo.
echo ============================================
echo The application cannot start because required
echo app files/folders are missing.
echo.
echo Make sure this .bat file sits directly inside
echo the railway_imprest folder, alongside app.py,
echo config.py, core\, docx_engine\, and ui\.
echo ============================================
echo.
pause
goto :end

:error_templates
echo.
echo ============================================
echo The application cannot start because one or
echo more required template files are missing.
echo.
echo Please copy all template files into:
echo.
echo templates\
echo ============================================
echo.
pause

:end