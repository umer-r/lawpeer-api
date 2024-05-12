import os
import sys
import unittest

# Add the parent directory of your Flask app to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import create_app

class TestAdminLogin(unittest.TestCase):

    def setUp(self):
        app = create_app()
        self.client = app.test_client()
        self.client.testing = True

    def test_01_login_with_valid_credentials(self):
        """
            - Send Post request with correct credentials.
            - Check if status code is 200.
            - Check if reponse contains access_token.
        """
        
        response = self.client.post('/api/admin/login', json={'email': 'superadmin@example.com', 'password': 'superadminpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_02_login_with_invalid_credentials(self):
        """
            - Send Post request with correct credentials.
            - Check if status code is 200.
            - Check if reponse contains access_token.
        """
        
        response = self.client.post('/api/admin/login', json={'email': 'admin@example.com', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Invalid credentials')

if __name__ == '__main__':
    unittest.main()
