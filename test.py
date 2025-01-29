import json
import unittest

from app import create_app


class TestCourseQuotes(unittest.TestCase):
    def setUp(self):
        """
        Set up the test client before each test.
        """
        self.app = create_app({'TESTING': True}).test_client()

    def test_course_quotes(self):
        """
        Test the /course_quotes endpoint with valid topics data.
        """
        request_data = {
            "topics": {
                "reading": 20,
                "math": 50,
                "science": 30,
                "history": 15,
                "art": 10
            }
        }
        expected_result = {
            "provider_a": 8,
            "provider_b": 5,
            "provider_c": 10,
        }

        response = self.app.post(
            '/course_quotes',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected_result)

    def test_course_quotes_no_topics(self):
        """
        Test the /course_quotes endpoint with empty topics data.
        """
        request_data = {
            "topics": {}
        }
        expected_result = {}

        response = self.app.post(
            '/course_quotes',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected_result)


if __name__ == '__main__':
    unittest.main()
