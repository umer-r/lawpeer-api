import os
import sys
import unittest
import json

# Add the parent directory of your Flask app to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import create_app
from flask import Flask

class TestUserLogin(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.client.testing = True

        # Create a Flask application context
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Pop the Flask application context after each test
        self.app_context.pop()

    def test_user_login_success(self):
        # Mock user credentials
        user_email = 'russs3400@gmail.com'
        user_password = 'client1234'

        # Mock request data
        data = {'email': user_email, 'password': user_password}

        # Send a POST request to user login endpoint
        response = self.client.post('/api/users/login', json=data)
        
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the access token
        response_data = response.json
        self.assertIn('access_token', response_data)

    def test_user_login_invalid_credentials(self):
        # Mock user credentials with invalid password
        user_email = 'user@example.com'
        invalid_password = 'wrong_password'

        # Mock request data
        data = {'email': user_email, 'password': invalid_password}

        # Send a POST request to user login endpoint with invalid credentials
        response = self.client.post('/api/users/login', json=data)
        
        # Check if the response status code is 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        
        # Check if the response contains the error message
        response_data = response.json
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Invalid credentials')

if __name__ == '__main__':
    unittest.main()
