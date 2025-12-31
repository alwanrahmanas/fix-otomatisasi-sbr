import os
import sys
import time
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuration
DATA_DIR = Path("data")
BATCH_SIZE = 20
START_FROM = 1
WHATSAPP_CONFIG = "config/whatsapp.json"
LOG_DIR = Path("artifacts/logs/batch_runner")

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

def setup_logging():
    """Setup logging directory and return log file path."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_DIR / f"batch_run_{timestamp}.log"
    return log_file

def log_message(message, log_file=None):
    """Print message and optionally write to log file."""
    print(message)
    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')

def parse_batch_output(output):
    """Parse subprocess output to extract batch statistics."""
    stats = {
        'success': 0,
        'errors': 0,
        'skipped': 0,
        'processed': 0
    }
    
    lines = output.split('\n')
    for line in lines:
        # Look for summary lines
        if 'Baris sukses' in line:
            try:
                stats['success'] = int(line.split(':')[-1].strip())
            except (ValueError, IndexError):
                pass
        elif 'Baris bermasalah' in line:
            try:
                stats['errors'] = int(line.split(':')[-1].strip())
            except (ValueError, IndexError):
                pass
        elif 'Baris dilewati' in line:
            try:
                stats['skipped'] = int(line.split(':')[-1].strip())
            except (ValueError, IndexError):
                pass
    
    stats['processed'] = stats['success'] + stats['errors'] + stats['skipped']
    return stats

def run_batch():
    # Setup logging
    log_file = setup_logging()
    log_message(f"📝 Log batch runner: {log_file}", log_file)
    log_message(f"⏰ Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    
    excel_file = get_excel_file()
    total_data_rows = count_rows(excel_file)
    
    log_message(f"✅ Total data ditemukan: {total_data_rows} baris", log_file)
    log_message(f"🚀 Memulai batch process dari baris {START_FROM} dengan ukuran {BATCH_SIZE}...", log_file)
    log_message(f"📁 File Excel: {excel_file.name}", log_file)
    
    current_start = START_FROM
    batch_number = 1
    total_stats = {
        'success': 0,
        'errors': 0,
        'skipped': 0,
        'batches_completed': 0,
        'batches_failed': 0
    }
    
    while current_start <= total_data_rows:
        current_end = current_start + BATCH_SIZE - 1
        
        # Ensure we don't go past the last row
        if current_end > total_data_rows:
            current_end = total_data_rows
        
        expected_rows = current_end - current_start + 1
        
        separator = f"\n{'='*70}"
        log_message(separator, log_file)
        log_message(f"▶️  BATCH #{batch_number}: Baris {current_start} sampai {current_end} (Total: {expected_rows} baris)", log_file)
        log_message(f"{'='*70}\n", log_file)
        
        # Construct command
        cmd = [
            sys.executable, "-u", "sbr_fill.py",  # -u for unbuffered output
            "--match-by", "idsbr",
            "--start", str(current_start),
            "--end", str(current_end),
            "--whatsapp-config", WHATSAPP_CONFIG,
            "--resume",  # Enable resume mode to skip already processed rows
            # Removed --stop-on-error to continue processing all batches
        ]
        
        batch_start_time = time.time()
        
        # Prepare environment with unbuffered output and UTF-8 encoding
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        
        try:
            # Run the subprocess with real-time output streaming
            log_message("📋 Menjalankan sbr_fill.py...\n", log_file)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr to stdout
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,  # Line buffered
                env=env     # Use unbuffered & utf-8 env
            )
            
            # Stream output in real-time
            output_lines = []
            if process.stdout:
                for line in process.stdout:
                    # Print to console (real-time)
                    try:
                        print(line, end='')
                    except UnicodeEncodeError:
                        # Fallback for terminals that don't support utf-8
                        print(line.encode('ascii', 'replace').decode(), end='')
                        
                    # Save to log file
                    if log_file:
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(line)
                    # Store for parsing
                    output_lines.append(line)
            
            # Wait for process to complete
            return_code = process.wait()
            
            batch_duration = time.time() - batch_start_time
            
            # Combine output for parsing
            full_output = ''.join(output_lines)
            
            log_message("\n" + "-" * 70, log_file)
            
            # Parse batch statistics from the captured output
            stats = parse_batch_output(full_output)

            
            # Update total statistics
            total_stats['success'] += stats['success']
            total_stats['errors'] += stats['errors']
            total_stats['skipped'] += stats['skipped']
            
            # Display batch summary
            log_message(f"\n📊 RINGKASAN BATCH #{batch_number}:", log_file)
            log_message(f"  ⏱️  Durasi        : {batch_duration:.2f} detik", log_file)
            log_message(f"  📝 Diharapkan    : {expected_rows} baris", log_file)
            log_message(f"  ✅ Diproses      : {stats['processed']} baris", log_file)
            log_message(f"  🎯 Sukses        : {stats['success']} baris", log_file)
            log_message(f"  ❌ Error         : {stats['errors']} baris", log_file)
            log_message(f"  ⏭️  Dilewati      : {stats['skipped']} baris", log_file)
            log_message(f"  🔢 Return code   : {return_code}", log_file)
            
            # Calculate next start position based on what was actually processed
            # If all rows were processed (success + error + skipped = expected), move to next batch
            # Otherwise, retry from current_start (in case of early termination)
            if stats['processed'] == expected_rows:
                # All rows processed, move to next batch
                next_start = current_end + 1
                total_stats['batches_completed'] += 1
                log_message(f"\n✅ Batch selesai, lanjut ke baris {next_start}", log_file)
            elif stats['processed'] > 0:
                # Some rows processed, continue from where we left off
                # Since we use --resume, we can continue from current_end + 1
                next_start = current_end + 1
                total_stats['batches_completed'] += 1
                warning = f"⚠️  PERINGATAN: Hanya {stats['processed']} dari {expected_rows} baris yang diproses!"
                log_message(f"\n{warning}", log_file)
                log_message("   Kemungkinan penyebab:", log_file)
                log_message("   - Error yang menghentikan proses lebih awal", log_file)
                log_message("   - Data Excel tidak sesuai ekspektasi", log_file)
                log_message("   - Resume mode melewati baris tertentu", log_file)
                log_message(f"   ℹ️  Dengan --resume aktif, baris yang sudah OK akan dilewati otomatis", log_file)
                log_message(f"   📍 Lanjut ke baris {next_start}", log_file)
            else:
                # No rows processed, retry same batch
                next_start = current_start
                warning = f"❌ CRITICAL: Tidak ada baris yang diproses dalam batch ini!"
                log_message(f"\n{warning}", log_file)
                log_message("   Periksa output sbr_fill.py di atas untuk detail error", log_file)
                log_message(f"   🔄 Akan retry batch yang sama (baris {current_start}-{current_end})", log_file)
                total_stats['batches_failed'] += 1
                
                # Prevent infinite loop - if same batch fails 3 times, skip it
                if batch_number > 1 and next_start == current_start:
                    log_message("   ⚠️  Batch gagal berulang kali, skip ke batch berikutnya", log_file)
                    next_start = current_end + 1
            
        except KeyboardInterrupt:
            log_message("\n⚠️  Batch process dihentikan oleh pengguna.", log_file)
            break
        except Exception as e:
            log_message(f"❌ Error menjalankan batch: {e}", log_file)
            total_stats['batches_failed'] += 1
            next_start = current_end + 1  # Skip to next batch on exception
        
        # Update start for next batch
        current_start = next_start
        batch_number += 1
        
        if current_start <= total_data_rows:
            log_message("\n⏳ Istirahat 5 detik sebelum batch berikutnya...", log_file)
            time.sleep(5)

    # Final summary
    separator = f"\n{'='*70}"
    log_message(separator, log_file)
    log_message("🎉 SEMUA BATCH SELESAI!", log_file)
    log_message(separator, log_file)
    log_message(f"\n📊 RINGKASAN KESELURUHAN:", log_file)
    log_message(f"  📦 Total batch dijalankan : {batch_number - 1}", log_file)
    log_message(f"  ✅ Batch sukses          : {total_stats['batches_completed']}", log_file)
    log_message(f"  ❌ Batch gagal           : {total_stats['batches_failed']}", log_file)
    log_message(f"  🎯 Total baris sukses    : {total_stats['success']}", log_file)
    log_message(f"  ❌ Total baris error     : {total_stats['errors']}", log_file)
    log_message(f"  ⏭️  Total baris dilewati  : {total_stats['skipped']}", log_file)
    log_message(f"  📝 Log lengkap tersimpan : {log_file}", log_file)
    log_message(f"  ⏰ Waktu selesai         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    log_message(separator, log_file)

if __name__ == "__main__":
    run_batch()
