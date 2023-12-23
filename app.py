import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = '8717281952454dbd9264dd61b3f49c51'
client_secret = '893e05907bd04cd99455525c3e704aa5'

# redirect_uri = URL user is redirected to after successful auth
sp_oath = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=,
    scope=
)