import base64
import io
import threading
import time
import logging
from PIL import Image
import cv2
import numpy as np
from selenium.webdriver.common.by import By
from utils.config import STREAMING_FPS, STREAMING_QUALITY, STREAMING_WIDTH, STREAMING_HEIGHT


class StreamingService:
    """Service to handle browser streaming for real-time visualization"""
    
    def __init__(self):
        self.driver = None
        self.streaming = False
        self.stream_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.subscribers = set()
        self.logger = logging.getLogger(__name__)
        
    def set_driver(self, driver):
        """Set the selenium driver for streaming"""
        self.driver = driver
        self.logger.info("Driver set for streaming service")
        
    def start_streaming(self):
        """Start the streaming process"""
        if self.streaming:
            self.logger.warning("Streaming already active")
            return False
            
        if not self.driver:
            self.logger.error("No driver available for streaming")
            return False
            
        self.streaming = True
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        self.logger.info("Streaming started")
        return True
        
    def stop_streaming(self):
        """Stop the streaming process"""
        self.streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=2)
        self.logger.info("Streaming stopped")
        
    def _stream_loop(self):
        """Main streaming loop that captures and processes frames"""
        frame_time = 1.0 / STREAMING_FPS
        
        while self.streaming and self.driver:
            try:
                start_time = time.time()
                
                # Capture screenshot from browser
                screenshot = self.driver.get_screenshot_as_png()
                
                # Process the image
                frame = self._process_screenshot(screenshot)
                
                if frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame
                
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"Error in streaming loop: {e}")
                time.sleep(0.1)  # Brief pause before retry
                
    def _process_screenshot(self, screenshot_bytes):
        """Process screenshot bytes into streaming format"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            # Resize if needed
            if image.size != (STREAMING_WIDTH, STREAMING_HEIGHT):
                image = image.resize((STREAMING_WIDTH, STREAMING_HEIGHT), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for OpenCV
            img_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), STREAMING_QUALITY]
            _, encoded_img = cv2.imencode('.jpg', img_bgr, encode_param)
            
            # Convert to base64 for web transmission
            img_base64 = base64.b64encode(encoded_img.tobytes()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            self.logger.error(f"Error processing screenshot: {e}")
            return None
    
    def get_current_frame(self):
        """Get the current frame for streaming"""
        with self.frame_lock:
            return self.current_frame
    
    def add_subscriber(self, subscriber_id):
        """Add a subscriber to the streaming service"""
        self.subscribers.add(subscriber_id)
        self.logger.info(f"Added subscriber: {subscriber_id}")
        
    def remove_subscriber(self, subscriber_id):
        """Remove a subscriber from the streaming service"""
        self.subscribers.discard(subscriber_id)
        self.logger.info(f"Removed subscriber: {subscriber_id}")
        
    def get_subscriber_count(self):
        """Get the number of active subscribers"""
        return len(self.subscribers)
    
    def is_streaming(self):
        """Check if streaming is active"""
        return self.streaming
    
    def get_stream_info(self):
        """Get streaming information"""
        return {
            "streaming": self.streaming,
            "fps": STREAMING_FPS,
            "quality": STREAMING_QUALITY,
            "resolution": f"{STREAMING_WIDTH}x{STREAMING_HEIGHT}",
            "subscribers": len(self.subscribers),
            "has_driver": self.driver is not None
        }
    
    def capture_frame_with_element_highlight(self, element_locator):
        """Capture frame with specific element highlighted"""
        try:
            if not self.driver:
                return None
                
            # Find and highlight element
            element = self.driver.find_element(*element_locator)
            
            # Add highlighting via JavaScript
            self.driver.execute_script(
                "arguments[0].style.border='3px solid red'; arguments[0].style.boxShadow='0 0 10px red';",
                element
            )
            
            # Capture screenshot
            screenshot = self.driver.get_screenshot_as_png()
            frame = self._process_screenshot(screenshot)
            
            # Remove highlighting
            self.driver.execute_script(
                "arguments[0].style.border=''; arguments[0].style.boxShadow='';",
                element
            )
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error capturing frame with highlight: {e}")
            return None


# Global streaming service instance
streaming_service = StreamingService()