@echo off
chcp 65001 >nul
echo ========================================
echo   BATCH RUNNER - PROSES MASSAL
echo ========================================
echo.
echo Batch Runner akan memproses data dalam jumlah besar
echo secara otomatis dengan membagi menjadi batch-batch kecil.
echo.

REM Cek apakah virtual environment ada
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ ERROR: Virtual environment tidak ditemukan!
    echo.
    echo Silakan jalankan "1_install.bat" terlebih dahulu.
    echo.
    pause
    exit /b 1
)

REM Aktifkan virtual environment
call .venv\Scripts\activate.bat

echo ⚠️  PERHATIAN:
echo    - Pastikan Chrome sudah dibuka (jalankan 2_buka_chrome.bat)
echo    - Pastikan sudah login ke MATCHAPRO
echo    - Pastikan file Excel sudah ada di folder 'data'
echo.
echo ℹ️  Konfigurasi batch dapat diubah di file batch_runner.py
echo    (BATCH_SIZE, START_FROM, dll)
echo.

set CONFIRM=
set /p CONFIRM="Lanjutkan? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Batch runner dibatalkan.
    pause
    exit /b 0
)

echo.
echo ========================================
echo   MEMULAI BATCH RUNNER...
echo ========================================
echo.

python batch_runner.py

echo.
echo ========================================
echo   BATCH RUNNER SELESAI!
echo ========================================
echo.
echo 📊 Log batch tersimpan di: artifacts\logs\batch_runner
echo.
pause
