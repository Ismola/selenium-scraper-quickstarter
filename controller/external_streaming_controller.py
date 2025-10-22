import logging
from flask import jsonify
from utils.external_streaming_service import external_streaming_service
from actions.web_driver import get_page, close_driver
from utils.config import EXTERNAL_STREAMING_ENABLED


def start_external_streaming_controller(url=None, browser='chrome', streaming_config=None):
    """
    Controller to start external streaming of browser automation

    Args:
        url (str): URL to navigate to (optional)
        browser (str): Browser type ('chrome' or 'firefox')
        streaming_config (dict): External streaming configuration

    Returns:
        dict: Response with streaming status and info
    """
    try:
        if streaming_config is None:
            streaming_config = {}

        if external_streaming_service.is_streaming():
            return {
                "success": False,
                "message": "External streaming is already active",
                "info": external_streaming_service.get_stream_info()
            }

        # Create new driver instance for streaming
        driver = get_page(browser=browser, url=url)

        if not driver:
            return {
                "success": False,
                "message": "Failed to create browser driver",
                "error": "DRIVER_CREATION_FAILED"
            }

        # Set driver for streaming service
        external_streaming_service.set_driver(driver)

        # Start streaming
        success = external_streaming_service.start_streaming(streaming_config)

        if success:
            logging.info(
                f"External streaming started successfully for URL: {url}")
            return {
                "success": True,
                "message": "External streaming started successfully",
                "info": external_streaming_service.get_stream_info(),
                "config": streaming_config
            }
        else:
            close_driver(driver)
            return {
                "success": False,
                "message": "Failed to start external streaming",
                "error": "STREAMING_START_FAILED"
            }

    except Exception as e:
        logging.error(f"Error starting external streaming: {e}")
        return {
            "success": False,
            "message": f"Error starting external streaming: {str(e)}",
            "error": "INTERNAL_ERROR"
        }


def stop_external_streaming_controller():
    """
    Controller to stop external streaming

    Returns:
        dict: Response with operation status
    """
    try:
        if not external_streaming_service.is_streaming():
            return {
                "success": False,
                "message": "No active external streaming session",
                "error": "NO_ACTIVE_STREAM"
            }

        # Stop streaming
        external_streaming_service.stop_streaming()

        # Close driver if exists
        if external_streaming_service.driver:
            close_driver(external_streaming_service.driver)
            external_streaming_service.driver = None

        logging.info("External streaming stopped successfully")
        return {
            "success": True,
            "message": "External streaming stopped successfully"
        }

    except Exception as e:
        logging.error(f"Error stopping external streaming: {e}")
        return {
            "success": False,
            "message": f"Error stopping external streaming: {str(e)}",
            "error": "INTERNAL_ERROR"
        }


def get_external_streaming_status_controller():
    """
    Controller to get current external streaming status

    Returns:
        dict: Current streaming status and information
    """
    try:
        return {
            "success": True,
            "external_streaming_enabled": EXTERNAL_STREAMING_ENABLED,
            "info": external_streaming_service.get_stream_info()
        }

    except Exception as e:
        logging.error(f"Error getting external streaming status: {e}")
        return {
            "success": False,
            "message": f"Error getting external streaming status: {str(e)}",
            "error": "INTERNAL_ERROR"
        }


def navigate_external_streaming_controller(url):
    """
    Controller to navigate to a new URL during external streaming

    Args:
        url (str): URL to navigate to

    Returns:
        dict: Response with navigation status
    """
    try:
        if not external_streaming_service.is_streaming():
            return {
                "success": False,
                "message": "No active external streaming session",
                "error": "NO_ACTIVE_STREAM"
            }

        if not external_streaming_service.driver:
            return {
                "success": False,
                "message": "No driver available",
                "error": "NO_DRIVER"
            }

        # Navigate to new URL
        external_streaming_service.driver.get(url)

        logging.info(f"Navigated to: {url}")
        return {
            "success": True,
            "message": f"Successfully navigated to {url}",
            "current_url": external_streaming_service.driver.current_url
        }

    except Exception as e:
        logging.error(f"Error navigating during external streaming: {e}")
        return {
            "success": False,
            "message": f"Error navigating: {str(e)}",
            "error": "NAVIGATION_ERROR"
        }


def execute_external_streaming_action_controller(action_type, **kwargs):
    """
    Controller to execute actions during external streaming

    Args:
        action_type (str): Type of action ('click', 'type', 'scroll', etc.)
        **kwargs: Action-specific parameters

    Returns:
        dict: Response with action execution status
    """
    try:
        if not external_streaming_service.is_streaming():
            return {
                "success": False,
                "message": "No active external streaming session",
                "error": "NO_ACTIVE_STREAM"
            }

        if not external_streaming_service.driver:
            return {
                "success": False,
                "message": "No driver available",
                "error": "NO_DRIVER"
            }

        driver = external_streaming_service.driver

        if action_type == "click":
            from selenium.webdriver.common.by import By
            locator = kwargs.get('locator')
            value = kwargs.get('value')

            if locator and value:
                element = driver.find_element(
                    getattr(By, locator.upper()), value)
                element.click()

        elif action_type == "type":
            from selenium.webdriver.common.by import By
            locator = kwargs.get('locator')
            value = kwargs.get('value')
            text = kwargs.get('text', '')

            if locator and value:
                element = driver.find_element(
                    getattr(By, locator.upper()), value)
                element.clear()
                element.send_keys(text)

        elif action_type == "scroll":
            x = kwargs.get('x', 0)
            y = kwargs.get('y', 500)
            driver.execute_script(f"window.scrollBy({x}, {y});")

        elif action_type == "execute_script":
            script = kwargs.get('script', '')
            if script:
                result = driver.execute_script(script)
                return {
                    "success": True,
                    "message": "Script executed successfully",
                    "result": result
                }

        logging.info(f"Executed action: {action_type}")
        return {
            "success": True,
            "message": f"Action '{action_type}' executed successfully"
        }

    except Exception as e:
        logging.error(f"Error executing action during external streaming: {e}")
        return {
            "success": False,
            "message": f"Error executing action: {str(e)}",
            "error": "ACTION_EXECUTION_ERROR"
        }


def update_streaming_config_controller(config):
    """
    Controller to update streaming configuration on the fly

    Args:
        config (dict): New streaming configuration

    Returns:
        dict: Response with update status
    """
    try:
        external_streaming_service.update_streaming_config(config)

        logging.info("External streaming configuration updated")
        return {
            "success": True,
            "message": "Streaming configuration updated successfully",
            "info": external_streaming_service.get_stream_info()
        }

    except Exception as e:
        logging.error(f"Error updating streaming configuration: {e}")
        return {
            "success": False,
            "message": f"Error updating configuration: {str(e)}",
            "error": "CONFIG_UPDATE_ERROR"
        }
