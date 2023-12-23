import requests
import urllib.parse
import base64
from flask import Flask, redirect, request

# Spotify API endpoints
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
AUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Client keys
CLIENT_ID = '8717281952454dbd9264dd61b3f49c51'
CLIENT_SECRET = '893e05907bd04cd99455525c3e704aa5'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'

app = Flask(__name__)

# Helper Methods
def get_auth_url():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }

    url = f'{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}'
    return url

# Routes
@app.route('/')
def login():
    auth_query_parameters = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'client_id': CLIENT_ID
    }

    url_args = '&'.join(['{}={}'.format(key, urllib.parse.quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = '{}/?{}'.format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route('/callback')
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

        response = requests.post(url=AUTH_TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            return f'Failed to retrieve token, status code: {response.status_code}', 500

        access_token_info = response.json()
        access_token = access_token_info['access_token']

        # Use the access token to access Spotify API or save it for later use
        # ...

        return f'Authentication successful! You may close this browser now.'

    return 'No code provided by Spotify', 400

if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)