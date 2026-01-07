@echo off
chcp 65001 >nul
echo ========================================
echo   PEMBERSIHAN FILE TIDAK PERLU
echo ========================================
echo.
echo Script ini akan membersihkan:
echo   - Log lama (lebih dari 30 hari)
echo   - Screenshot lama (lebih dari 30 hari)
echo   - File __pycache__
echo   - File .pyc
echo   - File temporary lainnya
echo.

set CONFIRM=
set /p CONFIRM="Lanjutkan pembersihan? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Pembersihan dibatalkan.
    pause
    exit /b 0
)

echo.
echo 🧹 Memulai pembersihan...
echo.

REM Hapus __pycache__
echo 📁 Menghapus __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo    Menghapus: %%d
    rd /s /q "%%d" 2>nul
)
echo ✅ __pycache__ dihapus
echo.

REM Hapus .pyc files
echo 📄 Menghapus file .pyc...
del /s /q *.pyc 2>nul
echo ✅ File .pyc dihapus
echo.

REM Hapus log lama (lebih dari 30 hari)
echo 📊 Menghapus log lama (>30 hari)...
if exist "artifacts\logs\" (
    forfiles /p "artifacts\logs" /s /m *.csv /d -30 /c "cmd /c del @path" 2>nul
    forfiles /p "artifacts\logs" /s /m *.html /d -30 /c "cmd /c del @path" 2>nul
    echo ✅ Log lama dihapus
) else (
    echo ℹ️  Folder logs tidak ditemukan
)
echo.

REM Hapus screenshot lama (lebih dari 30 hari)
echo 📸 Menghapus screenshot lama (>30 hari)...
if exist "artifacts\screenshots\" (
    forfiles /p "artifacts\screenshots" /s /m *.png /d -30 /c "cmd /c del @path" 2>nul
    echo ✅ Screenshot lama dihapus
) else (
    echo ℹ️  Folder screenshots tidak ditemukan
)
echo.

if exist "artifacts\screenshots_cancel\" (
    forfiles /p "artifacts\screenshots_cancel" /s /m *.png /d -30 /c "cmd /c del @path" 2>nul
    echo ✅ Screenshot cancel lama dihapus
) else (
    echo ℹ️  Folder screenshots_cancel tidak ditemukan
)
echo.

REM Hapus folder kosong
echo 📁 Menghapus folder kosong...
for /f "delims=" %%d in ('dir /ad /b /s artifacts 2^>nul ^| sort /r') do (
    rd "%%d" 2>nul
)
echo ✅ Folder kosong dihapus
echo.

REM Hapus chromium_attention.flag jika ada
if exist "artifacts\chromium_attention.flag" (
    echo 🗑️  Menghapus chromium_attention.flag...
    del /q "artifacts\chromium_attention.flag" 2>nul
    echo ✅ chromium_attention.flag dihapus
    echo.
)

echo ========================================
echo   ✅ PEMBERSIHAN SELESAI!
echo ========================================
echo.
echo File yang dibersihkan:
echo   ✅ __pycache__ dan .pyc
echo   ✅ Log lama (>30 hari)
echo   ✅ Screenshot lama (>30 hari)
echo   ✅ Folder kosong
echo   ✅ File temporary
echo.
pause
