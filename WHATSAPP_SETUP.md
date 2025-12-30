# WhatsApp Notification Setup Guide

## Overview

Fitur notifikasi WhatsApp otomatis mengirimkan ringkasan hasil autofill SBR setelah proses selesai. Notifikasi mencakup:
- Jumlah sukses, warning, dan error
- Detail top 5 error dengan IDSBR dan nama usaha
- Durasi eksekusi
- Link ke file log

## Prerequisites

1. **Chrome/Chromium** sudah terinstall
2. **WhatsApp Web** bisa diakses
3. **Selenium** sudah terinstall (`pip install selenium`)

## Setup Langkah demi Langkah

### 1. Install Dependencies

```powershell
pip install selenium
```

### 2. Konfigurasi WhatsApp

Buat file konfigurasi dari template:

```powershell
copy config\whatsapp.example.json config\whatsapp.json
```

Edit `config\whatsapp.json`:

```json
{
  "enabled": true,
  "phone_number": "+6281234567890",
  "group_name": "",
  "notify_on_completion": true,
  "notify_on_error_threshold": 0,
  "chrome_profile_path": "C:\\ChromeProfileSBR",
  "wait_for_login_seconds": 30,
  "message_template": "🤖 *SBR Autofill Report*\\n\\n📅 Run ID: {run_id}\\n⏰ Started: {started_at}\\n⏱️ Duration: {duration}\\n\\n📊 *Summary*\\n✅ Success: {ok_count}\\n⚠️ Warnings: {warn_count}\\n❌ Errors: {error_count}\\n📝 Total: {total_count}\\n\\n{error_details}\\n📁 Log: {log_path}"
}
```

**Penjelasan Field:**

- `enabled`: Set `true` untuk mengaktifkan notifikasi
- `phone_number`: Nomor WhatsApp tujuan (format: +62xxx) - untuk personal chat
- `group_name`: Nama grup WhatsApp - untuk grup chat (kosongkan jika pakai phone_number)
- `notify_on_completion`: Kirim notifikasi saat selesai
- `notify_on_error_threshold`: Minimum jumlah error untuk trigger notifikasi (0 = selalu kirim)
- `chrome_profile_path`: Path ke Chrome profile (gunakan yang sama dengan CDP atau buat baru)
- `wait_for_login_seconds`: Waktu tunggu untuk scan QR code (detik)
- `message_template`: Template pesan (bisa dikustomisasi)

### 3. Login WhatsApp Web (First Time Only)

Pertama kali menggunakan, Anda perlu login ke WhatsApp Web:

1. Jalankan autofill dengan WhatsApp notification:
   ```powershell
   python sbr_fill.py --match-by idsbr --start 1 --end 5 --whatsapp-config config\whatsapp.json
   ```

2. Browser Chrome akan terbuka otomatis ke WhatsApp Web
3. Scan QR code dengan WhatsApp di HP Anda
4. Tunggu sampai login berhasil
5. Session akan tersimpan di Chrome profile, tidak perlu scan QR lagi untuk run berikutnya

### 4. Penggunaan

#### Opsi A: Menggunakan Config File

```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 10 --whatsapp-config config\whatsapp.json
```

#### Opsi B: Override dengan CLI Arguments

```powershell
# Kirim ke nomor personal
python sbr_fill.py --match-by idsbr --start 1 --end 10 --whatsapp-number "+6281234567890"

# Kirim ke grup
python sbr_fill.py --match-by idsbr --start 1 --end 10 --whatsapp-group "Tim SBR Bulungan"
```

#### Opsi C: Kombinasi Config + CLI Override

```powershell
# Config file sebagai default, override nomor via CLI
python sbr_fill.py --match-by idsbr --start 1 --end 10 --whatsapp-config config\whatsapp.json --whatsapp-number "+6289876543210"
```

## Contoh Pesan Notifikasi

```
🤖 *SBR Autofill Report*

📅 Run ID: 14-30-45
⏰ Started: 2025-12-30T14:30:45
⏱️ Duration: 5m 23s

📊 *Summary*
✅ Success: 45
⚠️ Warnings: 3
❌ Errors: 2
📝 Total: 50

🔴 *Top Errors:*
1. 1234567890 - PT MAJU JAYA
   Stage: SUBMIT
   Note: CODE:SUBMIT_VALIDATION Maaf ada isian yang harus diperbaiki

2. 0987654321 - CV BERKAH SELALU
   Stage: FILL
   Note: Exception isi form: Timeout waiting for element

📁 Log: C:\...\artifacts\logs\2025-12-30\log_sbr_autofill_14-30-45.csv
```

## Troubleshooting

### QR Code Tidak Muncul / Timeout

**Solusi:**
- Pastikan Chrome profile path benar
- Coba hapus folder Chrome profile dan login ulang
- Tingkatkan `wait_for_login_seconds` di config (misal 60 detik)

### Kontak/Grup Tidak Ditemukan

**Solusi:**
- Pastikan nomor WhatsApp ditulis dengan format internasional (+62xxx)
- Untuk grup, pastikan nama grup persis sama (case-sensitive)
- Coba chat manual dulu ke kontak/grup tersebut di WhatsApp Web

### Pesan Tidak Terkirim

**Solusi:**
- Cek koneksi internet
- Pastikan WhatsApp Web tidak sedang dibuka di browser lain
- Coba restart Chrome dan login ulang

### Browser Tidak Auto-Close

**Solusi:**
- Ini normal jika ada error
- Browser akan auto-close setelah pesan berhasil terkirim
- Jika stuck, close manual dan cek log error

## Advanced Configuration

### Custom Message Template

Edit `message_template` di config file. Available variables:

- `{run_id}`: ID run
- `{started_at}`: Waktu mulai (ISO format)
- `{duration}`: Durasi eksekusi
- `{ok_count}`: Jumlah sukses
- `{warn_count}`: Jumlah warning
- `{error_count}`: Jumlah error
- `{total_count}`: Total rows processed
- `{error_details}`: Detail error (auto-generated)
- `{log_path}`: Path ke log file

Contoh custom template:

```json
{
  "message_template": "✨ *Laporan SBR Otomatis*\\n\\nHai Tim! Proses autofill sudah selesai:\\n\\n✅ Berhasil: {ok_count}\\n❌ Gagal: {error_count}\\n\\nDurasi: {duration}\\n\\n{error_details}\\n\\nCek detail di: {log_path}"
}
```

### Conditional Notification

Hanya kirim notifikasi jika ada error >= 5:

```json
{
  "enabled": true,
  "notify_on_error_threshold": 5
}
```

### Multiple Recipients

Untuk kirim ke multiple recipients, gunakan grup WhatsApp atau jalankan script multiple kali dengan nomor berbeda.

## Integration dengan Profile CLI

Tambahkan WhatsApp config ke profile CLI Anda:

`config/profile_autofill.json`:
```json
{
  "excel": "data/Profiling.xlsx",
  "match_by": "idsbr",
  "stop_on_error": false,
  "whatsapp_config": "config/whatsapp.json"
}
```

Lalu jalankan:
```powershell
python sbr_fill.py --profile config/profile_autofill.json --start 1 --end 100
```

## Security Notes

- Chrome profile menyimpan session WhatsApp Web
- Jangan share Chrome profile folder ke orang lain
- Gunakan Chrome profile terpisah untuk keamanan
- WhatsApp session bisa expired, perlu login ulang jika lama tidak dipakai

## FAQ

**Q: Apakah bisa kirim ke multiple nomor sekaligus?**
A: Tidak langsung. Solusinya: kirim ke grup WhatsApp yang berisi semua penerima.

**Q: Apakah perlu scan QR code setiap kali run?**
A: Tidak. Session tersimpan di Chrome profile. Hanya perlu scan QR pertama kali atau jika session expired.

**Q: Apakah browser akan tetap terbuka setelah kirim pesan?**
A: Tidak. Browser otomatis close setelah pesan terkirim untuk memory efficiency.

**Q: Bisa pakai pywhatkit instead of Selenium?**
A: Tidak direkomendasikan. Pywhatkit kurang reliable untuk automation dan sering bermasalah dengan timing.

**Q: Apakah bisa customize format pesan?**
A: Ya! Edit `message_template` di config file sesuai kebutuhan.

**Q: Bagaimana jika WhatsApp Web down?**
A: Notifikasi akan gagal, tapi autofill tetap jalan normal. Error akan di-print di console.
