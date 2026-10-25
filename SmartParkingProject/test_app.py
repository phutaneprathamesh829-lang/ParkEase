import unittest
from app import app

class ParkEaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage(self):
        # Test if index route responds with HTTP 200
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        # Test if status API returns valid JSON
        response = self.app.get('/api/status?branch=vashi')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'totalSlots', response.data)

if __name__ == '__main__':
    unittest.main()