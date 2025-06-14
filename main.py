from utils.config import STAGE
# Imports from external libraries
import ssl
# Flask imports and their extensions
from flask import Flask
# Imports of own modules
from controller.controller_sample import controller_sample
from utils.handle_request import handle_request_endpoint

app = Flask(__name__)


@app.route('/')
def index():
    return 'selenium-scraper-quickstarter'

# TODO modify this endpoint to do what is needed


@app.route('/sample', methods=['GET'])
def sample_endpoint():
    return handle_request_endpoint(controller_sample)

# Add more endpoint


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
