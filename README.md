# 🤖 Otomatisasi Profiling SBR - Panduan Lengkap untuk Pemula

> **Software otomatis untuk mengisi Profiling SBR di MATCHAPRO**  
> Tidak perlu coding! Cukup klik file .bat dan ikuti instruksi.

---

## 📋 Daftar Isi

- [Apa itu Otomatisasi SBR?](#-apa-itu-otomatisasi-sbr)
- [Persiapan Awal](#-persiapan-awal)
- [Cara Menggunakan (3 Langkah Mudah)](#-cara-menggunakan-3-langkah-mudah)
- [Fitur-Fitur](#-fitur-fitur)
- [Troubleshooting](#-troubleshooting)
- [FAQ (Pertanyaan Umum)](#-faq-pertanyaan-umum)
- [Panduan Lanjutan](#-panduan-lanjutan)

---

## 🎯 Apa itu Otomatisasi SBR?

Software ini membantu Anda mengisi **Profiling SBR di MATCHAPRO** secara otomatis dari file Excel. 

**Keuntungan:**
- ⚡ **Hemat Waktu**: Isi ratusan data dalam hitungan menit
- ✅ **Akurat**: Mengurangi kesalahan input manual
- 📊 **Laporan Lengkap**: Log otomatis untuk setiap proses
- 📱 **Notifikasi WhatsApp**: Dapat dikirim otomatis setelah selesai
- 🔄 **Resume Otomatis**: Lanjutkan dari data yang gagal

**Dikembangkan dari:** [OtomatisasiSBR](https://github.com/yuneko11/OtomatisasiSBR.git) oleh Yuneko/Uul - BPS Kabupaten Buru Selatan

---

## 🛠️ Persiapan Awal

### Yang Harus Diinstal:

1. **Python 3.10 atau lebih baru**
   - Download dari: https://www.python.org/downloads/
   - ⚠️ **PENTING**: Centang "Add Python to PATH" saat instalasi!

2. **Google Chrome**
   - Download dari: https://www.google.com/chrome/
   - Gunakan Chrome versi terbaru

3. **File Excel Profiling SBR**
   - Format resmi dari BPS
   - Harus ada kolom: IDSBR, Nama Usaha, Status, Email, dll.

### Struktur Folder:

```
fix-otomatisasi-sbr/
├── 1_install.bat           ← Klik ini untuk instalasi
├── 2_buka_chrome.bat        ← Klik ini untuk buka Chrome
├── 3_jalankan_autofill.bat  ← Klik ini untuk autofill
├── 4_batch_runner.bat       ← Untuk proses data banyak
├── 5_cancel_submit.bat      ← Untuk cancel submit
├── data/                    ← Letakkan file Excel di sini
├── config/                  ← File konfigurasi
└── artifacts/               ← Hasil log dan screenshot
```

---

## 🚀 Cara Menggunakan (3 Langkah Mudah)

### Langkah 1: Instalasi (Hanya Sekali)

1. **Klik 2x file `1_install.bat`**
2. Tunggu proses instalasi selesai (5-10 menit)
3. Jika berhasil, akan muncul pesan "INSTALASI SELESAI!"

**Troubleshooting:**
- Jika muncul error "Python tidak ditemukan" → Install Python dulu
- Jika gagal install → Pastikan koneksi internet stabil

---

### Langkah 2: Buka Chrome dan Login MATCHAPRO

1. **Klik 2x file `2_buka_chrome.bat`**
2. Chrome akan terbuka otomatis
3. **Login ke MATCHAPRO**: https://matchapro.web.bps.go.id/
4. **Buka menu "Direktori Usaha"**
5. **JANGAN TUTUP Chrome** - biarkan tetap terbuka!

**Tips:**
- Chrome ini khusus untuk otomatisasi, terpisah dari Chrome biasa Anda
- Login akan tersimpan, jadi tidak perlu login ulang setiap kali

---

### Langkah 3: Jalankan Autofill

1. **Letakkan file Excel** di folder `data/`
2. **Klik 2x file `3_jalankan_autofill.bat`**
3. **Isi pertanyaan** yang muncul:
   ```
   📁 File Excel: (tekan Enter jika sudah di folder data)
   📊 Mulai dari baris: 1
   📊 Sampai baris: 10
   🔍 Metode: 1 (IDSBR)
   ⚠️ Stop on error: Y
   📱 WhatsApp: N
   ```
4. **Tekan Enter** untuk mulai
5. **Tunggu proses selesai** - jangan tutup Chrome!

**Hasil:**
- Log tersimpan di: `artifacts/logs/`
- Screenshot tersimpan di: `artifacts/screenshots/`

---

## ✨ Fitur-Fitur

### 1. 🔄 Batch Runner (Proses Data Banyak)

Untuk memproses **ratusan atau ribuan data** sekaligus:

1. **Klik 2x file `4_batch_runner.bat`**
2. Script akan otomatis:
   - Membagi data menjadi batch kecil (30 baris per batch)
   - Memproses satu per satu
   - Lanjut otomatis jika ada yang gagal
   - Kirim laporan lengkap

**Konfigurasi** (edit file `batch_runner.py`):
```python
BATCH_SIZE = 30        # Ukuran batch (baris per batch)
START_FROM = 1         # Mulai dari baris ke-
```

---

### 2. 📱 Notifikasi WhatsApp

Kirim laporan otomatis ke WhatsApp setelah proses selesai!

**Setup:**
1. Copy file: `config/whatsapp.example.json` → `config/whatsapp.json`
2. Edit `config/whatsapp.json`:
   ```json
   {
     "enabled": true,
     "phone_number": "+6281234567890",
     "chrome_profile_path": "C:\\ChromeProfileSBR"
   }
   ```
3. Saat menjalankan autofill, pilih **Y** untuk WhatsApp
4. **Scan QR code** (hanya pertama kali)

**Isi Notifikasi:**
- ✅ Jumlah data berhasil
- ❌ Jumlah data gagal
- ⏱️ Durasi proses
- 📊 Detail error (top 5)

Lihat panduan lengkap: [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

---

### 3. ❌ Cancel Submit

Untuk membatalkan submit data yang sudah diisi:

1. **Klik 2x file `5_cancel_submit.bat`**
2. Isi range baris yang ingin di-cancel
3. Script akan otomatis:
   - Buka form satu per satu
   - Klik tombol "Cancel Submit"
   - Simpan log hasil

---

### 4. 📊 Resume Otomatis

Jika proses terhenti atau ada error, Anda bisa **lanjutkan dari yang gagal**:

**Cara Manual:**
```cmd
python sbr_fill.py --match-by idsbr --start 1 --end 100 --resume
```

**Cara Otomatis:**
- Batch Runner sudah otomatis pakai mode resume
- Data yang sudah OK akan dilewati
- Data yang ERROR akan diproses ulang

---

## 🔧 Troubleshooting

### ❌ Error: "Python tidak ditemukan"
**Solusi:**
1. Install Python dari https://www.python.org/downloads/
2. **PENTING**: Centang "Add Python to PATH" saat instalasi
3. Restart komputer
4. Jalankan ulang `1_install.bat`

---

### ❌ Error: "Chrome tidak ditemukan"
**Solusi:**
1. Install Google Chrome dari https://www.google.com/chrome/
2. Install di lokasi default (C:\Program Files\Google\Chrome\)
3. Jalankan ulang `2_buka_chrome.bat`

---

### ❌ Error: "Tidak menemukan tombol Edit"
**Solusi:**
1. Pastikan Chrome sudah login ke MATCHAPRO
2. Pastikan menu "Direktori Usaha" sudah terbuka
3. Pastikan kolom IDSBR/Nama di Excel terisi
4. Cek screenshot di `artifacts/screenshots/` untuk lihat apa yang terjadi

---

### ❌ Error: "Form sedang dikunci pengguna lain"
**Solusi:**
- Ini normal jika ada orang lain sedang edit data yang sama
- Script akan **skip** data tersebut dan lanjut ke data berikutnya
- Jalankan ulang nanti untuk data yang di-skip

---

### ❌ Chrome tidak bisa dibuka / Error CDP
**Solusi:**
1. Tutup semua jendela Chrome
2. Jalankan ulang `2_buka_chrome.bat`
3. Tunggu sampai Chrome terbuka
4. Login ke MATCHAPRO
5. Baru jalankan autofill

---

### ⚠️ Proses lambat / timeout
**Solusi:**
- Gunakan jeda lebih lama untuk koneksi lemot:
  ```cmd
  python sbr_fill.py --match-by idsbr --start 1 --end 10 --pause-after-edit 3000 --pause-after-submit 3000 --max-wait 10000
  ```
- Kurangi ukuran batch (edit `BATCH_SIZE` di `batch_runner.py`)

---

## ❓ FAQ (Pertanyaan Umum)

### 1. Apakah aman digunakan?
**Ya!** Software ini hanya mengisi form di MATCHAPRO seperti yang Anda lakukan manual. Tidak ada data yang dihapus atau diubah tanpa sepengetahuan Anda.

### 2. Apakah perlu koneksi internet?
**Ya**, karena software ini mengakses MATCHAPRO yang online.

### 3. Berapa lama proses untuk 100 data?
Tergantung koneksi internet, biasanya **5-10 menit** untuk 100 data.

### 4. Apakah bisa dijalankan di Mac/Linux?
**Bisa**, tapi file .bat hanya untuk Windows. Di Mac/Linux, gunakan terminal dan jalankan perintah Python langsung (lihat [Panduan Lanjutan](#-panduan-lanjutan)).

### 5. Apakah data Excel harus format tertentu?
**Ya**, harus format resmi Profiling SBR dari BPS dengan kolom standar (IDSBR, Nama Usaha, Status, Email, dll).

### 6. Bagaimana cara update software?
```cmd
git pull origin main
```
Atau download ulang dari repository.

### 7. Apakah log bisa dihapus?
**Ya**, log lama otomatis dihapus. Default menyimpan 10 hari terakhir. Bisa diubah dengan parameter `--keep-runs`.

### 8. Bagaimana cara kirim notifikasi ke grup WhatsApp?
Gunakan parameter `--whatsapp-group`:
```cmd
python sbr_fill.py --match-by idsbr --start 1 --end 50 --whatsapp-group "Tim SBR Bulungan"
```

### 9. Apakah bisa pause di tengah proses?
**Tidak direkomendasikan**. Tapi jika terpaksa, tekan `Ctrl+C` untuk stop, lalu jalankan ulang dengan `--resume`.

### 10. Bagaimana cara lihat hasil/log?
- Log CSV: `artifacts/logs/YYYY-MM-DD/log_sbr_autofill_*.csv`
- Log HTML: `artifacts/logs/YYYY-MM-DD/log_sbr_autofill_*.html`
- Screenshot: `artifacts/screenshots/YYYY-MM-DD/`

---

## 📚 Panduan Lanjutan

### Untuk Pengguna Terminal (Command Prompt/PowerShell)

Jika Anda familiar dengan terminal, bisa langsung jalankan perintah Python:

#### Instalasi Manual:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

#### Buka Chrome Manual:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
```

#### Jalankan Autofill Manual:
```cmd
.venv\Scripts\activate
python sbr_fill.py --match-by idsbr --start 1 --end 10 --stop-on-error
```

#### Parameter Lengkap:

| Parameter | Fungsi | Contoh |
|-----------|--------|--------|
| `--excel` | Pilih file Excel | `--excel "data/Profiling.xlsx"` |
| `--sheet` | Pilih sheet Excel | `--sheet 0` (sheet pertama) |
| `--match-by` | Metode pencocokan | `--match-by idsbr` atau `name` atau `index` |
| `--start` | Baris mulai | `--start 1` |
| `--end` | Baris akhir | `--end 100` |
| `--stop-on-error` | Stop jika error | (flag, tidak perlu nilai) |
| `--resume` | Lanjutkan dari yang gagal | (flag, tidak perlu nilai) |
| `--dry-run` | Test tanpa isi data | (flag, tidak perlu nilai) |
| `--pause-after-edit` | Jeda setelah klik Edit (ms) | `--pause-after-edit 2000` |
| `--pause-after-submit` | Jeda setelah submit (ms) | `--pause-after-submit 1500` |
| `--max-wait` | Timeout maksimal (ms) | `--max-wait 10000` |
| `--whatsapp-config` | Config WhatsApp | `--whatsapp-config config/whatsapp.json` |
| `--whatsapp-number` | Nomor WhatsApp | `--whatsapp-number "+6281234567890"` |
| `--whatsapp-group` | Grup WhatsApp | `--whatsapp-group "Tim SBR"` |

#### Contoh Perintah Lengkap:
```cmd
python sbr_fill.py --excel "data/Profiling.xlsx" --match-by idsbr --start 1 --end 50 --stop-on-error --resume --pause-after-edit 2000 --pause-after-submit 1500 --whatsapp-config config/whatsapp.json
```

---

### Konfigurasi Lanjutan

#### 1. Profile CLI
Simpan konfigurasi default di file JSON:

1. Copy: `config/profile.example.json` → `config/profile_saya.json`
2. Edit sesuai kebutuhan:
   ```json
   {
     "match_by": "idsbr",
     "stop_on_error": true,
     "pause_after_edit": 2000,
     "pause_after_submit": 1500,
     "max_wait": 8000
   }
   ```
3. Gunakan:
   ```cmd
   python sbr_fill.py --profile config/profile_saya.json --start 1 --end 50
   ```

#### 2. Custom Status Mapping
Jika MATCHAPRO menambah status baru:

1. Edit: `config/status_map.json`
2. Tambahkan mapping baru:
   ```json
   {
     "Status Baru": "radio_status_baru",
     "Aktif": "radio_aktif",
     ...
   }
   ```
3. Gunakan:
   ```cmd
   python sbr_fill.py --status-map config/status_map.json --start 1 --end 10
   ```

---

### Struktur File Excel

**Kolom Wajib:**
- `idsbr` atau `idsbr_master` (untuk match-by idsbr)
- `nama` atau `nama_usaha` atau `nama_usaha_pembetulan` (untuk match-by name)
- `status` atau `keberadaan_usaha`
- `email`
- `sumber` atau `sumber_profiling`
- `catatan` atau `catatan_profiling`

**Kolom Opsional (akan diisi jika ada):**
- `nama_usaha_pembetulan`
- `nama_komersial_usaha`
- `alamat_pembetulan`
- `nama_sls`
- `kodepos`
- `nomor_telepon` / `nomor_whatsapp`
- `website`
- `kdprov_pindah`, `kdkab_pindah`
- `kdprov`, `kdkab`, `kdkec`, `kddesa`
- `jenis_kepemilikan_usaha`
- `bentuk_badan_hukum_usaha`
- `latitude`, `longitude`

**Khusus Status Duplikat:**
- Isi kolom `idsbr_master` dengan kode master
- Script akan otomatis klik tombol "Check" dan "Accept"

---

### Testing

Jalankan test untuk memastikan semua berfungsi:

```cmd
.venv\Scripts\activate
pytest
```

Linting dengan Ruff:
```cmd
ruff check .
```

---

## 📁 Struktur Folder Detail

```
fix-otomatisasi-sbr/
├── 1_install.bat              # Instalasi otomatis
├── 2_buka_chrome.bat          # Buka Chrome dengan debugging
├── 3_jalankan_autofill.bat    # Autofill interaktif
├── 4_batch_runner.bat         # Batch processing
├── 5_cancel_submit.bat        # Cancel submit
│
├── sbr_fill.py                # Script autofill (Python)
├── sbr_cancel.py              # Script cancel (Python)
├── batch_runner.py            # Script batch runner (Python)
│
├── data/                      # Letakkan Excel di sini
│   └── Profiling.xlsx
│
├── config/                    # File konfigurasi
│   ├── profile.example.json
│   ├── status_map.json
│   ├── whatsapp.example.json
│   └── whatsapp.json
│
├── artifacts/                 # Hasil output
│   ├── logs/                  # Log CSV & HTML
│   │   ├── 2025-01-07/
│   │   ├── batch_runner/
│   │   └── index.csv
│   ├── screenshots/           # Screenshot autofill
│   └── screenshots_cancel/    # Screenshot cancel
│
├── sbr_automation/            # Modul Python (jangan diubah)
│   ├── __init__.py
│   ├── autofill.py
│   ├── config.py
│   ├── form_filler.py
│   ├── loader.py
│   ├── logbook.py
│   ├── navigator.py
│   ├── playwright_helpers.py
│   ├── resume.py
│   ├── submitter.py
│   ├── table_actions.py
│   ├── utils.py
│   ├── whatsapp_notifier.py
│   └── ...
│
├── tests/                     # Unit tests
│   ├── test_loader.py
│   ├── test_resume.py
│   └── test_utils.py
│
├── requirements.txt           # Dependencies Python
├── pyproject.toml            # Project config
├── .gitignore                # Git ignore
│
├── README.md                 # Panduan ini
├── CHANGELOG.md              # Riwayat perubahan
├── WHATSAPP_SETUP.md         # Panduan WhatsApp
└── UPDATE_SUMMARY.md         # Ringkasan update
```

---

## 📞 Bantuan & Dukungan

**Jika mengalami masalah:**

1. **Cek Troubleshooting** di atas
2. **Lihat log error** di `artifacts/logs/`
3. **Lihat screenshot** di `artifacts/screenshots/`
4. **Hubungi tim IPDS** BPS Kabupaten Bulungan

**Dokumentasi Tambahan:**
- [CHANGELOG.md](CHANGELOG.md) - Riwayat perubahan versi
- [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Setup WhatsApp lengkap
- [UPDATE_SUMMARY.md](UPDATE_SUMMARY.md) - Ringkasan update terbaru

---

## 🎉 Selamat Menggunakan!

Software ini dibuat untuk **memudahkan pekerjaan Anda**. Jika ada saran atau masukan, silakan hubungi tim pengembang.

**Kredit:**
- Pengembang Awal: Yuneko/Uul - BPS Kabupaten Buru Selatan
- Pengembang Lanjutan: Tim IPDS BPS Kabupaten Bulungan

---

**Versi:** 2.0  
**Terakhir Diperbarui:** Januari 2026

---

## 📝 Catatan Penting

⚠️ **PERHATIAN:**
- Pastikan Chrome **TIDAK DITUTUP** saat proses berjalan
- Jangan edit data di MATCHAPRO secara manual saat autofill berjalan
- Backup file Excel sebelum memproses
- Cek hasil di log setelah proses selesai

✅ **TIPS:**
- Mulai dengan data kecil (10-20 baris) untuk testing
- Gunakan `--dry-run` untuk test tanpa mengubah data
- Aktifkan `--stop-on-error` untuk debugging
- Gunakan Batch Runner untuk data besar (>100 baris)
- Setup WhatsApp untuk monitoring jarak jauh

---

**Happy Automating! 🚀**
