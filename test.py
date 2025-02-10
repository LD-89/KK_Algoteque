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

    def test_course_quotes__no_topics(self):
        """
        Test the /course_quotes endpoint with empty topics data.
        """
        request_data = {
            "topics": {}
        }
        expected_result = {'error': 'Request Missing required fields'}

        response = self.app.post(
            '/course_quotes',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), expected_result)

    def test_course_quotes__invalid_json(self):
        """
        Test the /course_quotes endpoint with non-json request data.
        """
        # Test invalid format
        response = self.app.post(
            '/course_quotes',
            data="invalid format",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", json.loads(response.data))

        # Test invalid Content-Type
        response = self.app.post(
            '/course_quotes',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
