'''
Author: Elliot H. Ha
Created on: Dec 27, 2023

Description:
This file provides the entry point to the Spotify Color Sorter Flask app.
'''

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=8888)