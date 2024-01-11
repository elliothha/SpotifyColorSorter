'''
Module: tests
Author: Elliot H. Ha
Created on: Jan 7, 2023

Description:
This file provides unit tests for testing the Flask routes in routes/auth.py

Functions:
- setUp(self): Creates a new Flask app instance for testing and pushes the app context

- tearDown(self): Deconstructs the test application context

- test_login_route(self): Tests the default '/' route set to the login logic
Successful test on successful redirection with correct URL

- test_callback_route_with_error(self): 
Tests the callback route when an error parameter is provided
Successful test on returned 400 response and correct error handling

- test_callback_route_with_token_success(self, mock_post):
Tests the callback route when a valid code is provided and a token is successfully returned
Successful test on valid access token return and successful redirection to correct URL

- test_callback_route_with_token_failure(self, mock_post):
Tests the callback route when a valid code is provided and a token is unsuccessfully returned
Successful test on failed token return response code 500 and correct error handling

- test_callback_route_without_code_or_error(self):
Tests the callback route when a valid code nor error is provided
Successful test on response code 400 for this scenario and correct error handling
'''

import unittest
import urllib.parse
from unittest.mock import patch

from flask import Flask, session
from app import REDIRECT_URI, SCOPE, create_app

class TestAuthRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['SECRET_KEY'] = 'dummy_secret_key'
        self.app.config['CLIENT_ID'] = 'dummy_client_id'
        self.app.config['CLIENT_SECRET'] = 'dummy_client_secret'
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.maxDiff = None
    
    def tearDown(self):
        self.ctx.pop()
    
    def test_login_route(self):
        # Makes a GET request to the '/' home login route
        response = self.client.get('/')

        expected_params = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'client_id': 'dummy_client_id'
        }
        expected_url = f'https://accounts.spotify.com/authorize?{urllib.parse.urlencode(expected_params)}'

        # Asserts that the status code returned from home route is 302 (redirect)
        self.assertEqual(response.status_code, 302)
        
        # Asserts that the redirect URL is the expected Auth URL
        self.assertEqual(response.headers['Location'], expected_url)
    
    def test_callback_route_with_error(self):
        response = self.client.get('/callback?error=dummy_error')

        # Asserts that the status code returned from a callback error is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Asserts that the returned response correctly gives the expected error message
        self.assertIn('Error: dummy_error', response.data.decode())
    
    @patch('app.routes.auth.requests.post')
    def test_callback_route_with_token_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'dummy_access_token'}

        with self.app.test_client() as client:
            response = client.get('callback?code=dummy_code')

            # Asserts that an access token is returned correctly
            self.assertEqual(session.get('access_token'), 'dummy_access_token')

        # Asserts that the status code returned from successful token retrieval is 302
        self.assertEqual(response.status_code, 302)

        # Asserts that the redirection is to the correct sorting route
        self.assertTrue('Location' in response.headers)
        self.assertTrue('sorter' in response.headers['Location'])
    
    @patch('app.routes.auth.requests.post')
    def test_callback_route_with_token_failure(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 500

        response = self.client.get('callback?code=dummy_code')

        # Asserts that the status code returned from failed token retrieval is 500
        self.assertEqual(response.status_code, 500)

        # Asserts that the returned response correctly gives the expected error message
        self.assertIn('Failed to retrieve token', response.data.decode())
    
    def test_callback_route_without_code_or_error(self):
        response = self.client.get('callback')

        # Asserts that the status code returned from response returning neither option is 400
        self.assertEqual(response.status_code, 400)

        # Asserts that the returned response correctly gives the expected error message
        self.assertIn('No code provided by Spotify', response.data.decode())

    
if __name__ == '__main__':
    unittest.main()