import json
import logging

logger = logging.getLogger(__name__)
SINGLE_TOPIC_PRICING_VALUES = {
    0: 20,
    1: 25,
    2: 30,
}


class QuotesCalculator:
    def __init__(self):
        """
        Initialize the QuotesCalculator with providers data from a JSON file.
        """
        try:
            with open('static/providers.json') as f:
                self.providers_data = json.load(f)

            if not isinstance(self.providers_data, dict) or 'provider_topics' not in self.providers_data:
                raise ValueError("Invalid providers.json contents")

        except FileNotFoundError as e:
            logger.critical("File missing: static/providers.json")
            raise RuntimeError("Service initialization error") from e
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON file: static/providers.jso", exc_info=True)
            raise ValueError("Invalid JSON format file") from e
        except Exception as e:
            logger.error("Unexpected error", exc_info=True)
            raise

    def _compare_topics(self, topics: str, top_topics: list):
        """
        Compare provider topics with top topics.

        Args:
            topics (str): Provider topics as a string.
            top_topics (list): List of top topics.

        Returns:
            tuple: Count of matching topics and the matching topics set.
        """
        provider_topics = topics.split('+')
        matching_topics = set(top_topics) & set(provider_topics)
        count = len(matching_topics)
        return count, matching_topics

    def _single_match_calculation(self, matching_topics: set, top_topics: list, topics_requested: dict):
        """
        Calculate quote for a single matching topic.

        Args:
            matching_topics (set): Set of matching topics.
            top_topics (list): List of top topics.
            topics_requested (dict): Requested topics with values.

        Returns:
            float: Calculated quote.
        """
        topic = next(iter(matching_topics))
        position = top_topics.index(topic)
        pricing_value = SINGLE_TOPIC_PRICING_VALUES[position]
        requested_topic_value = topics_requested[topic]
        return requested_topic_value * pricing_value / 100

    def _double_match_calculation(self, matching_topics: set, topics_requested: dict):
        """
        Calculate quote for double matching topics.

        Args:
            matching_topics (set): Set of matching topics.
            topics_requested (dict): Requested topics with values.

        Returns:
            float: Calculated quote.
        """
        quote = 0
        pricing_value = 10
        for topic in matching_topics:
            requested_topic_value = topics_requested[topic]
            quote += requested_topic_value * pricing_value / 100
        return quote

    def _get_quotes_for_provider(self, topics: str, top_topics: list, topics_requested: dict):
        """
        Get quotes for a provider based on the requested topics.

        Args:
            topics (str): Provider topics as a string.
            top_topics (list): List of top topics.
            topics_requested (dict): Requested topics with values.

        Returns:
            float: Calculated quote.
        """
        count, matching_topics = self._compare_topics(topics, top_topics)
        if count == 0:
            return 0
        elif count == 1:
            return self._single_match_calculation(matching_topics, top_topics, topics_requested)
        elif count == 2:
            return self._double_match_calculation(matching_topics, topics_requested)

    def calculate_quotes(self, topics_requested: dict):
        """
        Calculate quotes for all providers based on the requested topics.

        Args:
            topics_requested (dict): Requested topics with values.

        Returns:
            dict: Quotes for each provider.
        """
        sorted_topics = dict(sorted(topics_requested.items(), key=lambda item: item[1], reverse=True))
        top_topics = list(sorted_topics.keys())[:3]
        quotes = {}

        for provider, topics in self.providers_data['provider_topics'].items():
            quote_value = self._get_quotes_for_provider(topics, top_topics, topics_requested)
            if quote_value:
                quotes[provider] = int(quote_value) if quote_value.is_integer() else quote_value

        return quotes
