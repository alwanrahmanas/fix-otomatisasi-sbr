# Otomatisasi Profiling SBR

Software CLI berbasis Playwright untuk membantu pengisian Profiling SBR di MATCHAPRO secara otomatis sekaligus mencatatkan log monitoring. Proyek ini dikembangkan dari inovasi [https://github.com/yuneko11/OtomatisasiSBR.git](https://github.com/yuneko11/OtomatisasiSBR.git) (Yuneko/Uul - BPS Kabupaten Buru Selatan).

## Ringkasan Fitur

- Autofill Profiling SBR langsung dari Excel, termasuk kolom Profiling terbaru (identitas usaha, wilayah pindah, pemilik/badan usaha, sumber & catatan).
- Membuka form dan menekan tombol _Cancel Submit_ secara otomatis.
- Resume/dry-run, auto-scan Excel, deteksi header bertingkat, serta pemetaan status dengan alias/angka.
- Log CSV, laporan HTML, screenshot per run, dan indeks riwayat run yang dipangkas otomatis.
- Profil CLI, pemetaan status kustom, dan pembatasan jumlah arsip run.
- **🆕 Notifikasi WhatsApp otomatis** dengan ringkasan hasil autofill (sukses, error, durasi) dan range baris.
- **🆕 Configurable Defaults**: Pengisian otomatis untuk field kosong (Alamat, Sumber, Catatan) dengan nilai default yang dapat dikonfigurasi.

## Daftar Isi

- [Prasyarat](#prasyarat)
- [Catatan Terminal](#catatan-terminal)
- [Quickstart](#quickstart)
- [Instalasi (Detail)](#instalasi-detail)
- [Menyiapkan Data Profiling](#menyiapkan-data-profiling)
- [Menjalankan Autofill](#menjalankan-autofill)
- [Menjalankan Cancel Submit](#menjalankan-cancel-submit)
- [**🆕 WhatsApp Notification**](#whatsapp-notification)
- [**🔄 Batch Runner**](#batch-runner)
- [Struktur Proyek](#struktur-proyek)
- [Profil CLI](#profil-cli)
- [Pemetaan Status](#pemetaan-status)
- [Output dan Log](#output-dan-log)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Kredit](#kredit)

---

## Prasyarat

- Python 3.10 atau lebih baru.
- Google Chrome terpasang di lokasi default (atau sesuaikan path ketika menyalakan remote debugging).
- Akses ke MATCHAPRO dan berkas Excel Profiling SBR resmi.

---

## Catatan Terminal

- Semua contoh perintah di README menggunakan PowerShell. Jika Anda lebih nyaman dengan Command Prompt atau Git Bash/WSL, pilih salah satu dan sesuaikan perintah berikut.
- **Command Prompt (cmd.exe):** aktivasi venv dengan `.venv\Scripts\activate.bat`; perintah `python ...` sama; jalankan Chrome dengan `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"` (tanpa prefix `&`).
- **Git Bash/WSL/Linux/macOS:** aktivasi venv dengan `source .venv/bin/activate`; gunakan `python3 ...`; jalankan Chrome dengan `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-sbr` atau sesuaikan lokasi binary dan profil.
- Pada PowerShell, gunakan prefix `&` jika path berisi spasi (contoh Chrome). Di shell lain tidak diperlukan.

---

## Quickstart

Untuk langsung jalan (contoh PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
python sbr_fill.py --match-by idsbr --start 1 --end 5
```

- Command Prompt: gunakan `.venv\Scripts\activate.bat` dan hilangkan prefix `&` saat memanggil Chrome.
- Git Bash/WSL/Linux/macOS: gunakan `source .venv/bin/activate`, `python3`, dan perintah `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-sbr` atau sesuaikan path.
- Pastikan Excel Profiling resmi sudah ada di folder kerja (bisa di `data/`).

---

## Instalasi (Detail)

1. Clone repositori ini dan masuk ke foldernya:

   ```powershell
   git clone https://github.com/bpskabbulungan/otomatisasisbr-6502.git
   cd otomatisasisbr-6502
   ```

2. Buka PowerShell/terminal di folder proyek, lalu buat dan aktifkan virtual environment. Setelah aktif, instal dependensi runtime:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   playwright install chromium
   ```

   - Command Prompt: aktifkan venv dengan `.venv\Scripts\activate.bat`. Git Bash/WSL/Linux/macOS: `source .venv/bin/activate` dan `python3` bila diperlukan.
   - Jika perintah `python` mengarah ke versi lain, gunakan `py -3` atau `python3`.
   - `requirements.txt` berisi semua dependencies: `pandas`, `openpyxl`, `playwright`, `selenium`, `pyperclip`
   - `playwright install chromium` cukup dijalankan sekali untuk mengunduh browser otomatis.

3. Jalankan Chrome dengan mode remote debugging (dibutuhkan agar Playwright menempel ke sesi MATCHAPRO yang sudah login):

   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
   ```

   - Gunakan profil Chrome khusus agar loginnya terpisah dari Chrome harian.
   - Setelah Chrome terbuka, login ke [https://matchapro.web.bps.go.id/](https://matchapro.web.bps.go.id/) dan buka menu **Direktori Usaha**.
   - Saat skrip dijalankan, koneksi CDP (Chrome DevTools Protocol) diperiksa otomatis. Jika belum siap, pesan error menampilkan ulang perintah di atas.
   - Command Prompt: hilangkan prefix `&`. Git Bash/WSL/Linux/macOS: gunakan path binary Chrome/Chromium yang sesuai (lihat Catatan Terminal).
4. Simpan Excel Profiling (format resmi BPS) ke folder proyek, misalnya `data/Daftar Profiling.xlsx`.

---

## Menyiapkan Data Profiling

- Gunakan Excel Profiling resmi. Nama kolom akan dibersihkan (lowercase, spasi menjadi `_`); jika header bertingkat, skrip otomatis mencoba baris kedua.
- Kolom wajib untuk autofill: `status/keberadaan_usaha`, `email`, `sumber/sumber_profiling`, `catatan/catatan_profiling`, serta kolom pencocokan sesuai `--match-by` (`idsbr/idsbr_master` atau `nama/nama_usaha/nama_usaha_pembetulan`).
- Kolom Profiling yang akan diisi (kolom harus ada, nilai kosong akan dilewati): `nama_usaha_pembetulan`, `nama_komersial_usaha`, `alamat_pembetulan`, `nama_sls`, `kodepos`, `nomor_telepon`, `nomor_whatsapp`, `website`, `idsbr_master`, `kdprov_pindah`, `kdkab_pindah`, `kdprov`, `kdkab`, `kdkec`, `kddesa`, `jenis_kepemilikan_usaha`, `bentuk_badan_hukum_usaha`, `sumber_profiling`, `catatan_profiling`, `latitude`, `longitude`.
- Khusus status **Duplikat**, isi `idsbr_master` (kode master) di Excel; skrip akan otomatis menekan tombol **Check** dan **Accept** setelah mengisi field tersebut.
- Nilai status boleh berupa teks atau angka 1-11; pemetaan default mengikuti form MATCHAPRO (mis. 1=Aktif, 3=Belum Beroperasi/Berproduksi, 8=Aktif Nonrespon).
- Kolom nomor telepon otomatis dibaca dari beberapa alias (`nomor_telepon`, `nomor_whatsapp`, `no telp`, `phone`, dll).
- Simpan hanya satu berkas `.xlsx` di folder kerja atau `data/`; tanpa `--excel`, skrip memilih berkas tunggal tersebut otomatis (jika lebih dari satu akan diminta memilih via argumen).

---

## Menjalankan Autofill

Perintah contoh menggunakan PowerShell; sesuaikan ke Command Prompt atau Git Bash/WSL sesuai Catatan Terminal.

Contoh dasar:

```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 10
```

Contoh lebih lengkap (biasa dipakai):

```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 5 --pause-after-edit 1500 --pause-after-submit 1500 --stop-on-error
```

Penjelasan singkat:

- `--match-by idsbr` mencocokkan baris tabel berdasar kolom `idsbr/idsbr_master` di Excel.
- `--start 1 --end 5` memproses baris ke-1 s.d. 5 (inklusif) pada sheet terpilih.
- `--pause-after-edit 1500` menunggu 1.5 detik setelah klik Edit sebelum membaca/tab form.
- `--pause-after-submit 1500` menunggu 1.5 detik setelah klik Submit Final sebelum lanjut.
- `--stop-on-error` menghentikan run saat error pertama agar mudah diperbaiki sebelum melanjutkan.

Contoh jeda lebih aman (untuk jaringan yang lemot/latensi tinggi):

```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 5 --pause-after-edit 3000 --pause-after-submit 3000 --step-delay 800 --max-wait 10000 --stop-on-error
```

Penjelasan singkat:

- `--pause-after-edit 3000` memberi waktu 3 detik agar tab form benar-benar terbuka.
- `--pause-after-submit 3000` menunggu 3 detik setelah klik Submit Final sebelum lanjut.
- `--step-delay 800` menambah jeda slow mode antaraksi kecil (klik/ketik).
- `--max-wait 10000` memperpanjang timeout elemen/tab jadi 10 detik.

Daftar opsi bisa digunakan:

| Opsi                                    | Fungsi                                                                                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--profile config\profile.json`         | Memuat nilai default argumen dari file JSON (lihat [Profil CLI](#profil-cli)).                                                                          |
| `--excel "C:\path\file.xlsx"`         | Memilih Excel tertentu. Jika absen, skrip mencari satu-satunya `.xlsx` di folder kerja atau `data/`.                                                |
| `--sheet 1`                           | Memilih sheet Excel ke- (`0` = sheet pertama).                                                                                                        |
| `--cdp-endpoint`                      | Endpoint Chrome CDP (default [http://localhost:9222](http://localhost:9222)); ubah bila port atau host berbeda dari default.                                |
| `--match-by idsbr`                    | Cara menemukan tombol **Edit** (`idsbr`, `name`, atau indeks tabel `index`).                                                                 |
| `--start` / `--end`                 | Menentukan rentang baris yang diproses.                                                                                                                 |
| `--stop-on-error`                     | Menghentikan proses pada error pertama. Tanpa opsi ini, skrip lanjut ke baris berikutnya.                                                               |
| `--no-slow-mode`                      | Menghapus jeda antaraksi (gunakan setelah alur dipastikan stabil).                                                                                      |
| `--step-delay 500`                    | Mengatur lama jeda slow mode (ms).                                                                                                                      |
| `--pause-after-edit 1200`             | Waktu tunggu setelah klik Edit sebelum memproses tab form (ms).                                                                                         |
| `--pause-after-submit 500`            | Waktu tunggu setelah klik Submit Final (ms).                                                                                                            |
| `--max-wait 8000`                     | Timeout tunggu elemen/tab (ms) untuk interaksi tabel dan form.                                                                                          |
| `--skip-status`                       | Melewati pengisian kolom status di MATCHAPRO (berguna saat hanya memperbarui sumber atau catatan).                                                      |
| `--resume`                            | Melewati baris yang sudah berstatus**OK** pada log terakhir (skrip mencari `log_sbr_autofill_*.csv` terbaru di folder harian atau log default). |
| `--dry-run`                           | Verifikasi tombol Edit tanpa membuka form atau mengubah data MATCHAPRO.                                                                                 |
| `--status-map config\status_map.json` | Pemetaan status kustom (lihat[Pemetaan Status](#pemetaan-status)).                                                                                         |
| `--selectors config\selectors.json`   | Kustom selector field Profiling (bagian `fields` untuk input biasa, `select2` untuk dropdown Select2).                                              |
| `--run-id Sesi01`                     | Menamai label file log secara manual (huruf, angka, strip, atau garis bawah).                                                                           |
| `--keep-runs 7`                       | Membatasi jumlah folder harian yang disimpan sebelum dibersihkan otomatis.                                                                              |

Catatan parameter:

- `--match-by idsbr` memakai kolom `idsbr/idsbr_master`; `--match-by name` memakai `nama/nama_usaha/nama_usaha_pembetulan`; mode `index` tidak perlu kolom tambahan.
- Tanpa `--skip-status`, nilai kolom `status/keberadaan_usaha` di Excel dianggap sumber kebenaran dan dapat menimpa status di MATCHAPRO.
- `--resume` membaca log terakhir (berdasarkan waktu modifikasi). Jika log untuk label sekarang belum ada, skrip mencari `log_sbr_autofill_*.csv` terbaru di folder harian sebelum melewati baris berstatus OK.
- `--dry-run` hanya menghasilkan log tahap `DRY_RUN`; data di MATCHAPRO tidak disentuh.
- `--selectors` berguna jika layout MATCHAPRO berubah; isi file JSON dengan struktur `{ "fields": { "nama_sls": "input#nama_sls_baru" }, "select2": { "kdkab": "#select-kabupaten" } }`.
- Jika `--status-map` tidak diberikan, skrip memakai bawaan internal (setara dengan `config/status_map.json`); file kustom digabungkan sehingga entri dapat ditambah atau ditimpa.
- `--run-id` memudahkan memberi label run; jika nama bentrok, sufiks angka otomatis ditambahkan.
- Semua run dicatat di `artifacts/logs/index.csv`.

---

## Pengujian

Jalankan uji unit dasar (normalisasi utilitas dan resume log) dengan:

```powershell
pytest
```

Pastikan dependensi `pytest` sudah terpasang di lingkungan virtual.

Linting cepat dengan Ruff:

```powershell
ruff check .
```

---

## Menjalankan Cancel Submit

Perintah contoh menggunakan PowerShell; sesuaikan ke Command Prompt atau Git Bash/WSL sesuai Catatan Terminal.

Contoh perintah:

```powershell
python sbr_cancel.py --match-by name --start 1 --end 20
```

- Aksi yang dijalankan sama seperti autofill, tetapi tombol akhir adalah _Cancel Submit_.
- Log CSV dan laporan HTML tersimpan di folder harian, misalnya `artifacts/logs/2025-11-25/log_sbr_cancel_<label>.csv`.
- Screenshot hasil berada di `artifacts/screenshots_cancel/2025-11-25/` dengan nama file bertimestamp.
- Riwayat ringkas run tersimpan di `artifacts/logs/index.csv`.
- Pastikan Excel memuat kolom sesuai pilihan `--match-by` (`idsbr/idsbr_master` atau `nama/nama_usaha/nama_usaha_pembetulan`; mode `index` tidak butuh kolom tambahan).
- Opsi yang sering dipakai untuk cancel: `--profile`, `--excel`, `--sheet`, `--match-by`, `--start`/`--end`, `--stop-on-error`, `--cdp-endpoint`, `--pause-after-edit`, `--max-wait`, `--run-id`, `--keep-runs`.

---

## 🆕 WhatsApp Notification

Fitur notifikasi WhatsApp otomatis mengirimkan ringkasan hasil autofill setelah proses selesai. Notifikasi mencakup jumlah sukses/error, detail error, durasi eksekusi, dan link ke log file.

### Setup Cepat

1. **Install dependencies (jika belum):**
   ```powershell
   pip install -r requirements.txt
   ```
   
   Dependencies yang dibutuhkan: `selenium`, `pyperclip` (sudah termasuk di requirements.txt)

2. **Buat konfigurasi WhatsApp:**
   ```powershell
   copy config\whatsapp.example.json config\whatsapp.json
   ```

3. **Edit `config\whatsapp.json`:**
   ```json
   {
     "enabled": true,
     "phone_number": "+6281234567890",
     "chrome_profile_path": "C:\\ChromeProfileSBR"
   }
   ```

4. **Jalankan autofill dengan notifikasi:**
   ```powershell
   python sbr_fill.py --match-by idsbr --start 1 --end 10 --whatsapp-config config\whatsapp.json
   ```

5. **Scan QR code** (hanya pertama kali) saat browser Chrome terbuka ke WhatsApp Web.

### Opsi Penggunaan

**Menggunakan config file:**
```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 50 --whatsapp-config config\whatsapp.json
```

**Override nomor via CLI:**
```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 50 --whatsapp-number "+6281234567890"
```

**Kirim ke grup WhatsApp:**
```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 50 --whatsapp-group "Tim SBR Bulungan"
```

### Fitur Notifikasi

- ✅ **Auto-send** setelah autofill selesai
- 📊 **Ringkasan lengkap**: OK, WARNING, ERROR counts
- 🔴 **Top 5 errors** dengan detail IDSBR dan nama usaha
- ⏱️ **Durasi eksekusi** otomatis dihitung
- 🔒 **Auto-close browser** setelah pesan terkirim (memory efficient)
- 📱 **Support personal & grup** WhatsApp
- 🎨 **Custom message template** via config file
- 🎯 **Conditional notification** (hanya kirim jika error >= threshold)

### Dokumentasi Lengkap

Lihat [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) untuk:
- Setup langkah demi langkah
- Troubleshooting
- Advanced configuration
- Custom message templates
- FAQ

---

## 🔄 Batch Runner

Untuk memproses data dalam jumlah besar, gunakan **`batch_runner.py`** yang akan membagi data menjadi batch-batch kecil dan memproses secara berurutan.

### Fitur Batch Runner

- ✅ **Auto-split data** menjadi batch berukuran tetap (default 30 baris)
- ✅ **Smart continuation** - Lanjut dari baris terakhir yang diproses (bukan +30)
- ✅ **Auto-resume mode** - Skip baris yang sudah OK, retry yang gagal
- ✅ **Comprehensive logging** - Semua output disimpan ke file log
- ✅ **Real-time monitoring** - Lihat progress setiap batch di console
- ✅ **Batch statistics** - Ringkasan detail per batch (sukses, error, dilewati)
- ✅ **Warning detection** - Peringatan otomatis jika batch tidak sesuai ekspektasi
- ✅ **Overall summary** - Ringkasan keseluruhan setelah semua batch selesai
- ✅ **Persistent logs** - Log tersimpan di `artifacts/logs/batch_runner/`
- ✅ **Auto-continue** - Lanjut ke batch berikutnya meski ada error
- ✅ **Configurable** - Mudah disesuaikan (batch size, start row, dll)

### Konfigurasi

Edit `batch_runner.py` untuk menyesuaikan:

```python
DATA_DIR = Path("data")              # Folder Excel
BATCH_SIZE = 30                      # Ukuran batch (baris per batch)
START_FROM = 30                      # Mulai dari baris ke-
WHATSAPP_CONFIG = "config/whatsapp.json"
```

### Cara Menggunakan

```powershell
# Jalankan batch runner
python batch_runner.py
```

Script akan:
1. Mencari file Excel di folder `data/`
2. Menghitung total baris data
3. Membagi menjadi batch berukuran `BATCH_SIZE`
4. Menjalankan `sbr_fill.py` untuk setiap batch dengan `--resume` aktif
5. Menampilkan ringkasan detail per batch
6. Menyimpan log lengkap ke file

### Cara Kerja Auto-Resume

Batch runner menggunakan `--resume` mode secara otomatis untuk menghindari duplikasi:

**Skenario: Batch #1 ada yang gagal**
```
Batch #1: Baris 151-180 (30 baris)
  ✅ Sukses: 29 baris (152-180)
  ❌ Error: 1 baris (151)

Batch #2: Baris 181-210 (30 baris)
  → Baris 152-180: SKIP (sudah OK di log)
  → Baris 151: RETRY (masih ERROR)
  → Baris 181-210: PROSES
```

**Keuntungan:**
- ✅ Baris yang gagal akan **dikerjakan ulang** otomatis
- ✅ Baris yang sudah sukses **tidak diproses ulang** (efisien)
- ✅ Tidak ada data yang terlewat
- ✅ Tidak ada duplikasi data

**Smart Continuation Logic:**
- Jika semua baris diproses → lanjut ke batch berikutnya
- Jika ada yang gagal → lanjut ke batch berikutnya (resume akan handle retry)
- Jika tidak ada yang diproses → retry batch yang sama (max 1x retry)


### Output Batch Runner

**Console Output:**
```
📝 Log batch runner: artifacts/logs/batch_runner/batch_run_2025-12-30_15-17-00.log
⏰ Waktu mulai: 2025-12-30 15:17:00
✅ Total data ditemukan: 150 baris
🚀 Memulai batch process dari baris 30 dengan ukuran 30...

======================================================================
▶️  BATCH #1: Baris 30 sampai 59 (Total: 30 baris)
======================================================================

📋 Output dari sbr_fill.py:
----------------------------------------------------------------------
  Memeriksa koneksi Chrome (CDP)...
  Chrome CDP siap digunakan.
  Baris 30: PT MAJU JAYA
  ...
----------------------------------------------------------------------

📊 RINGKASAN BATCH #1:
  ⏱️  Durasi        : 45.32 detik
  📝 Diharapkan    : 30 baris
  ✅ Diproses      : 30 baris
  🎯 Sukses        : 28 baris
  ❌ Error         : 2 baris
  ⏭️  Dilewati      : 0 baris
  🔢 Return code   : 0

⏳ Istirahat 5 detik sebelum batch berikutnya...
```

**Warning Detection:**
```
⚠️  PERINGATAN: Hanya 1 dari 30 baris yang diproses!
   Kemungkinan penyebab:
   - Error yang menghentikan proses lebih awal
   - Data Excel tidak sesuai ekspektasi
   - Resume mode melewati baris tertentu
   - Periksa log detail di atas untuk informasi lebih lanjut
```

**Final Summary:**
```
======================================================================
🎉 SEMUA BATCH SELESAI!
======================================================================

📊 RINGKASAN KESELURUHAN:
  📦 Total batch dijalankan : 5
  ✅ Batch sukses          : 4
  ❌ Batch gagal           : 1
  🎯 Total baris sukses    : 120
  ❌ Total baris error     : 15
  ⏭️  Total baris dilewati  : 10
  📝 Log lengkap tersimpan : artifacts/logs/batch_runner/batch_run_2025-12-30_15-17-00.log
  ⏰ Waktu selesai         : 2025-12-30 16:05:23
```

### Log File

Semua output disimpan ke file log di `artifacts/logs/batch_runner/batch_run_TIMESTAMP.log` yang berisi:
- Konfigurasi batch (size, start, total data)
- Output lengkap dari setiap `sbr_fill.py` execution
- Ringkasan statistik per batch
- Peringatan jika ada anomali
- Ringkasan keseluruhan

### Troubleshooting Batch Runner

**Batch hanya memproses 1 baris:**
- Periksa log file untuk melihat output detail dari `sbr_fill.py`
- Kemungkinan ada error yang menghentikan proses
- Cek apakah data Excel sesuai ekspektasi
- Pastikan tidak ada resume mode yang melewati baris

**Batch gagal semua:**
- Pastikan Chrome CDP sudah running
- Cek koneksi ke MATCHAPRO
- Periksa file Excel ada di folder `data/`
- Lihat error detail di log file

**Ingin mengubah ukuran batch:**
- Edit `BATCH_SIZE` di `batch_runner.py`
- Batch lebih kecil = lebih aman tapi lebih lama
- Batch lebih besar = lebih cepat tapi risiko error lebih tinggi

---

## Struktur Proyek

```text
.
|-- artifacts/              # Arsip log dan screenshot per run
|   |-- logs/
|   |   |-- batch_runner/   # Log dari batch_runner.py
|   |   `-- YYYY-MM-DD/     # Log harian dari sbr_fill.py & sbr_cancel.py
|   |-- screenshots/
|   `-- screenshots_cancel/
|-- data/                   # Tempat menyimpan Excel Profiling (opsional)
|-- config/                 # Profil CLI dan pemetaan status
|-- sbr_automation/         # Modul Python otomatisasi (lihat rincian di bawah)
|-- sbr_fill.py             # Perintah autofill
|-- sbr_cancel.py           # Perintah cancel submit
`-- batch_runner.py         # 🆕 Batch processing dengan logging komprehensif
```

- `sbr_fill.py` mengisi form Profiling sesuai Excel.
- `sbr_cancel.py` membuka form dan menekan tombol _Cancel Submit_.
- `batch_runner.py` memproses data dalam batch dengan logging detail.
- Semua log dan screenshot otomatis tersimpan di `artifacts/`.

### Rincian folder `sbr_automation/`

- `config.py`: pengaturan runtime (timeout, jeda slow mode, folder output), pemetaan status default, dan util untuk membuat folder run/log.
- `loader.py`: baca & validasi Excel, normalisasi status/telepon, membentuk `RowContext` untuk setiap baris yang akan diproses.
- `navigator.py`: logika membuka tab form setelah klik Edit, termasuk fallback pencarian href.
- `table_actions.py`: helper interaksi tabel (filter, klik Edit by index/teks) dengan retry.
- `form_filler.py`: isi field form (status, identitas, select2, IDSBR master) dengan selector yang dapat dikonfigurasi.
- `submitter.py`: menangani tombol Submit Final/konfirmasi, deteksi form final/terkunci, dengan reason code.
- `resume.py`: baca log sebelumnya untuk mode resume dan mencari log terbaru.
- `playwright_helpers.py`: util dasar Playwright (attach ke Chrome CDP, slow pause, hilangkan overlay).
- `logbook.py`: pencatatan log CSV/HTML dan indeks run.
- `field_selectors.py`: default selector field + loader JSON override.
- `utils.py`: fungsi umum (normalisasi, screenshot, retry `with_retry`).
- `models.py`: definisi dataclass `RowContext` dan `SubmitResult`.

---

## Profil CLI

1. Salin `config/profile.example.json` menjadi profil baru, misalnya `config/profile_autofill.json`.
2. Isi nilai default sesuai kebutuhan menggunakan nama argumen CLI. Autofill mendukung kunci seperti `excel`, `sheet`, `match_by`, `start`, `end`, `stop_on_error`, `cdp_endpoint`, `no_slow_mode`, `step_delay`, `pause_after_edit`, `pause_after_submit`, `max_wait`, `resume`, `dry_run`, `skip_status`, `status_map`, `run_id`, `keep_runs`. Untuk cancel gunakan kunci yang relevan (`excel`, `sheet`, `match_by`, `start`, `end`, `stop_on_error`, `cdp_endpoint`, `pause_after_edit`, `max_wait`, `run_id`, `keep_runs`).
3. Jalankan skrip dengan `--profile config/profile_autofill.json`. Argumen di baris perintah tetap menimpa nilai dari profil.

---

## Pemetaan Status

1. Gunakan atau salin `config/status_map.json` sesuai kebutuhan (isi default sama dengan pemetaan bawaan di skrip).
2. Sesuaikan pasangan `Nama Status` -> `id radio` mengikuti tampilan terbaru MATCHAPRO.
3. Jalankan autofill dengan menambahkan `--status-map "config/status_map.json"`.

Jika MATCHAPRO menambahkan status baru, tambahkan entri baru tanpa menghapus yang sudah ada.

---

## Output dan Log

- Folder arsip per hari: `artifacts/logs/YYYY-MM-DD/`, `artifacts/screenshots/YYYY-MM-DD/`, `artifacts/screenshots_cancel/YYYY-MM-DD/`.
- Setiap run memiliki label unik (default `HH-MM-SS` atau nilai `--run-id` yang disanitasi). Nama file log mengikuti label tersebut, misalnya:
  - `artifacts/logs/2025-11-25/log_sbr_autofill_09-30-12.csv`
  - `artifacts/logs/2025-11-25/log_sbr_autofill_09-30-12.html`
  - `artifacts/logs/2025-11-25/log_sbr_cancel_09-45-01.csv`
  - `artifacts/logs/2025-11-25/log_sbr_cancel_09-45-01.html`
- Screenshot dari semua run di hari itu berada di folder hari yang sama; nama file screenshot sudah mengandung timestamp sehingga tidak menimpa.
- Kolom CSV memuat konteks baris (`idsbr`, `nama`, `match_value`), sehingga mudah memfilter lokasi error.
- `artifacts/logs/index.csv` mencatat riwayat run (run_id/label, waktu mulai, ringkasan OK/WARN/ERROR).
- `--keep-runs` kini membatasi jumlah folder harian yang disimpan (default 10 hari).

Selama proses berjalan, terminal menampilkan informasi:

- filter yang sedang diterapkan di tabel MATCHAPRO,
- status loading tabel,
- informasi jika baris dilewati karena form sedang dibuka pengguna lain.

---

## Troubleshooting

1. **Tidak menemukan tombol Edit.** Pastikan kolom untuk `--match-by` terisi dan cek screenshot di `artifacts/screenshots/...` apakah tabel masih memuat data.
2. **Form "Profiling Info" sedang dikunci pengguna lain.** Skrip akan mencatat event `WARN` dan lanjut ke baris berikutnya. Jalankan ulang setelah form bisa dibuka.
3. **Skrip tidak menemukan tab MATCHAPRO.** Chrome harus dibuka melalui perintah remote debugging dan tab **Direktori Usaha** aktif sebelum skrip dijalankan.
4. **Perlu mengubah kecepatan atau jeda.**
   Ubah konfigurasi di `sbr_automation/config.py` (jeda klik, timeout, dan lokasi output).

---

## FAQ

- **Apakah log tetap dicatat tanpa `--stop-on-error`?** Ya, semua kesalahan (misalnya `CLICK_EDIT`, `FILL`, `SUBMIT`) tetap masuk CSV dan ringkasan akhir.
- **Bagaimana melanjutkan dari baris tertentu setelah error?** Jalankan ulang dengan `--start <baris berikutnya>`; baris yang sudah sukses tidak disentuh.
- **Bisakah menjalankan di akun Chrome berbeda?** Gunakan opsi `--user-data-dir=` pada perintah Chrome untuk profil terpisah.

---

## Kredit

Semoga panduan ini membantu. Jika menemukan pesan baru di log atau screenshot yang belum terbahas, hubungi tim IPDS BPS Kabupaten Bulungan.
