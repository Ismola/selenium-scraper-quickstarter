
import inspect
import logging
from actions.login import login
from actions.web_driver import close_driver, get_page
from utils.error import messageError


def controller_sample(data):

    try:
        username = data['username']
        password = data['password']

    except KeyError as e:
        raise messageError(f"The field '{e.args[0]}' has not been sent")
    try:
        message = "ok"

        logging.info("|| Get initial page")
        # You can choose betwen Chrome (default ) or firefox. Example: get_page('firefox')
        driver = get_page()

        # TODO: decominate to use login
        logging.info("|| Init Login")
        # driver = login(driver, username, password)

        # Add actions here - customize for your use case

        return message

    except Exception as e:
        raise messageError(
            f"Error {inspect.currentframe().f_code.co_name}: {e}")

    finally:
        close_driver(driver)
