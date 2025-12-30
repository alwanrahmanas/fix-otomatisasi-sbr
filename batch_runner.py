import os
import sys
import time
import subprocess
import pandas as pd
from pathlib import Path

# Configuration
DATA_DIR = Path("data")
BATCH_SIZE = 30
START_FROM = 30
WHATSAPP_CONFIG = "config/whatsapp.json"

def get_excel_file():
    """Find the first Excel file in the data directory."""
    if not DATA_DIR.exists():
        print(f"❌ Directory '{DATA_DIR}' tidak ditemukan.")
        sys.exit(1)
    
    files = list(DATA_DIR.glob("*.xlsx"))
    if not files:
        print(f"❌ Tidak ada file .xlsx di folder '{DATA_DIR}'.")
        sys.exit(1)
    
    return files[0]

def count_rows(file_path):
    """Count total rows in the first sheet of Excel file."""
    print(f"📊 Membaca file: {file_path.name}...")
    try:
        # Read only headers to check columns, but we need total length
        # Reading whole file might be slow if huge, but safe for typical SBR files
        df = pd.read_excel(file_path)
        return len(df)
    except Exception as e:
        print(f"❌ Error membaca Excel: {e}")
        sys.exit(1)

def run_batch():
    excel_file = get_excel_file()
    total_data_rows = count_rows(excel_file)
    
    # Adjust for Excel 1-based indexing + header usually taking row 1
    # If pandas says 100 rows, it means 100 data rows.
    # Usually sbr_fill.py treats row 1 as header, data starts at 2 (index 1).
    # If pandas reads 100 records, the last row index in Excel is usually 101.
    # However, sbr_fill.py usually refers to 'data row index' or 'excel absolute row'?
    # Based on previous logs: "Baris 1... Target: ..."
    # Assuming sbr_fill.py 'start' corresponds to the logical nth data row.
    
    print(f"✅ Total data ditemukan: {total_data_rows} baris")
    print(f"🚀 Memulai batch process dari baris {START_FROM} dengan ukuran {BATCH_SIZE}...")
    
    current_start = START_FROM
    
    while current_start <= total_data_rows:
        current_end = current_start + BATCH_SIZE - 1
        
        # Ensure we don't go past the last row
        if current_end > total_data_rows:
            current_end = total_data_rows
            
        print(f"\n{'='*50}")
        print(f"▶️  Menjalankan Batch: Baris {current_start} sampai {current_end}")
        print(f"{'='*50}\n")
        
        # Construct command
        cmd = [
            sys.executable, "sbr_fill.py",
            "--match-by", "idsbr",
            "--start", str(current_start),
            "--end", str(current_end),
            "--whatsapp-config", WHATSAPP_CONFIG,
            "--stop-on-error"  # Optional: stop batch if critical error occurs? 
                               # Removed to ensure it tries all batches, or User can decide.
                               # Let's keep it robust: don't stop on error so next batch continues.
        ]
        
        try:
            # Run the subprocess
            subprocess.run(cmd, check=False)
            
        except KeyboardInterrupt:
            print("\n⚠️  Batch process dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"❌ Error menjalankan batch: {e}")
        
        # Update start for next batch
        current_start += BATCH_SIZE
        
        if current_start <= total_data_rows:
            print("⏳ Istirahat 5 detik sebelum batch berikutnya...")
            time.sleep(5)

    print("\n🎉 Semua batch selesai!")

if __name__ == "__main__":
    run_batch()
