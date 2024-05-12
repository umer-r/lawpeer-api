import os
import sys
import unittest
import json

# Add the parent directory of your Flask app to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import create_app
from api.models.admin import Admin
from flask_jwt_extended import create_access_token, JWTManager
from api.utils.token_generator import generate_admin_access_token
from flask import Flask

class TestCreateNewAdmin(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.client.testing = True

        # Create a Flask application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a JWT token with the 'super-admin' role
        self.admin_jwt_token = self.create_jwt_token(1, 'super-admin')
        self.user_jwt_token = self.create_jwt_token(1, 'client')

    def tearDown(self):
        """ Pop the Flask application context after each test """
        self.app_context.pop()

    def create_jwt_token(self, id, role):
        """ Generate a JWT token within the application context """
        jwt_token = create_access_token(identity={'id': id, 'role': role})
        return jwt_token

    def test_01_create_new_admin_success(self): 
        """
            - Send a POST request to create a new admin with valid data
            - Check if the response status code is 200 OK
            - Check if the response contains the new admin's data
        """
        
        data = {'email': 'newadmin@example.com', 'password': 'new_password', 'phone_number': '1234567890'}
        headers = {'Authorization': f'Bearer {self.admin_jwt_token}'}
        response = self.client.post('/api/admin/', json=data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        admin_data = response.json
        self.assertEqual(admin_data['email'], data['email'])
        self.assertEqual(admin_data['phone_number'], data['phone_number'])

    def test_02_create_new_admin_duplicate_email(self):
        """
            - Send a POST request to create a new admin with an existing email
            - Check if the response status code is 409 Conflict
            - Check if the response contains the error message
        """
        
        data = {'email': 'newadmin@example.com', 'password': 'new_password', 'phone_number': '1234567890'}
        headers = {'Authorization': f'Bearer {self.admin_jwt_token}'}
        response = self.client.post('/api/admin/', json=data, headers=headers)
        
        self.assertEqual(response.status_code, 409)
        error_message = response.json['error']
        self.assertEqual(error_message, 'Admin with the same email already exists')
        
    def test_03_create_new_admin_as_user(self):
        """
            - Send a POST request to create a new admin with valid data.
            - Check if the response status code is 403 Unauthorized.
            - Check if the response contains the error message.
        """
        
        data = {'email': 'admin@example.com', 'password': 'new_password', 'phone_number': '1234567890'}
        headers = {'Authorization': f'Bearer {self.user_jwt_token}'}
        response = self.client.post('/api/admin/', json=data, headers=headers)
    
        self.assertEqual(response.status_code, 401)
        error_message = response.json['error']
        self.assertEqual(error_message, 'Unauthorized access. User is not super admin.')

if __name__ == '__main__':
    unittest.main()
