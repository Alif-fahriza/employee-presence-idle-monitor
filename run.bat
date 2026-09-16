@echo off
echo ======================================================
echo   Employee Presence & Idle-Time Monitor
echo ======================================================
echo.

:: Pindah ke folder script ini berada
cd /d "%~dp0"

:: ── Cari Python di PATH ──
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON=python
    goto :found
)

:: ── Coba beberapa lokasi default Python di Windows ──
set PYTHON=
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%PROGRAMFILES%\Python311\python.exe"
    "%PROGRAMFILES%\Python310\python.exe"
    "%PROGRAMFILES%\Python39\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
) do (
    if not defined PYTHON if exist "%%~P" set PYTHON=%%~P
)

:found
if not defined PYTHON (
    echo [ERROR] Python tidak ditemukan.
    echo.
    echo Pastikan Python sudah terinstall dan ditambahkan ke PATH,
    echo atau install Python dari https://python.org
    echo.
    echo Atau jalankan langsung: python main.py
    pause
    exit /b 1
)

echo [OK] Python ditemukan: %PYTHON%
echo [OK] Menjalankan Employee Presence Monitor...
echo.

"%PYTHON%" main.py

echo.
echo Program selesai.
pause
