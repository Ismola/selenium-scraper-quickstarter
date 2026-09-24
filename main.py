from flask import Flask, jsonify
from controller.controller_sample import controller_sample
from controller.controller_test import controller_test
from utils.handle_request import handle_request_endpoint
from utils.config import MAX_CONTENT_LENGTH, PORT, STAGE, validate_runtime_configuration
from selenium_scraper_runtime import init_metrics, init_request_logging

def create_app():
    validate_runtime_configuration()
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    init_request_logging(app)
    init_metrics(app)

    @app.route('/')
    def index():
        """Root endpoint for health check."""
        return 'selenium-scraper-quickstarter'

    # No borrar para hacer pruebas
    @app.route('/sample', methods=['GET'])
    def sample_endpoint():
        """Sample endpoint demonstrating controller usage."""
        try:
            return handle_request_endpoint(controller_sample)
        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return jsonify(error="An internal error has occurred."), 500

    @app.route('/test', methods=['GET', 'POST'])
    def test_endpoint():
        """
        Endpoint de pruebas completo que valida todos los navegadores y funcionalidades.

        Parámetros (GET/POST):
        - browsers: Lista de navegadores ['chrome', 'firefox'] (default: ambos)
        - test_search: Habilitar pruebas de búsqueda (default: true)
        - test_writes: Habilitar pruebas de escritura (default: true)
        - screenshots: Habilitar capturas de pantalla (default: true)
        - urls: Rutas URL a visitar (default: Google y GitHub)
        """
        try:
            return handle_request_endpoint(controller_test)
        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return jsonify(error="An internal error has occurred."), 500

    # TODO: Add more endpoints here as needed
    return app


# Instancia global para Gunicorn (debe estar fuera del if)
app = create_app()

if __name__ == "__main__":
    port = int(PORT)
    debug = STAGE != 'production' 
    app.run(debug=debug, host='0.0.0.0', port=port)
