import unittest
from unittest.mock import patch

from ..api.spotify import get_auth_url, get_user_info, get_track_info, get_owned_playlists

class TestAPIInteraction(unittest.TestCase):

    