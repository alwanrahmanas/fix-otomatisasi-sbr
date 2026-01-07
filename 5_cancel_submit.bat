@echo off
chcp 65001 >nul
echo ========================================
echo   CANCEL SUBMIT SBR
echo ========================================
echo.
echo Tool ini akan membuka form dan menekan tombol
echo "Cancel Submit" secara otomatis.
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

echo Silakan isi konfigurasi berikut:
echo.

REM Tanya baris mulai
set START_ROW=1
set /p START_ROW="📊 Mulai dari baris ke- (default: 1): "
if "%START_ROW%"=="" set START_ROW=1
echo.

REM Tanya baris akhir
set END_ROW=10
set /p END_ROW="📊 Sampai baris ke- (default: 10): "
if "%END_ROW%"=="" set END_ROW=10
echo.

REM Tanya metode pencocokan
echo 🔍 Metode pencocokan data:
echo    1. IDSBR (cocokkan berdasarkan ID SBR)
echo    2. Nama (cocokkan berdasarkan nama usaha)
echo    3. Index (urutan baris di tabel)
echo.
set MATCH_METHOD=2
set /p MATCH_METHOD="   Pilih metode (1/2/3, default: 2-Nama): "
if "%MATCH_METHOD%"=="" set MATCH_METHOD=2

if "%MATCH_METHOD%"=="1" (
    set MATCH_BY=idsbr
) else if "%MATCH_METHOD%"=="2" (
    set MATCH_BY=name
) else (
    set MATCH_BY=index
)
echo    ✅ Menggunakan metode: %MATCH_BY%
echo.

echo ========================================
echo   MEMULAI CANCEL SUBMIT...
echo ========================================
echo.
echo Konfigurasi:
echo   📊 Baris       : %START_ROW% sampai %END_ROW%
echo   🔍 Metode      : %MATCH_BY%
echo.
echo ⏳ Proses dimulai...
echo ========================================
echo.

python sbr_cancel.py --match-by %MATCH_BY% --start %START_ROW% --end %END_ROW%

echo.
echo ========================================
echo   PROSES SELESAI!
echo ========================================
echo.
echo 📊 Log hasil tersimpan di folder: artifacts\logs
echo.
pause
