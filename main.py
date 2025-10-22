import os
from flask import Flask, jsonify, request
from controller.controller_sample import controller_sample
from utils.handle_request import handle_request_endpoint
from utils.config import STAGE
from actions.web_driver import get_streaming_status, stop_streaming


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY', 'selenium-scraper-quickstarter')

    @app.route('/')
    def index():
        """Root endpoint for health check."""
        return 'selenium-scraper-quickstarter with auto-streaming support'

    @app.route('/sample', methods=['GET'])
    def sample_endpoint():
        """Sample endpoint demonstrating controller usage."""
        try:
            return handle_request_endpoint(controller_sample)
        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return jsonify(error="An internal error has occurred."), 500

    @app.route('/stream/status', methods=['GET'])
    def streaming_status():
        """Get current streaming status."""
        return jsonify(get_streaming_status())

    @app.route('/stream/stop', methods=['POST'])
    def stop_stream():
        """Stop current streaming."""
        return jsonify(stop_streaming())

    # Add more endpoints here as needed
    return app


# Instancia global para Gunicorn (debe estar fuera del if)
app = create_app()

if __name__ == "__main__":
    debug_mode = STAGE != "production"
    port = int(os.getenv("PORT", 3000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
