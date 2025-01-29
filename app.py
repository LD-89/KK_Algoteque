from flask import Flask, request, jsonify
from calculate_quotes import QuotesCalculator


def create_app(test_config=None):
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)

    if test_config is not None:
        app.config.from_mapping(test_config)

    @app.route("/course_quotes", methods=["POST"])
    def course_quotes():
        """
        Endpoint to calculate course quotes based on provided topics.
        """
        data = request.get_json()

        # Validate the incoming request data
        if not data or 'topics' not in data or not data['topics']:
            return {}

        quotes_calculator = QuotesCalculator()

        # Calculate the quotes
        try:
            quotes = quotes_calculator.calculate_quotes(data['topics'])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify(quotes)

    return app
