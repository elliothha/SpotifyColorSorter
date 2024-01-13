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

import time
import requests
import numpy as np

from flask import Blueprint, session, render_template, jsonify

from ..api.spotify import get_user_info, get_track_info, get_owned_playlists
from ..utils.image_processing import download_image, get_dominant_colors, rgb_to_lab, lab_color_distance

sorting_bp = Blueprint('sorting', __name__)

def chunk_list(lst, chunk_size=100):
    '''Yield successive chunk_size chunks from lst.'''
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def sort_tracks(access_token, playlist_id):
    track_info = get_track_info(access_token, playlist_id)
    
    tracks_with_colors = []

    for track_id, image_url in track_info.items():
        img = download_image(image_url)
        top_rgb_colors = get_dominant_colors(img)

        # top_3_lab_colors = NP array [[L1, a1, b1], [L2, a2, b2], [L3, a3, b3]]
        top_lab_colors = [rgb_to_lab(rgb_color) for rgb_color in top_rgb_colors]

        # lab_color_vector = 9D vector in LAB space [L1, a1, b1, L2, a2, b2, L3, a3, b3]
        lab_color_vector = np.array(top_lab_colors).flatten()

        tracks_with_colors.append((track_id, lab_color_vector))

    # print('TRACKS WITH COLORS (ID, vector)')
    # print(tracks_with_colors)

    sorted_track_ids = []
    # Our starting reference color vector will be the first lab_color_vector in the list
    reference_vector = tracks_with_colors[0][1]

    tracks_with_colors.sort(
        key=lambda x: cosine_similarity(vec1=reference_vector, vec2=x[1]), 
        reverse=True
    )
    
    # while tracks_with_colors:
    #     # Cosine similarity has range [-1, 1], with higher value = vectors are more similar
    #     # Thus, sort in reverse (descending) order to get similar colors next to each other
    #     tracks_with_colors.sort(
    #         key=lambda x: cosine_similarity(vec1=x[1], vec2=reference_vector), 
    #         reverse=True
    #     )
    #
    #    # I want to iteratively update the reference vector to the latest addition
    #    # Thus, each sort will be in reference to the most recent album cover
    #    most_similar_track_id, most_similar_lab_vector = tracks_with_colors.pop(0)
    #    sorted_track_ids.append(most_similar_track_id)
    #    reference_vector = most_similar_lab_vector

    # print('SORTED TRACK IDS')
    # print(sorted_track_ids)
    # sorted_track_ids = list of track IDs
    sorted_track_ids = [track[0] for track in tracks_with_colors]
    return sorted_track_ids

@sorting_bp.route('/sorter')
def sorter():
    access_token = session.get('access_token')
    user_info = get_user_info(access_token)
    playlists = get_owned_playlists(access_token)

    return render_template('playlists.html', user_name=user_info['display_name'], playlists=playlists)

@sorting_bp.route('/sort_playlist/<playlist_id>')
def sort_playlist(playlist_id):
    access_token = session.get('access_token')
    print(f'Successfully started sorting route for {playlist_id}')

    # sorted_track_ids = list of track IDs
    sorted_track_ids = sort_tracks(access_token, playlist_id)

    # replace the tracks with the sorted order
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Clearing the playlist first to execute post (replacement) request
    clear_data = {'uris': []}
    clear_response = requests.put(url=url, json=clear_data, headers=headers)

    if clear_response.status_code not in [200, 201]:
        print(f'Error clearing playlist: {clear_response.json()}')
        return jsonify({
            'status': 'error',
            'message': 'Failed to clear playlist',
            'response': clear_response.json()
        })

    # Convert track IDs to Spotify URI format and split this list into chunks of size=100
    track_uris = [f'spotify:track:{track_id}' for track_id in sorted_track_ids]
    track_uri_chunks = list(chunk_list(lst=track_uris, chunk_size=100))
    
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