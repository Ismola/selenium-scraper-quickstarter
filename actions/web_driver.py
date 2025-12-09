import logging
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.config import PAGE_MAX_TIMEOUT, BASE_URL, DOWNLOAD_DIR, STAGE, BROWSER_LANGUAGE, has_display

import psutil


def get_driver_chrome():
    options = Options()
    options = add_generic_arguments(options)
    options = add_chrome_arguments(options)
    
    # In Docker/Alpine environment, use the system chromium and chromedriver
    if (os.environ.get('DOCKERIZED', False) or os.path.exists('/usr/bin/chromedriver') or STAGE == 'production'):
        service = Service('/usr/bin/chromedriver')
        options.binary_location = '/usr/bin/chromium-browser'
    else:
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_driver_firefox():
    options = webdriver.FirefoxOptions()
    options = add_generic_arguments(options)
    driver = webdriver.Firefox(options=options)
    return driver


def get_page(browser = 'chrome', url = BASE_URL):
    # Return driver
    logging.info('Starting driver')
    if browser == 'firefox':
        driver = get_driver_firefox()
    else:
        driver = get_driver_chrome()
    logging.info('Getting URL')
    driver.get(url)
    return driver


def get_wait(driver):
    # Return wait function
    return WebDriverWait(driver, PAGE_MAX_TIMEOUT)


def close_driver(driver):
    if driver:
        driver.quit()


# This function, kill all chrome process
def kill_driver_process():
    for proc in psutil.process_iter():
        try:
            if proc.name() == "chrome" or proc.name() == "chromedriver" or proc.name() == "chrome.exe":
                proc.kill()
        except psutil.NoSuchProcess:
            pass


def add_generic_arguments(options):
    if not has_display():
        logging.info("Running in headless mode")
        options.add_argument("--headless")
    else:
        logging.info("Running in GUI mode")

    # Set language based on BROWSER_LANGUAGE configuration
    if BROWSER_LANGUAGE.lower() == 'es':
        language_arg = "--lang=es-ES"
    else:
        language_arg = "--lang=en-US"
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
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-cache")
    options.add_argument("--disable-translate")
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
    
    # Set language based on BROWSER_LANGUAGE configuration
    if BROWSER_LANGUAGE.lower() == 'es':
        language_list = ["es-ES", "es"]
    else:
        language_list = ["en-US", "en"]
    
    pref_opt = {
        # Disable all type of popups
        "profile.default_content_setting_values.notifications": 2,
        "profile.password_manager_enabled": False,
        "intl.accept_languages": language_list,
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
