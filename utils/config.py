import os
import platform
from dotenv import load_dotenv

# Carga el .env desde la ruta absoluta
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Global variables
STAGE = os.getenv("STAGE") or 'staging'
VALID_TOKEN = os.getenv("VALID_TOKEN") or 'sample'
AUTO_DELETE_LOGS = os.getenv("AUTO_DELETE_LOGS") or True
HEADLESS_MODE = os.getenv("HEADLESS_MODE") or 'auto'
DOWNLOAD_DIR = os.path.abspath("temp_downloads")
PAGE_MAX_TIMEOUT = 7
DOWNLOAD_MAX_TIMEOUT = 4
BASE_URL = 'https://www.google.com/'
LOG_FILE_DELETION_DAYS = 30

# Streaming configuration
STREAMING_ENABLED = os.getenv("STREAMING_ENABLED", "false").lower() == "true"
STREAMING_FPS = int(os.getenv("STREAMING_FPS", "10"))
STREAMING_QUALITY = int(os.getenv("STREAMING_QUALITY", "80"))
STREAMING_WIDTH = int(os.getenv("STREAMING_WIDTH", "1280"))
STREAMING_HEIGHT = int(os.getenv("STREAMING_HEIGHT", "720"))

# External streaming configuration
EXTERNAL_STREAMING_ENABLED = os.getenv(
    "EXTERNAL_STREAMING_ENABLED", "false").lower() == "true"
RTMP_SERVER_URL = os.getenv("RTMP_SERVER_URL", "")
STREAM_KEY = os.getenv("STREAM_KEY", "")
HTTP_STREAMING_ENDPOINT = os.getenv("HTTP_STREAMING_ENDPOINT", "")
STREAMING_PROTOCOL = os.getenv(
    "STREAMING_PROTOCOL", "rtmp")  # rtmp, http, file
OUTPUT_FILE_PATH = os.getenv("OUTPUT_FILE_PATH", "/tmp/selenium_stream.mp4")


def has_display():
    if HEADLESS_MODE == 'True':
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
