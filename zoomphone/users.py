from .util import validateparam


class Users:
    def __init__(self, session, server):
        self._session = session
        self._server = server

    def _users_get(
        self,
        endpoint_url: str,
        params: dict = None,
        raw: bool = False,
        key_in_response_to_return: str = None,
    ):
        """Generic HTTP GET method for Zoom User API

        Args:
            endpoint_url (str): endpoint url
            params (dict, optional): parameters used in HTTP query parameters. Defaults to None.
            raw (bool, optional): If set to 'True' will return raw JSON response as returned from Zoom API.  IF set to 'False', this function will complete pagination and return a list of all data returned on key 'key_in_response_to_return'. Defaults to False.
            key_in_response_to_return (str, optional): Used to determine the key in the Zoom API response with interesting data to use for pagination. Defaults to None.

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type]: [description]
        """

        if raw == False and key_in_response_to_return == None:
            raise ValueError(
                "You must specify a key_in_response_to_return if 'raw' = False"
            )

        url = "https://" + self._server + endpoint_url

        # use while loop to handle Zoom Phone API rate limits
        rate_limit_counter = 0
        while True:
            response = self._session.get(url, params=params)

            if response.status_code == 200:
                break

            elif response.status_code == 429:
                # API returned that we are rate limited, wait one second and try again

                if rate_limit_counter > 5:
                    # we shouldn't get rate limited more than 5 times on a single query, but if we do error with exception
                    raise RuntimeError(f"Exceeded rate limit requests on request {url}")
                else:
                    rate_limit_counter += 1  # increase rate limit counter
                    time.sleep(1)  # sleep for a second, then try again

            else:
                raise RuntimeError(
                    f"Received status code {response.status_code} on request {url}"
                )

        raw_json = response.json()

        if raw:
            # return raw JSON response without any modification, paging is handed outside of this class
            return response.json()
        else:
            # we will handle paging within the class method.  page through all data and return a list of all responses
            if key_in_response_to_return in raw_json:
                list_of_paged_data_to_return = raw_json[key_in_response_to_return]

                # complete pagination to retrive all data
                while raw_json["page_number"] < raw_json["page_count"]:
                    params["page_number"] = raw_json["page_number"] + 1

                    raw_json = self._phone_get(
                        endpoint_url, params, True, key_in_response_to_return
                    )

                    if key_in_response_to_return in raw_json:
                        list_of_paged_data_to_return = (
                            list_of_paged_data_to_return
                            + raw_json[key_in_response_to_return]
                        )

                return list_of_paged_data_to_return

            else:
                raise ValueError(
                    f"Unable to find {key_in_response_to_return} in json response"
                )

    def list_users(
        self,
        status: str = "active",
        role_id: str = None,
        page_size: int = 300,
        raw: bool = False,
    ):

        if status:
            validateparam(
                status,
                ["active", "inactive", "pending"],
                "'status' is set to an invalid value not supported by Zoom API",
            )

        params = {"page_size": page_size, "status": status}

        if role_id != None:
            params["role_id"] = role_id

        response = self._users_get(
            endpoint_url="/users",
            raw=raw,
            params=params,
            key_in_response_to_return="users",
        )
        return response

    def get_user(self, userId: str, login_type: str = None) -> dict:
        params = {}

        if login_type:
            validateparam(
                login_type,
                ["0", "1", "99", "100", "101"],
                "'login_type' is set to an invalid value not supported by Zoom API",
            )
            params["login_type"] = login_type

        response = self._users_get(
            endpoint_url=f"/users/{userId}", params=params, raw=True
        )
        return response