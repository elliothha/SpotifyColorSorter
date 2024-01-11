'''
Module: tests
Author: Elliot H. Ha
Created on: Jan 7, 2023

Description:
This file provides unit tests for testing the interaction with the Spotify API

Functions:
- setUp(self): Creates a new Flask app instance for testing and pushes the app context

- tearDown(self): Deconstructs the test application context

- test_get_auth_url(self): Tests the get_auth_url() function
Successful test on proper URL formation

- test_get_user_info(self, mock_get): Tests the get_user_info() function
Successful test on returned response matching mock_response with mock user data
'''

import unittest
import urllib.parse
from unittest.mock import patch

from app import REDIRECT_URI, SCOPE, create_app
from app.api.spotify import get_auth_url, get_user_info

class TestAPIInteraction(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['CLIENT_ID'] = 'dummy_client_id'
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.maxDiff = None
    
    def tearDown(self):
        self.ctx.pop()

    def test_get_auth_url(self):
        # Testing against this correctly formatted expected URL
        expected_params = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'client_id': 'dummy_client_id'
        }
        expected_url = f'https://accounts.spotify.com/authorize?{urllib.parse.urlencode(expected_params)}'
            
        # Call the function to get auth URL
        auth_url = get_auth_url()

        # Asserts that the URL is formed correctly
        self.assertEqual(auth_url, expected_url)

    @patch('app.api.spotify.requests.get')
    def test_get_user_info(self, mock_get):
        # The mock get response will return a response with an OK status code and mock data
        mock_response = {
            'id': '1234',
            'display_name': 'Test User',
            'email': 'testuser@example.com'
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Makes the actual call to the function with a dummy access token
        access_token = 'dummy_access_token'
        response = get_user_info(access_token)

        # Asserts that the returned response from get_user_info() matches the mock response
        self.assertEqual(response, mock_response)

        # Asserts that the response from get_user_info() was called with the proper URL and headers
        mock_get.assert_called_with(
            url='https://api.spotify.com/v1/me', 
            headers={'Authorization': f'Bearer {access_token}'}
        )


if __name__ == '__main__':
    unittest.main()
