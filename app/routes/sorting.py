'''
Module: routes
Author: Elliot H. Ha
Created on: Dec 27, 2023

Description:
This file provides functions and routes to handle the main sorting logic for Spotify playlists.
It interacts with both the Spotify API as well as data to/from the rendered HTML template.

Functions:
- chunk_list(lst, chunk_size): This function helps handles Spotify's pagination limit of 100 tracks.
If there is a playlist ('lst') with more than 100 tracks, it returns a list of lists of the 
playlist tracks broken up into "chunks" of size 'chunk_size' (default=100).

Routes:
- @sorting_bp.route('/sorter'): This route is called at the end of the @auth_bp.route('/callback')
route. It renders the playlist.html template with all of the user's playlist data
- @sorting_bp.route('/sort_playlist/<playlist_id>'): This route is called whenever the user clicks
on the "sort" button for any of the playlists rendered in the playlist.html template. 
It contains the MAIN SORTING LOGIC for the actual sorting of the playlist tracks.
'''

import requests
import time

from flask import Blueprint, session, render_template, jsonify

from ..api.spotify import get_user_info, get_track_info, get_owned_playlists
from ..utils.image_processing import download_image, get_dominant_color, rgb_to_lab, lab_color_distance

sorting_bp = Blueprint('sorting', __name__)

def chunk_list(lst, chunk_size=100):
    '''Yield successive chunk_size chunks from lst.'''
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

@sorting_bp.route('/sorter')
def sorter():
    access_token = session.get('access_token')
    user_info = get_user_info(access_token)
    playlists = get_owned_playlists(access_token)

    return render_template('playlists.html', user_name=user_info['display_name'], playlists=playlists)

@sorting_bp.route('/sort_playlist/<playlist_id>')
def sort_playlist(playlist_id):
    print(f'Successfully started sorting route for {playlist_id}')

    access_token = session.get('access_token')
    track_info = get_track_info(access_token, playlist_id)
    print(f'LENGTH OF TRACK_INFO: {len(track_info)}')
    
    tracks_with_colors = []

    for track_id, image_url in track_info.items():
        img = download_image(image_url)
        dominant_color = get_dominant_color(img)
        # print(f'DOMINANT COLOR: {dominant_color}')
        tracks_with_colors.append((track_id, rgb_to_lab(dominant_color)))

    print('Successfully obtained tracks with colors from playlist')
    print(f'LENGTH OF TRACKS_WITH_COLORS): {len(tracks_with_colors)}')

    # Choose a starting reference color, for example, the first color in the list
    reference_color = tracks_with_colors[0][1]

    # Sort the tracks based on color distance from the reference color
    tracks_with_colors.sort(key=lambda x: lab_color_distance(x[1], reference_color))
    print('Successfully implemented sorting algorithm')

    # Extract sorted track IDs
    sorted_track_ids = [track[0] for track in tracks_with_colors]
    print(f'LENGTH OF SORTED_TRACK_IDS: {len(sorted_track_ids)}')

    # replace the tracks with the sorted order
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    clear_data = {'uris': []}
    clear_response = requests.put(url=url, json=clear_data, headers=headers)

    if clear_response.status_code not in [200, 201]:
        print(f'Error clearing playlist: {clear_response.json()}')
        return jsonify({
            'status': 'error',
            'message': 'Failed to clear playlist',
            'response': clear_response.json()
        })

    # Convert track IDs to Spotify URI format
    track_uris = [f'spotify:track:{track_id}' for track_id in sorted_track_ids]
    print(f'LENGTH OF TRACK_URIS: {len(track_uris)}')
    # Split track URIs into chunks of 100
    track_uri_chunks = list(chunk_list(track_uris, 100))
    print(track_uri_chunks)
    
    if len(track_uri_chunks) == 1:
        data = {'uris': track_uri_chunks[0]}
        response = requests.put(url=url, json=data, headers=headers)
    else:
        # Loop through each chunk and update the playlist
        for i, chunk in enumerate(track_uri_chunks):
            data = {'uris': chunk}
            response = requests.post(url=url, json=data, headers=headers)
            print(f'Chunk: {i}, Total tracks: {len(chunk)}, Response code: {response.status_code}, Response body: {response.json()}')

            if response.status_code not in [200, 201]:
                print(f'Error updating playlist: {response.json()}')
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to update playlist',
                    'response': response.json()
                })

            # sleep to avoid hitting rate limits
            time.sleep(0.1)

    print('Successfully finished sorting')

    return jsonify({'status': 'success', 'message': 'Playlist sorted successfully'})