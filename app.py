import requests
import urllib.parse
import base64
import colorsys
import math
from PIL import Image
from io import BytesIO
from flask import Flask, redirect, request, render_template, url_for, session, jsonify

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
def download_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)

def get_dominant_color(image, palette_size=16):
    # Resize for efficiency
    image.thumbnail((100, 100))
    paletted = image.convert('P', palette=Image.ADAPTIVE, colors=palette_size)
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]
    return dominant_color

def hsv_color_distance(hsv1, hsv2):
    # Euclidean distance in HSV space
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(hsv1, hsv2)))

# API Getter Methods
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
            print(f'Failed to retrieve data, status code: {response.status_code}')
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

def get_track_info(access_token, playlist_id):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    track_info = {}

    while url:
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to retrieve data, status code: {response.status_code}')
            break

        data = response.json()

        for item in data['items']:
            track_info[item['track']['id']] = item['track']['album']['images'][0]['url']

        url = data.get('next')
    
    return track_info


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


@app.route('/sort_playlist/<playlist_id>')
def sort_playlist(playlist_id):
    access_token = session.get('access_token')
    track_info = get_track_info(access_token, playlist_id)
    
    tracks_with_colors = []

    for track_id, image_url in track_info.items():
        img = download_image(image_url)
        dominant_color = get_dominant_color(img)
        tracks_with_colors.append((track_id, dominant_color))

    # Convert to HSV and sort by hue
    # tracks_with_colors.sort(key=lambda x: rgb_to_hsv(x[1])[0])

    # Choose a starting reference color, for example, the first color in the list
    reference_color = tracks_with_colors[0][1]

    # Sort the tracks based on color distance from the reference color
    tracks_with_colors.sort(key=lambda x: hsv_color_distance(x[1], reference_color))

    # Extract sorted track IDs
    sorted_track_ids = [track[0] for track in tracks_with_colors]

    # replace the tracks with the sorted order
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Convert track IDs to Spotify URI format
    track_uris = [f'spotify:track:{track_id}' for track_id in sorted_track_ids]
    data = {'uris': track_uris}
    
    response = requests.put(url, json=data, headers=headers)

    if response.status_code != 200:
        return jsonify({
            'status': 'error', 
            'message': 'Failed to update playlist',
            'response': response.json()
        })

    return jsonify({'status': 'success', 'message': 'Playlist sorted successfully'})


if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)