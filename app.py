import requests
import urllib.parse
import base64
from flask import Flask, redirect, request, render_template, url_for, session

# Spotify API endpoints
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
AUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
ALL_PLAYLISTS_URL = 'https://api.spotify.com/v1/me/playlists'
USER_INFO_URL = 'https://api.spotify.com/v1/me'

# Client keys
CLIENT_ID = '8717281952454dbd9264dd61b3f49c51'
CLIENT_SECRET = '893e05907bd04cd99455525c3e704aa5'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'

app = Flask(__name__)
app.secret_key = '1234'

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

def get_user_id(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url=USER_INFO_URL, headers=headers)
    user_info = response.json()

    return user_info['id']

def get_owned_playlists(access_token):
    url = ALL_PLAYLISTS_URL
    user_id = get_user_id(access_token)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    owned_playlists_ids = {}

    while url:
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve data, status code: {response.status_code}")
            break

        data = response.json()

        for item in data['items']:
            if item['tracks']['total'] > 0 and item['owner']['id'] == user_id:
                image_url = item['images'][0]['url'] if item['images'] else None

                owned_playlists_ids[item['name']] = {
                    'url': image_url,
                    'id': item['id']
                }

        url = data.get('next')

    return owned_playlists_ids

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
        session['access_token'] = access_token

        return redirect(url_for('sorter'))

    return 'No code provided by Spotify', 400


@app.route('/sorter')
def sorter():
    access_token = session.get('access_token')
    playlists = get_owned_playlists(access_token=access_token)

    return render_template('playlists.html', playlists=playlists)


if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)