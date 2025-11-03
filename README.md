## Otomatisasi Profiling SBR

Perangkat CLI berbasis Playwright untuk membantu pengisian MATCHAPRO (autofill) atau membatalkan submit data Profiling SBR secara aman dan disertai log untuk monitoring.

Otomisasi ini dikembangkan dari Inovasi https://github.com/yuneko11/OtomatisasiSBR.git milik Yuneko (Uul) dari BPS Kabupaten Buru Selatan.

---

### 1. Struktur Folder 

```
.
|-- artifacts/              # Hasil menjalankan skrip (log & screenshot)
|   |-- logs/
|   |-- screenshots/
|   `-- screenshots_cancel/
|-- data/                   # Tempat menyimpan data Excel (opsional/bisa di tempat lain)
|-- sbr_automation/         # Modul Python untuk otomatisasi
|-- sbr_fill.py             # Perintah autofill
`-- sbr_cancel.py           # Perintah cancel submit
```

- **`sbr_fill.py`** → mengisi form Profiling sesuai Excel.
- **`sbr_cancel.py`** → membuka form dan menekan tombol *Cancel Submit*.
- Semua log dan screenshot otomatis tersimpan di folder `artifacts/`.

---

### 2. Installasi/Persiapan

1. **Install Python 3.10+** dan buka PowerShell.
2. Di folder proyek ini jalankan:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install pandas playwright
   playwright install chromium
   ```
3. **Jalankan Chrome dengan remote debugging** (wajib agar Playwright bisa menempel ke tab yang sudah login MATCHAPRO):

   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfileSBR"
   ```

   - Gunakan profil khusus supaya login tidak bentrok dengan Chrome lain.
   - Setelah Chrome terbuka, login ke https://matchapro.web.bps.go.id/ dan buka menu **Direktori Usaha**.
4. Siapkan file Excel Profiling (format resmi BPS). Simpan di dalam folder proyek (mis. `data/Daftar Profiling.xlsx`).

---

### 3. Memahami pilihan baris (`--start` & `--end`)

Skrip membaca Excel seperti daftar antrean. Dua opsi ini menentukan bagian mana yang diproses.

| Contoh Perintah        | Arti praktis                                                                   |
| ---------------------- | ------------------------------------------------------------------------------ |
| `--start 1 --end 10` | Proses baris 1 sampai 10 (inklusif). Baris ke-1 adalah baris pertama di Excel. |
| `--start 21`         | Proses mulai baris 21 sampai akhir file.                                       |
| `--end 5`            | Proses baris 1 sampai 5 saja.                                                  |

Tips: setelah batch pertama sukses, lanjutkan dengan `--start` baris berikutnya sehingga tidak mengulang entri yang sudah OK.

---

### 4. Menjalankan autofill

```powershell
python sbr_fill.py --match-by idsbr --start 1 --end 10 
```

Parameter yang sering dipakai:

| Opsi                            | Fungsi                                                                                                         |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `--excel "C:\path\file.xlsx"` | Memilih file Excel tertentu. Jika kosong, skrip mencari satu-satunya `.xlsx` di folder kerja atau `data/`. |
| `--match-by idsbr`            | Cara mencari tombol**Edit** di tabel: `idsbr`, `name`, atau berdasarkan indeks tabel (`index`).    |
| `--start` / `--end`         | Menentukan rentang baris (lihat tabel di atas).                                                                |
| `--stop-on-error`             | Hentikan proses di error pertama. Tanpa opsi ini skrip lanjut ke baris berikutnya.                             |
| `--no-slow-mode`              | Mempercepat langkah (hampir tanpa jeda). Cocok jika sudah yakin proses berjalan stabil.                        |

Selama berjalan, konsol menampilkan status rinci:

- filter apa yang sedang diterapkan di tabel MATCHAPRO,
- apakah skrip menunggu tabel selesai memuat,
- info jika baris dilewati karena terkunci oleh pengguna lain.

**Hasil:**
`artifacts/logs/log_sbr_autofill.csv` berisi ringkasan tiap baris (OK, WARN, ERROR).
Screenshot error/lock berada di `artifacts/screenshots/`.

---

### 5. Menjalankan cancel submit

```powershell
python sbr_cancel.py --match-by name --start 1 --end 20
```

Mirip autofill, hanya aksi akhirnya menekan tombol *Cancel Submit*.
Log tersimpan di `artifacts/logs/log_sbr_cancel.csv`, screenshot di `artifacts/screenshots_cancel/`.

Pastikan Excel berisi kolom `Nama` dan/atau `IDSBR` sesuai pilihan `--match-by`.

---

### 6. Kalau terjadi error, apa yang harus dicek?

1. **Tidak menemukan tombol Edit**

   - Pastikan kolom yang dipakai untuk `--match-by` terisi.
   - Lihat screenshot di `artifacts/screenshots/...` apakah tabel masih loading atau filter kosong.
2. **Form bertuliskan “Profiling Info – sedang diedit oleh user lain”**

   - Skrip akan mencatat event `WARN` dan lanjut ke baris berikutnya.
   - Ulangi baris tersebut nanti ketika form sudah bisa dibuka.
3. **Skrip tidak menemukan tab MATCHAPRO**

   - Chrome harus dijalankan melalui perintah remote debugging di atas dan tab “Direktori Usaha” sudah aktif sebelum menjalankan skrip.
4. **Ingin mengubah kecepatan/jeda**

   - Lihat `sbr_automation/config.py` untuk mengatur jeda klik, timeout, serta lokasi output.

---

### 7. FAQ singkat

- **Apakah log tetap dicatat jika tidak memakai `--stop-on-error`?**Ya. Semua kesalahan (mis. `CLICK_EDIT`, `FILL`, `SUBMIT`) tetap masuk ke CSV dan ditampilkan di ringkasan akhir.
- **Apakah bisa melanjutkan dari baris tertentu setelah ada error?**Bisa. Jalankan ulang dengan `--start <baris berikutnya>`; baris yang sudah sukses tidak disentuh lagi.
- **Bisakah menjalankan di akun berbeda?**
  Gunakan profil Chrome berbeda dengan opsi `--user-data-dir=` supaya login tidak saling menimpa.

---

Semoga panduan ini membantu. Jika menemukan pesan baru di log/screenshot yang belum terjelaskan, silahkan hubungi tim IPDS BPS Kabupaten Bulungan.
