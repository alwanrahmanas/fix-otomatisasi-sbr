@echo off
chcp 65001 >nul
echo ========================================
echo   MEMBUKA CHROME UNTUK SBR
echo ========================================
echo.
echo Chrome akan dibuka dengan mode debugging...
echo.
echo PENTING:
echo 1. Setelah Chrome terbuka, login ke MATCHAPRO
echo 2. Buka menu "Direktori Usaha"
echo 3. JANGAN TUTUP jendela Chrome ini!
echo 4. Biarkan Chrome tetap terbuka saat menjalankan autofill
echo.
echo ========================================
echo.

REM Cek apakah Chrome sudah terinstal
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome ditemukan
    echo 🌐 Membuka Chrome dengan mode debugging...
    echo.
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
    echo.
    echo ✅ Chrome berhasil dibuka!
    echo.
    echo Silakan:
    echo 1. Login ke https://matchapro.web.bps.go.id/
    echo 2. Buka menu "Direktori Usaha"
    echo 3. Setelah siap, jalankan "3_jalankan_autofill.bat"
    echo.
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome ditemukan (32-bit)
    echo 🌐 Membuka Chrome dengan mode debugging...
    echo.
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
    echo.
    echo ✅ Chrome berhasil dibuka!
    echo.
    echo Silakan:
    echo 1. Login ke https://matchapro.web.bps.go.id/
    echo 2. Buka menu "Direktori Usaha"
    echo 3. Setelah siap, jalankan "3_jalankan_autofill.bat"
    echo.
) else (
    echo ❌ ERROR: Chrome tidak ditemukan!
    echo.
    echo Silakan install Google Chrome terlebih dahulu dari:
    echo https://www.google.com/chrome/
    echo.
)

pause
