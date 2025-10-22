import logging
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.config import PAGE_MAX_TIMEOUT, BASE_URL, DOWNLOAD_DIR, has_display, STREAMING_ENABLED, STREAMING_WIDTH, STREAMING_HEIGHT, STAGE

import psutil

# Global streaming service instance
_streaming_service = None


def get_driver_chrome():
    options = Options()
    options = add_generic_arguments(options)
    options = add_chrome_arguments(options)

    # Use the driver path we know works
    driver_path = "/root/.wdm/drivers/chromedriver/linux64/141.0.7390.122/chromedriver-linux64/chromedriver"

    # Always use our installed driver for now
    if os.path.exists(driver_path):
        service = Service(driver_path)
        # Use google-chrome-stable
        options.binary_location = '/usr/bin/google-chrome-stable'
    else:
        # Fallback to webdriver-manager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_driver_firefox():
    options = webdriver.FirefoxOptions()
    options = add_generic_arguments(options)
    driver = webdriver.Firefox(options=options)
    return driver


def get_page(browser='chrome', url=BASE_URL):
    global _streaming_service

    # Return driver
    logging.info('Starting driver')
    if browser == 'firefox':
        driver = get_driver_firefox()
    else:
        driver = get_driver_chrome()

    logging.info('Getting URL')
    driver.get(url)

    # Auto-start streaming AFTER driver is ready
    if STREAMING_ENABLED and not _streaming_service:
        try:
            from utils.external_streaming_service import ExternalStreamingService
            _streaming_service = ExternalStreamingService()
            _streaming_service.set_driver(driver)
            config = {
                "protocol": "file",
                "output_file": "/tmp/current_session.mp4",
                "fps": 10,
                "width": STREAMING_WIDTH,
                "height": STREAMING_HEIGHT
            }
            logging.info("Auto-starting streaming...")
            _streaming_service.start_streaming(config)
            logging.info("Streaming started successfully")
        except Exception as e:
            logging.error(f"Failed to start streaming: {e}")

    # Update driver for existing streaming service
    elif STREAMING_ENABLED and _streaming_service:
        try:
            _streaming_service.set_driver(driver)
            logging.info("Driver updated for existing streaming service")
        except Exception as e:
            logging.error(f"Failed to update driver for streaming: {e}")

    return driver


def get_wait(driver):
    # Return wait function
    return WebDriverWait(driver, PAGE_MAX_TIMEOUT)


def close_driver(driver):
    global _streaming_service

    if driver:
        driver.quit()

    # No auto-stop streaming when closing driver - keep it active for next call
    # User can manually stop it with /stream/stop endpoint


def get_streaming_status():
    """Get current streaming status"""
    global _streaming_service
    if _streaming_service and _streaming_service.is_streaming():
        return {
            "streaming": True,
            "output_file": "/tmp/current_session.mp4",
            "protocol": "file"
        }
    return {"streaming": False}


def stop_streaming():
    """Manually stop streaming"""
    global _streaming_service
    if _streaming_service and _streaming_service.is_streaming():
        _streaming_service.stop_streaming()
        _streaming_service = None
        return {"success": True, "message": "Streaming stopped"}
    return {"success": False, "message": "No streaming active"}


# This function, kill all chrome process
def kill_driver_process():
    for proc in psutil.process_iter():
        try:
            if proc.name() == "chrome" or proc.name() == "chromedriver" or proc.name() == "chrome.exe":
                proc.kill()
        except psutil.NoSuchProcess:
            pass


def add_generic_arguments(options):
    # Force visible mode when streaming is enabled
    if STREAMING_ENABLED:
        logging.info("Streaming enabled - forcing GUI mode")
        options.add_argument(
            f"--window-size={STREAMING_WIDTH},{STREAMING_HEIGHT}")
    elif not has_display():
        logging.info("Running in headless mode")
        options.add_argument("--headless")
    else:
        logging.info("Running in GUI mode")
        options.add_argument(
            f"--window-size={STREAMING_WIDTH},{STREAMING_HEIGHT}")

    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extension")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--password-store=basic")
    options.add_argument("--no-sandbox")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--no-proxy-server")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-cache")
    options.add_argument("--disable-translate")

    # Additional options for streaming
    if STREAMING_ENABLED:
        options.add_argument("--enable-media-stream")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")

    return options


def add_chrome_arguments(options):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-blink-features=AutomationControlled")
    exp_opt = [
        # Disable possible errors
        "enable_automation",
        "ignore-certificate-errors",
        "enable-logging"
    ]
    options.add_experimental_option("excludeSwitches", exp_opt)
    pref_opt = {
        # Disable all type of popups
        "profile.default_content_setting_values.notifications": 2,
        "profile.password_manager_enabled": False,
        "intl.accept_languages": ["es-Es", "es"],
        "credentials_enable_service": False,

        # Automatic downloads
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        # Optional: Open PDFs in a separate viewer
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", pref_opt)

    return options
