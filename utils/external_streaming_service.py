import subprocess
import threading
import time
import logging
import os
import signal
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from utils.config import (
    STREAMING_FPS, STREAMING_WIDTH, STREAMING_HEIGHT,
    EXTERNAL_STREAMING_ENABLED, RTMP_SERVER_URL, STREAM_KEY,
    HTTP_STREAMING_ENDPOINT, STREAMING_PROTOCOL, OUTPUT_FILE_PATH
)


class ExternalStreamingService:
    """Service to stream browser automation to external services"""

    def __init__(self):
        self.driver = None
        self.streaming = False
        self.external_streaming = False
        self.capture_thread = None
        self.ffmpeg_process = None
        self.logger = logging.getLogger(__name__)
        self.frame_queue = []
        self.max_queue_size = 60  # 2 seconds at 30fps

    def set_driver(self, driver):
        """Set the selenium driver for streaming"""
        self.driver = driver
        self.logger.info("Driver set for external streaming service")

    def start_streaming(self, streaming_config=None):
        """Start the external streaming process"""
        if self.streaming:
            self.logger.warning("Streaming already active")
            return False

        if not self.driver:
            self.logger.error("No driver available for streaming")
            return False

        if streaming_config:
            self.streaming_config = streaming_config
        else:
            self.streaming_config = self._get_default_config()

        self.streaming = True

        # Start frame capture thread
        self.capture_thread = threading.Thread(
            target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        # Start external streaming if enabled
        if EXTERNAL_STREAMING_ENABLED or streaming_config:
            self._start_external_streaming()

        self.logger.info("External streaming started")
        return True

    def stop_streaming(self):
        """Stop the streaming process"""
        self.streaming = False
        self.external_streaming = False

        if self.capture_thread:
            self.capture_thread.join(timeout=2)

        if self.ffmpeg_process:
            self._stop_ffmpeg()

        self.logger.info("External streaming stopped")

    def _get_default_config(self):
        """Get default streaming configuration"""
        return {
            "protocol": STREAMING_PROTOCOL,
            "rtmp_url": RTMP_SERVER_URL,
            "stream_key": STREAM_KEY,
            "http_endpoint": HTTP_STREAMING_ENDPOINT,
            "output_file": OUTPUT_FILE_PATH,
            "fps": STREAMING_FPS,
            "width": STREAMING_WIDTH,
            "height": STREAMING_HEIGHT
        }

    def _capture_loop(self):
        """Main capture loop for screenshots"""
        frame_time = 1.0 / STREAMING_FPS

        while self.streaming and self.driver:
            try:
                start_time = time.time()

                # Capture screenshot
                screenshot = self.driver.get_screenshot_as_png()

                # Process frame
                frame = self._process_screenshot(screenshot)

                if frame is not None and self.external_streaming:
                    self._send_frame_to_ffmpeg(frame)

                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)

    def _process_screenshot(self, screenshot_bytes):
        """Process screenshot into video frame format"""
        try:
            # Convert to PIL Image
            image = Image.open(BytesIO(screenshot_bytes))

            # Resize if needed
            if image.size != (STREAMING_WIDTH, STREAMING_HEIGHT):
                image = image.resize(
                    (STREAMING_WIDTH, STREAMING_HEIGHT), Image.Resampling.LANCZOS)

            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to numpy array
            frame = np.array(image)

            return frame

        except Exception as e:
            self.logger.error(f"Error processing screenshot: {e}")
            return None

    def _start_external_streaming(self):
        """Start external streaming using FFmpeg"""
        try:
            config = self.streaming_config
            protocol = config.get("protocol", "rtmp")

            if protocol == "rtmp":
                self._start_rtmp_streaming(config)
            elif protocol == "http":
                self._start_http_streaming(config)
            elif protocol == "file":
                self._start_file_streaming(config)
            else:
                self.logger.error(
                    f"Unsupported streaming protocol: {protocol}")
                return False

            self.external_streaming = True
            return True

        except Exception as e:
            self.logger.error(f"Error starting external streaming: {e}")
            return False

    def _start_rtmp_streaming(self, config):
        """Start RTMP streaming"""
        rtmp_url = config.get("rtmp_url", RTMP_SERVER_URL)
        stream_key = config.get("stream_key", STREAM_KEY)

        if not rtmp_url or not stream_key:
            raise ValueError(
                "RTMP URL and Stream Key are required for RTMP streaming")

        full_rtmp_url = f"{rtmp_url}/{stream_key}"

        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f"{STREAMING_WIDTH}x{STREAMING_HEIGHT}",
            '-r', str(STREAMING_FPS),
            '-i', '-',  # Input from stdin
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'veryfast',
            '-maxrate', '3000k',
            '-bufsize', '6000k',
            '-vf', f'scale={STREAMING_WIDTH}:{STREAMING_HEIGHT}',
            '-g', str(STREAMING_FPS * 2),  # Keyframe interval
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-f', 'flv',
            full_rtmp_url
        ]

        self.logger.info(f"Starting RTMP stream to: {rtmp_url}")
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _start_http_streaming(self, config):
        """Start HTTP streaming"""
        endpoint = config.get("http_endpoint", HTTP_STREAMING_ENDPOINT)

        if not endpoint:
            raise ValueError("HTTP endpoint is required for HTTP streaming")

        # For HTTP streaming, we'll use HLS format
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f"{STREAMING_WIDTH}x{STREAMING_HEIGHT}",
            '-r', str(STREAMING_FPS),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'veryfast',
            '-f', 'hls',
            '-hls_time', '2',
            '-hls_list_size', '3',
            '-hls_flags', 'delete_segments',
            endpoint
        ]

        self.logger.info(f"Starting HTTP stream to: {endpoint}")
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _start_file_streaming(self, config):
        """Start file output streaming"""
        output_file = config.get("output_file", OUTPUT_FILE_PATH)

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f"{STREAMING_WIDTH}x{STREAMING_HEIGHT}",
            '-r', str(STREAMING_FPS),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            output_file
        ]

        self.logger.info(f"Starting file output to: {output_file}")
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _send_frame_to_ffmpeg(self, frame):
        """Send frame to FFmpeg process"""
        try:
            if self.ffmpeg_process and self.ffmpeg_process.stdin:
                frame_bytes = frame.tobytes()
                self.ffmpeg_process.stdin.write(frame_bytes)
                self.ffmpeg_process.stdin.flush()
        except Exception as e:
            self.logger.error(f"Error sending frame to FFmpeg: {e}")
            self._stop_ffmpeg()

    def _stop_ffmpeg(self):
        """Stop FFmpeg process"""
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
                self.ffmpeg_process.wait()
            except Exception as e:
                self.logger.error(f"Error stopping FFmpeg: {e}")
            finally:
                self.ffmpeg_process = None

    def is_streaming(self):
        """Check if streaming is active"""
        return self.streaming

    def is_external_streaming(self):
        """Check if external streaming is active"""
        return self.external_streaming

    def get_stream_info(self):
        """Get streaming information"""
        return {
            "streaming": self.streaming,
            "external_streaming": self.external_streaming,
            "fps": STREAMING_FPS,
            "resolution": f"{STREAMING_WIDTH}x{STREAMING_HEIGHT}",
            "has_driver": self.driver is not None,
            "protocol": self.streaming_config.get("protocol", "none") if hasattr(self, 'streaming_config') else "none",
            "ffmpeg_running": self.ffmpeg_process is not None and self.ffmpeg_process.poll() is None
        }

    def update_streaming_config(self, config):
        """Update streaming configuration on the fly"""
        if self.external_streaming:
            self.logger.info(
                "Restarting external streaming with new configuration")
            self._stop_ffmpeg()
            self.streaming_config.update(config)
            self._start_external_streaming()
        else:
            self.streaming_config = config


# Global external streaming service instance
external_streaming_service = ExternalStreamingService()
