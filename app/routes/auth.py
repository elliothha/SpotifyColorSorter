'''
Module: routes
Author: Elliot H. Ha
Created on: Dec 27, 2023

Description:
This file provides Flask routes to interact with the Spotify OAuth 2.0 Workflow.
It includes routes for app startup, as well as handling the Spotify callback.

Routes:
- @auth_bp.route('/'): On app startup, redirects client to the Spotify login authorization URL

- @auth_bp.route('/callback'): This route handles the callback redirection upon successful login
'''

import base64
import requests

from flask import current_app, Blueprint, request, session, redirect, url_for

from app import REDIRECT_URI
from ..api.spotify import get_auth_url

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login():
    AUTH_URL = get_auth_url()
    return redirect(AUTH_URL)

@auth_bp.route('/callback')
def spotify_callback():
    CLIENT_ID = current_app.config['CLIENT_ID']
    CLIENT_SECRET = current_app.config['CLIENT_SECRET']

    error = request.args.get('error')
    code = request.args.get('code')

    if error:
        return f'Error: {error}', 400

    if code:
        combined = f'{CLIENT_ID}:{CLIENT_SECRET}'
        b64combined = base64.b64encode(combined.encode()).decode()

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {b64combined}'
        }

        token_url = 'https://accounts.spotify.com/api/token'

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }

        response = requests.post(url=token_url, headers=headers, data=data)

        if response.status_code != 200:
            return f'Failed to retrieve token, status code: {response.status_code}', 500

        access_token_info = response.json()
        access_token = access_token_info['access_token']
        session['access_token'] = access_token

        return redirect(url_for('sorting.sorter'))

    return 'No code provided by Spotify', 400