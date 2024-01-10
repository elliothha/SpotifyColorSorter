# Spotify Color Sorter

A locally run application to sort personal Spotify playlists by song album cover colors.
Utilizes the Spotify Web API and OAuth 2.0 system to securely access only user playlist data. Does not track any data.

## Description

Currently, the system is built on the basis of KMeans clustering algorithms in order to extract the singular most dominant color in LAB space. However, this has led to suboptimal results via the eye test, as some songs out of the majority appear out of place or disrupt what would otherwise be a singularly smooth color gradient. 

In order to correct this, I plan on expanding on the sorting heuristic by extracting a color "palette" of a number of the most dominant colors in an album cover, rather than just a single color. From here, I would be able to better sort songs to ensure a smooth gradient and reduce the variability inherent in KMeans causing irregularities.

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

After navigating to the location of the downloaded project directory, create and activate your virtual environment here. After installing the required dependencies, the project will be ready for personal use.

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
