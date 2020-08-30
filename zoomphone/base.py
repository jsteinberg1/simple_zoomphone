import requests
import datetime
import jwt


class _ZoomAPIBase(object):
    def __init__(self, API_KEY: str, API_SECRET: str):
        self.server = "api.zoom.us/v2"

        self.jwt = jwt.encode(
            {
                "iss": API_KEY,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            },
            API_SECRET,
            algorithm="HS256",
            headers={"alg": "HS256", "typ": "JWT"},
        ).decode("utf-8")

        s = requests.Session()
        s.headers.update({"authorization": f"Bearer {self.jwt}"})
        s.headers.update({"Content-type": "application/json"})
        self.session = s