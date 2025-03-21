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
    if STAGE == "production":
        # You can change that using nginx and Gunicorn
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain("./certs/cert.pem", "./certs/private.pem")
        app.run(debug=False, host='0.0.0.0', port=3000, ssl_context=context)
    else:
        app.run(debug=True, host='0.0.0.0', port=3000)
