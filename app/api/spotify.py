'''
Module: api.py
Author: Elliot H. Ha
Created on: Dec 27, 2023

Description:
This file provides functions to interact with the Spotify Web API.
It includes functions to authenticate, fetch user data, playlists, and tracks.

Functions:
- get_auth_url(): returns the URL to the Spotify OAuth login page for use in redirecting users on app start
- get_user_info(access_token): returns the profile information of the current logged-in user after authenticating
    https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
- get_owned_playlists(access_token): returns a dict of playlists owned by the user that have at least 1 track in them
    https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
'''

import requests
import urllib.parse

from flask import current_app, session
from app import REDIRECT_URI, SCOPE

CLIENT_ID = current_app.config['CLIENT_ID']
CLIENT_SECRET = current_app.config['CLIENT_SECRET']

# Spotify API endpoints
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
AUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
USER_INFO_URL = 'https://api.spotify.com/v1/me'
USER_PLAYLISTS_URL = 'https://api.spotify.com/v1/me/playlists'

def get_auth_url():
    params = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'client_id': CLIENT_ID
    }

    auth_url = f'{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}'
    return auth_url


def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url=USER_INFO_URL, headers=headers)

    user_info = response.json()
    return user_info


def get_owned_playlists(access_token):
    url = USER_PLAYLISTS_URL
    user_info = get_user_info(access_token)
    user_id = user_info['id']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Key = Name of the playlist
    # Value = Dict of the playlist_id, image_url, and number of tracks mapped to their respective values
    owned_playlists = {}

    while url:
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to retrieve data, status code: {response.status_code}')
            break

        playlist_data = response.json()

        for playlist in playlist_data['items']:
            num_tracks = playlist['tracks']['total']

            # If the playlist is owned by the user and has at least 1 track in it, add to owned_playlists
            if playlist['owner']['id'] == user_id and num_tracks > 0:
                image_url = playlist['images'][0]['url'] if playlist['images'] else None

                owned_playlists[playlist['name']] = {
                    'playlist_id': playlist['id'],
                    'image_url': image_url,
                    'num_tracks': num_tracks
                }

        # Updates the URL of the request to next page of playlist data due to Spotify's request limits
        url = playlist_data.get('next')

    return owned_playlists


def get_track_info(access_token, playlist_id):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    track_info = {}
    not_in = 0
    in_count = 0

    while url:
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to retrieve data, status code: {response.status_code}')
            break

        data = response.json()
        print(f'HOW MANY TRACKS HERE: {len(data["items"])}')

        for item in data['items']:
            track_id = item['track']['id']
            image_url = item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else None
            if track_id not in track_info:
                not_in += 1
            else:
                in_count += 1

            track_info[track_id] = image_url

        url = data.get('next')
        print(f'NOT IN COUNT: {not_in}, IN COUNT: {in_count}')
        print(f'NEXT URL IS {url}')
    
    return track_info