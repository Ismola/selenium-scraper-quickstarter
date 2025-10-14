import os
from flask import Flask, jsonify
from controller.controller_sample import controller_sample
from utils.handle_request import handle_request_endpoint
from utils.config import STAGE

def create_app():

    app = Flask(__name__)

    @app.route('/')
    def index():
        """Root endpoint for health check."""
        return 'selenium-scraper-quickstarter'

    # TODO: modify this endpoint to implement the desired logic
    @app.route('/sample', methods=['GET'])
    def sample_endpoint():
        """Sample endpoint demonstrating controller usage."""
        try:
            return handle_request_endpoint(controller_sample)
        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return jsonify(error="An internal error has occurred."), 500

    # Add more endpoints here as needed
    return app

# Instancia global para Gunicorn (debe estar fuera del if)
app = create_app()

if __name__ == "__main__":
    debug_mode = STAGE != "production"
    port = int(os.getenv("PORT", 3000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
