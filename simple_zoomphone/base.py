import requests
from requests_oauthlib import OAuth2Session

from .util import JWT_AUTH

from .phone import Phone
from .users import Users


class ZoomAPIClient(object):
    def __init__(
        self,
        API_KEY: str = None,
        API_SECRET: str = None,
        OAuth2Session: OAuth2Session = None,
    ):
        """Zoom Phone API Client

        Specify either API_KEY & API_SECRET to use JWT authentication or oAuth2Session to use oAuth authentication

        Args:
            API_KEY (str, optional): JWT API key from Zoom Marketplace.
            API_SECRET (str, optional): JWT API Secret from Zoom Marketplace.
            OAuth2Session (OAuth2Session, optional): oAuth2 Session to be used by oAuth application

        Raises:
            RuntimeError: If authentication parameters are not passed properly
        """
        self._server = "api.zoom.us/v2"

        if (API_KEY == None or API_SECRET == None) and OAuth2Session == None:
            raise RuntimeError(
                "Must specify either 1) API_KEY and API_SECRET for JWT authentication or 2) OAuth2Session for oAuth authentication"
            )
        elif (API_KEY != None and API_SECRET != None) and OAuth2Session != None:
            raise RuntimeError(
                "Specify either API_KEY and API_SECRET for JWT authentication or OAuth2Session for oAuth authentication. Do not specify both."
            )
        elif (API_KEY != None and API_SECRET != None) and OAuth2Session == None:
            # using JWT authentication and standard requests session

            s = requests.Session()
            s.auth = JWT_AUTH(API_KEY, API_SECRET)
            s.headers.update({"Content-type": "application/json"})

        elif (API_KEY == None and API_SECRET == None) and OAuth2Session != None:
            # using oAuth2 authenticaiton
            s = OAuth2Session

        self._session = s

        # Define child classes
        self.phone = Phone(self._session, self._server)
        self.users = Users(self._session, self._server)
