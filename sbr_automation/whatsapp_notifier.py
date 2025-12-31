"""WhatsApp notification module using Selenium for SBR automation."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class WhatsAppConfig:
    """Configuration for WhatsApp notifications."""

    enabled: bool = False
    phone_number: str = ""
    group_name: str = ""
    notify_on_completion: bool = True
    notify_on_error_threshold: int = 0
    chrome_profile_path: str = "C:\\ChromeProfileSBR"
    wait_for_login_seconds: int = 30
    message_template: str = (
        "🤖 *SBR Autofill Report*\\n\\n"
        "📅 Run ID: {run_id}\\n"
        "🔢 Range: {row_range}\\n"
        "⏰ Started: {started_at}\\n"
        "⏱️ Duration: {duration}\\n\\n"
        "📊 *Summary*\\n"
        "✅ Success: {ok_count}\\n"
        "⚠️ Warnings: {warn_count}\\n"
        "❌ Errors: {error_count}\\n"
        "📝 Total Processed: {total_count}\\n\\n"
        "{error_details}\\n"
        "📁 Log: {log_path}"
    )


@dataclass
class NotificationSummary:
    """Summary data for WhatsApp notification."""

    run_id: str
    row_range: str
    started_at: str
    duration: str
    ok_count: int
    warn_count: int
    error_count: int
    total_count: int
    error_details: str
    log_path: str


class WhatsAppNotifier:
    """Send WhatsApp notifications using Selenium."""

    def __init__(self, config: WhatsAppConfig):
        """Initialize WhatsApp notifier with configuration.

        Args:
            config: WhatsApp configuration object
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None

    def _create_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver with WhatsApp profile.

        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={self.config.chrome_profile_path}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Suppress unnecessary logs
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        return driver

    def _wait_for_whatsapp_ready(self, driver: webdriver.Chrome, timeout: int = 30) -> bool:
        """Wait for WhatsApp Web to be ready.

        Args:
            driver: Chrome WebDriver instance
            timeout: Maximum seconds to wait

        Returns:
            True if WhatsApp is ready, False otherwise
        """
        try:
            # Wait for either QR code or chat list (already logged in)
            WebDriverWait(driver, timeout).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "canvas[aria-label]")
                or d.find_elements(By.CSS_SELECTOR, "div[data-testid='chat-list']")
                or d.find_elements(By.CSS_SELECTOR, "#pane-side")
            )

            # Check if QR code is present (not logged in)
            qr_elements = driver.find_elements(By.CSS_SELECTOR, "canvas[aria-label]")
            if qr_elements:
                print(f"⚠️  WhatsApp belum login. Silakan scan QR code dalam {timeout} detik...")
                # Wait for login to complete
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
                )
                print("✅ Login berhasil!")

            return True

        except TimeoutException:
            print(f"❌ Timeout menunggu WhatsApp Web ready ({timeout}s)")
            return False

    def _search_contact(self, driver: webdriver.Chrome, contact: str) -> bool:
        """Search for contact or group in WhatsApp.

        Args:
            driver: Chrome WebDriver instance
            contact: Phone number (with country code) or group name

        Returns:
            True if contact found, False otherwise
        """
        try:
            # Wait a bit for WhatsApp to fully load
            time.sleep(2)
            
            # Find search box
            search_selectors = [
                "div[contenteditable='true'][data-tab='3']",
                "div[title='Search input textbox']",
                "div[data-testid='chat-list-search']",
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not search_box:
                print("❌ Tidak dapat menemukan search box WhatsApp")
                return False

            # Scroll to element and click
            driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
            time.sleep(0.5)
            
            # Try clicking with JavaScript if normal click fails
            try:
                search_box.click()
            except Exception:
                driver.execute_script("arguments[0].click();", search_box)
            
            time.sleep(1)
            
            # Type contact name/number
            search_box.send_keys(contact)
            time.sleep(3)  # Wait for search results

            # Click first result
            result_selectors = [
                "div[data-testid='cell-frame-container']",
                "div[class*='_2aBzC']",
                "span[title='" + contact + "']",
            ]

            for selector in result_selectors:
                try:
                    result = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    # Scroll to result
                    driver.execute_script("arguments[0].scrollIntoView(true);", result)
                    time.sleep(0.3)
                    result.click()
                    time.sleep(2)
                    print(f"✅ Kontak '{contact}' ditemukan")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue

            print(f"❌ Kontak '{contact}' tidak ditemukan")
            return False

        except Exception as e:
            print(f"❌ Error saat mencari kontak: {e}")
            return False

    def _send_message(self, driver: webdriver.Chrome, message: str) -> bool:
        """Send message to current chat.

        Args:
            driver: Chrome WebDriver instance
            message: Message text to send

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Find message input box
            input_selectors = [
                "div[contenteditable='true'][data-tab='10']",
                "div[title='Type a message']",
                "div[data-testid='conversation-compose-box-input']",
            ]

            message_box = None
            for selector in input_selectors:
                try:
                    message_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not message_box:
                print("❌ Tidak dapat menemukan message box")
                return False

            # Click message box to focus
            message_box.click()
            time.sleep(0.5)

            # Replace \\n with actual newlines for proper formatting
            formatted_message = message.replace("\\n", "\n")
            
            # Use clipboard to paste message (most reliable method for emoji)
            # This works by copying to clipboard then pasting with Ctrl+V
            try:
                import pyperclip
                pyperclip.copy(formatted_message)
                message_box.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)
            except ImportError:
                # Fallback: Use JavaScript if pyperclip not available
                print("⚠️  pyperclip not installed, using JavaScript fallback")
                script = """
                var element = arguments[0];
                var text = arguments[1];
                
                // Create a text node and insert it
                var lines = text.split('\\n');
                element.innerHTML = '';
                
                for (var i = 0; i < lines.length; i++) {
                    var textNode = document.createTextNode(lines[i]);
                    element.appendChild(textNode);
                    
                    if (i < lines.length - 1) {
                        element.appendChild(document.createElement('br'));
                    }
                }
                
                // Trigger input event
                var event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
                
                // Set cursor to end
                var range = document.createRange();
                var sel = window.getSelection();
                range.selectNodeContents(element);
                range.collapse(false);
                sel.removeAllRanges();
                sel.addRange(range);
                element.focus();
                """
                driver.execute_script(script, message_box, formatted_message)
                time.sleep(1)

            # Send message using Enter key
            message_box.send_keys(Keys.ENTER)
            time.sleep(10)  # Wait longer for message to send (10 seconds)

            # Verify message was sent by checking if input box is empty
            try:
                # Check if message box is now empty (message sent)
                is_empty = driver.execute_script(
                    "return arguments[0].textContent.trim() === '';", 
                    message_box
                )
                
                if is_empty:
                    print("✅ Pesan terkirim!")
                    return True
                else:
                    print("⚠️  Pesan mungkin tidak terkirim (message box masih berisi text)")
                    return False
                    
            except Exception:
                # Fallback: assume sent if no error
                print("✅ Pesan terkirim! (tidak bisa verify)")
                return True

        except Exception as e:
            print(f"❌ Error saat mengirim pesan: {e}")
            return False

    def _format_message(self, summary: NotificationSummary) -> str:
        """Format notification message from summary data.

        Args:
            summary: Notification summary data

        Returns:
            Formatted message string
        """
        return self.config.message_template.format(
            run_id=summary.run_id,
            row_range=summary.row_range,
            started_at=summary.started_at,
            duration=summary.duration,
            ok_count=summary.ok_count,
            warn_count=summary.warn_count,
            error_count=summary.error_count,
            total_count=summary.total_count,
            error_details=summary.error_details,
            log_path=summary.log_path,
        )

    def send_notification(self, summary: NotificationSummary) -> bool:
        """Send WhatsApp notification with run summary.

        Args:
            summary: Notification summary data

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.config.enabled:
            print("ℹ️  WhatsApp notification disabled")
            return False

        # Check error threshold
        if summary.error_count < self.config.notify_on_error_threshold:
            print(
                f"ℹ️  Skipping notification (errors {summary.error_count} < threshold {self.config.notify_on_error_threshold})"
            )
            return False

        # Determine target (phone or group)
        target = self.config.phone_number if self.config.phone_number else self.config.group_name
        if not target:
            print("❌ WhatsApp target tidak dikonfigurasi (phone_number atau group_name)")
            return False

        print(f"\n{'='*60}")
        try:
            print(f"📱 Mengirim notifikasi WhatsApp ke: {target}")
        except UnicodeEncodeError:
            print(f"[WA] Mengirim notifikasi WhatsApp ke: {target}")
        print(f"{'='*60}\n")

        try:
            # Create driver
            self.driver = self._create_driver()

            # Open WhatsApp Web
            self.driver.get("https://web.whatsapp.com")

            # Wait for WhatsApp to be ready
            if not self._wait_for_whatsapp_ready(self.driver, self.config.wait_for_login_seconds):
                return False

            # Search and select contact/group
            if not self._search_contact(self.driver, target):
                return False

            # Format and send message
            message = self._format_message(summary)
            success = self._send_message(self.driver, message)

            return success

        except WebDriverException as e:
            print(f"❌ WebDriver error: {e}")
            return False

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

        finally:
            # Always close browser for memory efficiency
            if self.driver:
                print("\n🔒 Menutup browser WhatsApp...")
                time.sleep(1)  # Brief pause before closing
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
                print("✅ Browser ditutup\n")


def create_notification_summary(
    run_id: str,
    started_at: str,
    ok_count: int,
    warn_count: int,
    error_count: int,
    error_rows: list[dict],
    log_path: str,
    start_time: float,
    start_row: int | None = None,
    end_row: int | None = None,
) -> NotificationSummary:
    """Create notification summary from run results.

    Args:
        run_id: Run identifier
        started_at: ISO timestamp of run start
        ok_count: Number of successful rows
        warn_count: Number of warnings
        error_count: Number of errors
        error_rows: List of error row dictionaries
        log_path: Path to log file
        start_time: Start time (time.time())
        start_row: Starting row number
        end_row: Ending row number

    Returns:
        NotificationSummary object
    """
    # Calculate duration
    duration_seconds = int(time.time() - start_time)
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        duration = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        duration = f"{minutes}m {seconds}s"
    else:
        duration = f"{seconds}s"

    # Format row range
    if start_row and end_row:
        row_range = f"Baris {start_row} - {end_row}"
    elif start_row:
        row_range = f"Baris {start_row}+"
    else:
        row_range = "Semua baris"

    # Format error details dengan informasi lebih lengkap
    error_details = ""
    if error_rows:
        error_details = "🔴 *Detail Errors:*\\n"
        
        for i, err in enumerate(error_rows[:10], 1):  # Show top 10 instead of 5
            row_index = err.get("row_index", "?")
            idsbr = err.get("idsbr", "N/A")
            nama = err.get("nama", "N/A")
            stage = err.get("stage", "UNKNOWN")
            note = err.get("note", "")
            
            # Don't truncate names - show full name
            # Truncate only if extremely long (>50 chars)
            if len(nama) > 50:
                nama = nama[:47] + "..."
            
            # Format error entry dengan baris, nama toko, dan alasan
            error_details += f"\\n*{i}. Baris {row_index}*\\n"
            error_details += f"   📍 IDSBR: {idsbr}\\n"
            error_details += f"   🏪 Nama: {nama}\\n"
            error_details += f"   ⚠️ Stage: {stage}\\n"
            
            if note:
                # Extract error reason dari note
                # Clean up CODE: prefix dan technical details
                clean_note = note.replace("CODE:", "").strip()
                
                # Truncate hanya jika sangat panjang (>100 chars)
                if len(clean_note) > 100:
                    clean_note = clean_note[:97] + "..."
                
                error_details += f"   💬 Alasan: {clean_note}\\n"

        if len(error_rows) > 10:
            error_details += f"\\n...dan {len(error_rows) - 10} error lainnya\\n"
    
    total_count = ok_count + warn_count + error_count

    return NotificationSummary(
        run_id=run_id,
        row_range=row_range,
        started_at=started_at,
        duration=duration,
        ok_count=ok_count,
        warn_count=warn_count,
        error_count=error_count,
        total_count=total_count,
        error_details=error_details,
        log_path=log_path,
    )
