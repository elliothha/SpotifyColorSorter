import unittest
from unittest.mock import patch

from app.api.spotify import get_auth_url, get_user_info, get_track_info, get_owned_playlists

class TestAPIInteraction(unittest.TestCase):

    @patch('app.api.spotify.requests.get')
    def test_get_user_info(self, mock_get):
        # Configure the mock to return a response with an OK status code and mock data
        mock_response = {
            'id': '1234',
            'display_name': 'Test User',
            'email': 'testuser@example.com'
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Function call
        access_token = 'dummy_access_token'
        response = get_user_info(access_token)

        # Assertions
        self.assertEqual(response, mock_response)

        mock_get.assert_called_with(
            url='https://api.spotify.com/v1/me', 
            headers={'Authorization': f'Bearer {access_token}'}
        )

if __name__ == '__main__':
    unittest.main()
