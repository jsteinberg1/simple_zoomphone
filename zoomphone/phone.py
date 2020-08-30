import time
import datetime


class PhoneMixin(object):
    def _phone_get(
        self,
        endpoint_url: str,
        params: dict = None,
        raw: bool = False,
        key_in_response_to_return: str = None,
    ):
        """Generic HTTP GET method for Zoom Phone API.

        Note that Zoom Phone API pagination uses next_page_token which other Zoom APIs do not use

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

        url = "https://" + self.server + endpoint_url

        # use while loop to handle Zoom Phone API rate limits
        rate_limit_counter = 0
        while True:
            response = self.session.get(url, params=params)

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
                while raw_json["next_page_token"] != "":
                    params["next_page_token"] = raw_json["next_page_token"]

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
                raise RuntimeWarning(
                    f"No {key_in_response_to_return} records in API response."
                )

    def phone_list_users(self, page_size: int = 100, raw: bool = False):
        if page_size > 100:
            raise ValueError("'page_size' must be between 1 - 100")

        response = self._phone_get(
            endpoint_url="/phone/users",
            raw=raw,
            params={"page_size": page_size},
            key_in_response_to_return="users",
        )
        return response

    def phone_get_user_profile(self, userId: str) -> dict:
        response = self._phone_get(endpoint_url=f"/phone/users/{userId}", raw=True)
        return response

    def phone_get_user_settings(self, userId: str) -> dict:
        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/settings", raw=True
        )
        return response

    def phone_get_user_call_logs(
        self,
        userId: str,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        type_: str = "all",
        page_size: int = 300,
        raw: bool = False,
    ):

        if (to_date - from_date).days > 30:
            raise RuntimeWarning("'from' date and 'to' date must be 30 days or less")

        if page_size > 300:
            raise ValueError("'page_size' must be between 1 - 300")

        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/call_logs",
            params={
                "from": from_date,
                "to": to_date,
                "type": type_,
                "page_size": page_size,
            },
            raw=raw,
            key_in_response_to_return="call_logs",
        )

        return response

    def phone_get_user_call_recordings(
        self,
        userId: str,
        page_size: int = 300,
        raw: bool = False,
    ):

        if page_size > 300:
            raise ValueError("'page_size' must be between 1 - 300")

        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/recordings",
            params={
                "page_size": page_size,
            },
            raw=raw,
            key_in_response_to_return="recordings",
        )

        return response

    def phone_get_user_voicemails(
        self,
        userId: str,
        status: str = all,
        page_size: int = 300,
        raw: bool = False,
    ):

        if page_size > 300:
            raise ValueError("'page_size' must be between 1 - 300")

        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/voice_mails",
            params={"page_size": page_size, "status": status},
            raw=raw,
            key_in_response_to_return="voice_mails",
        )

        return response

    def phone_get_account_call_logs(
        self,
        from_date: str,
        to_date: str,
        type_: str = "all",
        page_size: int = 300,
        raw: bool = False,
    ):

        if (to_date - from_date).days > 30:
            raise RuntimeWarning("'from' date and 'to' date must be 30 days or less")

        if page_size > 300:
            raise ValueError("'page_size' must be between 1 - 300")

        if type_ not in ["all", "missed"]:
            raise ValueError(
                "Invalid value for 'type' should be either 'all' or 'missed'."
            )

        response = self._phone_get(
            endpoint_url=f"/phone/call_logs",
            params={
                "from": from_date,
                "to": to_date,
                "type": type_,
                "page_size": page_size,
            },
            raw=raw,
            key_in_response_to_return="call_logs",
        )

        return response