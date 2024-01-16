# Spotify Color Sorter

A locally run application to sort personal Spotify playlists by song album cover colors.
Utilizes the Spotify Web API and OAuth 2.0 system to securely access only user playlist data. Does not track any data.

## Description

Currently, the application is built on the basis of the Pillow ImagePalette module for color palette extraction via clustering algorithms. Using this color palette, a set of the three most dominant (i.e., largest color clusters) RGB colors from a given song's album cover is obtained and concatenated into a 9-dimensional vector in LAB space. Finally, the cosine similarity for each vector representation is calculated and it is upon this heuristic that sorting is done. 

Using this application on your local machine does not track any login data and is granted these permissions for use in interacting with Spotify's Web API.

```
SCOPE = 'user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
```

Unit tests for testing interaction with Spotify's Web API can be found in [/SpotifyColorSorter/app/tests](/SpotifyColorSorter/app/tests).

## Getting Started

These instructions will get you a copy of this Flask project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To use this program, it is required to have compatible and/or up-to-date versions of the following packages:

```
Python 3.x
pip (Python package manager)
git (Version control system)
```

### Installing

First, clone the repository onto your local device using 

```
git clone https://github.com/elliothha/SpotifyColorSorter.git
```

After navigating to the location of the downloaded project directory, create and activate your virtual environment here. After installing the required dependencies, create a file in the root directory named ".env" without the quotations, and please reach out for the client information! After setting the environment variables, the project will be ready for personal use.

```
# 1. Create the virtual environment
python -m venv venv

# 2. Activate the virtual environment
# 2a. For Windows
venv\Scripts\activate

# 2b. For macOS and Linux:
source venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

The core dependencies are as follows - see the [requirements.txt](requirements.txt) file for full details:

```
Flask==3.0.0
numpy==1.26.2
opencv-python==4.8.1.78
Pillow==10.1.0
python-dotenv==1.0.0
requests==2.31.0
spotipy==2.23.0a
```

## Deployment

After installing the required dependencies, run the program via the command

```
python app.py
```

## Authors

* **Elliot Ha** - [LinkedIn](https://www.linkedin.com/in/elliothha/) | [GitHub](https://github.com/elliothha)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
