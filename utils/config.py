import os
import platform
from dotenv import load_dotenv
load_dotenv()
# Global variables
STAGE = os.getenv("STAGE") or 'staging'
VALID_TOKEN = os.getenv("VALID_TOKEN") or 'sample'
AUTO_DELETE_LOGS = os.getenv("AUTO_DELETE_LOGS") or True
HEADLESS_MODE = os.getenv("HEADLESS_MODE") or 'auto'
DOWNLOAD_DIR = 'temp_downloads'
PAGE_MAX_TIMEOUT = 7
DOWNLOAD_MAX_TIMEOUT = 4
# TODO Change this to target url
URL = "https://www.google.com/"


def has_display():
    if HEADLESS_MODE == False:
        return False

    # ⬇️ Automatic mode
    system = platform.system()
    if system == "Windows":
        try:
            from screeninfo import get_monitors
            monitors = get_monitors()
            return len(monitors) > 0
        except ImportError:
            return False
    elif system == "Linux" or system == "Darwin":
        display_env = os.environ.get("DISPLAY")
        return display_env is not None
    else:
        # Other operating systems, we assume that there is no screen available
        return False
