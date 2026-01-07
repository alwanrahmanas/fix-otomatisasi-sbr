@echo off
chcp 65001 >nul
echo ========================================
echo   OTOMATISASI AUTOFILL SBR
echo ========================================
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

REM Tanya file Excel
set EXCEL_FILE=
echo 📁 File Excel yang akan diproses:
echo    (Kosongkan jika file Excel ada di folder 'data')
set /p EXCEL_FILE="   Masukkan path file Excel (atau tekan Enter): "
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
set MATCH_METHOD=1
set /p MATCH_METHOD="   Pilih metode (1/2/3, default: 1): "
if "%MATCH_METHOD%"=="" set MATCH_METHOD=1

if "%MATCH_METHOD%"=="1" (
    set MATCH_BY=idsbr
) else if "%MATCH_METHOD%"=="2" (
    set MATCH_BY=name
) else (
    set MATCH_BY=index
)
echo    ✅ Menggunakan metode: %MATCH_BY%
echo.

REM Tanya apakah ingin stop on error
echo ⚠️  Hentikan proses jika ada error?
set STOP_ERROR=
set /p STOP_ERROR="   (Y/N, default: Y): "
if "%STOP_ERROR%"=="" set STOP_ERROR=Y

set STOP_FLAG=
if /i "%STOP_ERROR%"=="Y" set STOP_FLAG=--stop-on-error
echo.

REM Tanya apakah ingin kirim notifikasi WhatsApp
echo 📱 Kirim notifikasi WhatsApp setelah selesai?
set USE_WA=
set /p USE_WA="   (Y/N, default: N): "
if "%USE_WA%"=="" set USE_WA=N

set WA_FLAG=
if /i "%USE_WA%"=="Y" (
    if exist "config\whatsapp.json" (
        set WA_FLAG=--whatsapp-config config\whatsapp.json
        echo    ✅ Notifikasi WhatsApp akan dikirim
    ) else (
        echo    ⚠️  File config\whatsapp.json tidak ditemukan
        echo    ℹ️  Notifikasi WhatsApp dilewati
    )
)
echo.

echo ========================================
echo   MEMULAI AUTOFILL...
echo ========================================
echo.
echo Konfigurasi:
echo   📁 File Excel  : %EXCEL_FILE%
if "%EXCEL_FILE%"=="" echo                  (auto-detect dari folder 'data')
echo   📊 Baris       : %START_ROW% sampai %END_ROW%
echo   🔍 Metode      : %MATCH_BY%
echo   ⚠️  Stop on error: %STOP_ERROR%
echo   📱 WhatsApp    : %USE_WA%
echo.
echo ⏳ Proses dimulai...
echo ========================================
echo.

REM Jalankan autofill
if "%EXCEL_FILE%"=="" (
    python sbr_fill.py --match-by %MATCH_BY% --start %START_ROW% --end %END_ROW% %STOP_FLAG% %WA_FLAG%
) else (
    python sbr_fill.py --excel "%EXCEL_FILE%" --match-by %MATCH_BY% --start %START_ROW% --end %END_ROW% %STOP_FLAG% %WA_FLAG%
)

echo.
echo ========================================
echo   PROSES SELESAI!
echo ========================================
echo.
echo 📊 Log hasil tersimpan di folder: artifacts\logs
echo 📸 Screenshot tersimpan di folder: artifacts\screenshots
echo.
pause
