import os
import logging

from flask import Flask, request, jsonify
from calculate_quotes import QuotesCalculator
from werkzeug.exceptions import BadRequest
from logging.handlers import RotatingFileHandler
from logging import Formatter


def create_app(test_config=None):
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)

    # Logging configuration
    if not app.debug and not app.testing:
        configure_logging(app)

    if test_config is not None:
        app.config.from_mapping(test_config)

    register_endpoints(app)
    return app


def configure_logging(app):
    os.makedirs('logs', exist_ok=True)

    log_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024 * 10,  # 10MB per file
        backupCount=5,
        encoding='utf-8'
    )
    log_format = (
        '[%(asctime)s] %(levelname)s %(process)d '
        '%(module)s:%(lineno)d - %(message)s'
    )

    log_handler.setFormatter(Formatter(log_format))
    log_handler.setLevel(logging.INFO)

    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)


def register_endpoints(app):
    @app.route("/course_quotes", methods=["POST"])
    def course_quotes():
        """
        Endpoint to calculate course quotes based on provided topics.
        """
        try:
            data = request.get_json()
            # Validate the incoming request data
            if data is None:
                app.logger.warning(f"Empty request. Sender: {request.remote_addr}")
                return jsonify({"error": "Request is empty"}), 400
            if 'topics' not in data or not data['topics']:
                app.logger.warning(f"Missing required data. Sender: {request.remote_addr},")
                return jsonify({"error": "Request Missing required fields"}), 400
        except BadRequest as e:
            app.logger.error(f"JSON parsing error. Sender: {request.remote_addr}, Content-Type: {request.headers['Content-Type']}", exc_info=True)
            return jsonify({
                "error": "Invalid JSON",
                "detail": e.description
            }), 400

        # Initialize the service
        try:
            quotes_calculator = QuotesCalculator()
        except Exception as e:
            app.logger.critical(
                "Failed to initialize QuotesCalculator - "
                f"Environment: {os.environ.get('FLASK_ENV', 'development')}, "
                f"Error: {str(e)}",
                exc_info=True
            )
            return jsonify({"error": "Service unavailable"}), 503

        # Calculate the quotes
        try:
            quotes = quotes_calculator.calculate_quotes(data['topics'])
        except Exception as e:
            app.logger.critical(
                "Failed to calculate Quotes - "
                f"Environment: {os.environ.get('FLASK_ENV', 'development')}, "
                f"Error: {str(e)}",
                exc_info=True
            )
            return jsonify({"error": str(e)}), 500

        return jsonify(quotes)