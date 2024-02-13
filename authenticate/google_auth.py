from urllib.parse import urlencode

import requests

USERINFO_SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth?'
TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
USERINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v3/userinfo'





class GoogleAuth:
    def __init__(self, google_secret: dict):
        self.google_secret = google_secret

    def login_redirect(self, oauth2_state: str, redirect_uri: str):
        qs = urlencode({
            'client_id': self.google_secret['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(USERINFO_SCOPES),
            'state': oauth2_state
        })

        url = AUTH_ENDPOINT + qs
        return url

    def get_user_info(self, auth_code: str, redirect_uri: str) -> dict:
        token = self.__request_access_token(auth_code=auth_code, redirect_uri=redirect_uri)
        user_info = self.__request_user_info(token)

        return user_info

    def __request_access_token(self, auth_code: str, redirect_uri: str) -> str:
        payload = {
            'client_id': self.google_secret['client_id'],
            'client_secret': self.google_secret['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }

        response = requests.post(
            TOKEN_ENDPOINT,
            data=payload,
            headers={'Accept': 'application/json'}
        )

        if response.status_code != 200:
            raise Exception("Failed to authorize user")

        token = response.json().get('access_token')
        if not token:
            raise Exception("Failed to authorize user")

        return token

    def __request_user_info(self, token: str):
        response = requests.get(
            USERINFO_ENDPOINT,
            headers={
                'Authorization': 'Bearer ' + token,
                'Accept': 'application/json'
            }
        )

        if response.status_code != 200:
            raise Exception("Failed to authorize user")

        return response.json()
