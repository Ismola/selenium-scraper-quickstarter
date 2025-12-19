import inspect
import logging
from actions.web_driver import get_wait
from utils.error import messageError
from selenium.webdriver.support import expected_conditions

# This function searches for an element on the page, scrolls to it, and click to it.


def search_element(driver, locator, wait_to_search=True, raise_exception=True):

    # locator  example: driver, (By.XPATH, "//span[contains(@class, 'x-menu-item-text') and contains(text(), '{}')]".format(xpath))
    logging.info('- Searching {}'.format(locator))
    wait = get_wait(driver)
    try:
        if wait_to_search:
            element = wait.until(lambda d:
                        # expected_conditions.presence_of_element_located(locator)(d) or
                        expected_conditions.element_to_be_clickable(locator)(d) or
                        expected_conditions.visibility_of_element_located(
                            locator)(d)
                        )
        else:
            element = driver.find_element(*locator)
        return element
    except Exception as e:
        if raise_exception:
            # Get information from the function that called Search_element
            caller = inspect.stack()[1]
            error_message = (
                f"Error in function '{caller.function}' at {caller.filename}:{caller.lineno} - "
                f"Failed to locate element {locator}: {str(e)}"
            )
            raise messageError(error_message)
        else:
            pass
