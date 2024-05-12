import os
import sys
import unittest
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import create_app
from flask_jwt_extended import create_access_token
from flask import Flask

class TestChangeUserPassword(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.client.testing = True

        # Create a Flask application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a JWT token with a mock user ID
        self.jwt_token = self.create_jwt_token(user_id=2, user_role='client')

    def tearDown(self):
        """ Pop the Flask application context after each test """
        self.app_context.pop()

    def create_jwt_token(self, user_id, user_role):
        """ Generate a JWT token within the application context """
        jwt_token = create_access_token(identity={"id":user_id, "role": user_role})
        return jwt_token

    def test_01_change_user_password_success(self):
        """
            - Send a POST request to change user password endpoint
            - Check if the response status code is 200 OK
            - Check if the response contains the success message
        """

        data = {'old_password': 'client1234', 'new_password': 'umer1234'}
        
        headers = {'Authorization': f'Bearer {self.jwt_token}'}
        response = self.client.post('/api/users/change-password/2', json=data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Password change operation for User with id 2 successful!')

    def test_02_change_user_password_invalid_previous_password(self):
        """
            - Send a POST request to change user password endpoint with invalid previous password
            - Check if the response status code is 400 Bad Request
            - Check if the response contains the error message
        """
        
        data = {'old_password': 'invalid_password', 'new_password': 'new_password'}
        
        headers = {'Authorization': f'Bearer {self.jwt_token}'}
        response = self.client.post('/api/users/change-password/2', json=data, headers=headers)
        
        self.assertEqual(response.status_code, 400)
        
        response_data = response.json
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'New password and previous password do not match!')

if __name__ == '__main__':
    unittest.main()
