@echo off
chcp 65001 >nul
echo ========================================
echo   INSTALASI OTOMATISASI SBR
echo ========================================
echo.
echo Proses instalasi akan dimulai...
echo Harap tunggu, ini mungkin memakan waktu beberapa menit.
echo.

REM Cek apakah Python terinstal
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python tidak ditemukan!
    echo.
    echo Silakan install Python terlebih dahulu dari:
    echo https://www.python.org/downloads/
    echo.
    echo Pastikan centang "Add Python to PATH" saat instalasi!
    echo.
    pause
    exit /b 1
)

echo ✅ Python ditemukan
echo.

REM Buat virtual environment
echo 📦 Membuat virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ❌ Gagal membuat virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment berhasil dibuat
echo.

REM Aktifkan virtual environment
echo 🔧 Mengaktifkan virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Gagal mengaktifkan virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment aktif
echo.

REM Upgrade pip
echo 📦 Mengupgrade pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo 📦 Menginstall dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Gagal menginstall dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies berhasil diinstall
echo.

REM Install Playwright browsers
echo 🌐 Menginstall browser Playwright...
playwright install chromium
if errorlevel 1 (
    echo ❌ Gagal menginstall browser Playwright
    pause
    exit /b 1
)
echo ✅ Browser Playwright berhasil diinstall
echo.

REM Buat folder data jika belum ada
if not exist "data" (
    echo 📁 Membuat folder data...
    mkdir data
    echo ✅ Folder data berhasil dibuat
    echo.
)

REM Buat config WhatsApp jika belum ada
if not exist "config\whatsapp.json" (
    if exist "config\whatsapp.example.json" (
        echo 📝 Membuat config WhatsApp...
        copy config\whatsapp.example.json config\whatsapp.json >nul
        echo ✅ Config WhatsApp berhasil dibuat
        echo    Silakan edit config\whatsapp.json untuk mengatur nomor WhatsApp
        echo.
    )
)

echo ========================================
echo   ✅ INSTALASI SELESAI!
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Letakkan file Excel di folder "data"
echo 2. Jalankan "2_buka_chrome.bat" untuk membuka Chrome
echo 3. Login ke MATCHAPRO dan buka menu Direktori Usaha
echo 4. Jalankan "3_jalankan_autofill.bat" untuk memulai autofill
echo.
pause
