
import base64
import requests

from flask import current_app, request, session, redirect, url_for

from app import REDIRECT_URI, SCOPE
from ..api import get_auth_url

AUTH_URL = get_auth_url()
CLIENT_ID = current_app.config['CLIENT_ID']
CLIENT_SECRET = current_app.config['CLIENT_SECRET']

@current_app.route('/')
def login():
    return redirect(AUTH_URL)

@current_app.route('/callback')
def spotify_callback():
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

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }

        response = requests.post(url=AUTH_URL, headers=headers, data=data)

        if response.status_code != 200:
            return f'Failed to retrieve token, status code: {response.status_code}', 500

        access_token_info = response.json()
        access_token = access_token_info['access_token']
        session['access_token'] = access_token

        return redirect(url_for('sorter'))

    return 'No code provided by Spotify', 400