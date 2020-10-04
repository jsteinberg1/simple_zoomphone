import time
import json
import datetime

from .util import validateparam
from .exceptions import ZoomAPIError


class Phone:
    def __init__(self, session, server):
        self._session = session
        self._server = server

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
                    raise ZoomAPIError(f"Exceeded rate limit requests on request {url}")
                else:
                    rate_limit_counter += 1  # increase rate limit counter
                    time.sleep(1)  # sleep for a second, then try again

            else:
                raise ZoomAPIError(
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
                raise ZoomAPIError(
                    f"No {key_in_response_to_return} records in API response."
                )

    def _phone_post(self, endpoint_url: str, data: dict):
        """Generic HTTP Post method for Zoom Phone API.

        Args:
            endpoint_url (str): endpoint url
            data (dict): data json used in HTTP post body.
            raw (bool, optional): If set to 'True' will return raw JSON response as returned from Zoom API.  IF set to 'False', this function will complete pagination and return a list of all data returned on key 'key_in_response_to_return'. Defaults to False.
        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """

        url = "https://" + self._server + endpoint_url

        # use while loop to handle Zoom Phone API rate limits
        rate_limit_counter = 0
        while True:
            response = self._session.post(url, data=json.dumps(data))

            if response.status_code in [200, 201, 204]:
                # pass requests response to calling method for further request validation
                if response.content in [b""]:
                    return response.status_code
                else:
                    return response.content

            elif response.status_code == 429:
                # API returned that we are rate limited, wait one second and try again

                if rate_limit_counter > 5:
                    # we shouldn't get rate limited more than 5 times on a single query, but if we do error with exception
                    raise ZoomAPIError(f"Exceeded rate limit requests on request {url}")
                else:
                    rate_limit_counter += 1  # increase rate limit counter
                    time.sleep(1)  # sleep for a second, then try again

            else:
                if "message" in response.json():
                    raise ZoomAPIError(response.json()["message"])
                else:
                    raise ZoomAPIError(
                        f"Received status code {response.status_code} on request {url}"
                    )

    def _phone_patch(self, endpoint_url: str, params: dict = None, data: dict = None):
        """Generic HTTP Patch method for Zoom Phone API.

        Args:
            endpoint_url (str): endpoint url
            params (dict, optional): parameters used in HTTP query parameters. Defaults to None.
            raw (bool, optional): If set to 'True' will return raw JSON response as returned from Zoom API.  IF set to 'False', this function will complete pagination and return a list of all data returned on key 'key_in_response_to_return'. Defaults to False.
        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type]: [description]
        """

        url = "https://" + self._server + endpoint_url

        # use while loop to handle Zoom Phone API rate limits
        rate_limit_counter = 0
        while True:
            response = self._session.patch(url, params=params, data=json.dumps(data))

            if response.status_code in [200, 204]:
                # pass requests response to calling method for further request validation
                return response

            elif response.status_code == 429:
                # API returned that we are rate limited, wait one second and try again

                if rate_limit_counter > 5:
                    # we shouldn't get rate limited more than 5 times on a single query, but if we do error with exception
                    raise RuntimeError(f"Exceeded rate limit requests on request {url}")
                else:
                    rate_limit_counter += 1  # increase rate limit counter
                    time.sleep(1)  # sleep for a second, then try again

            else:
                if "message" in response.json():
                    raise ZoomAPIError(response.json()["message"])
                else:
                    raise ZoomAPIError(
                        f"Received status code {response.status_code} on request {url}"
                    )

    def list_users(self, site_id: str = None, page_size: int = 100, raw: bool = False):
        validateparam(page_size, range(1, 101), "'page_size' must be between 1 - 100")

        params = {}
        params["page_size"] = page_size

        if site_id:
            params["site_id"] = site_id

        response = self._phone_get(
            endpoint_url="/phone/users",
            raw=raw,
            params=params,
            key_in_response_to_return="users",
        )
        return response

    def get_user_profile(self, userId: str) -> dict:
        response = self._phone_get(endpoint_url=f"/phone/users/{userId}", raw=True)
        return response

    def get_user_settings(self, userId: str) -> dict:
        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/settings", raw=True
        )
        return response

    def get_user_call_logs(
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

        validateparam(page_size, range(1, 301), "'page_size' must be between 1 - 300")

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

    def get_user_call_recordings(
        self,
        userId: str,
        page_size: int = 300,
        raw: bool = False,
    ):

        validateparam(page_size, range(1, 301), "'page_size' must be between 1 - 300")
        try:
            response = self._phone_get(
                endpoint_url=f"/phone/users/{userId}/recordings",
                params={
                    "page_size": page_size,
                },
                raw=raw,
                key_in_response_to_return="recordings",
            )
        except ZoomAPIError as e:
            if e == "No recordings records in API response.":
                """
                The Zoom API will not return any 'recordings' fields if the user has no recordings, typically this errors the '_phone_get' method, but we need to override that in this case and return an empty list.
                """
                response = []
            else:
                raise ZoomAPIError(e)

        return response

    def get_user_voicemails(
        self,
        userId: str,
        status: str = "all",
        page_size: int = 300,
        raw: bool = False,
    ):

        validateparam(page_size, range(1, 301), "'page_size' must be between 1 - 300")

        validateparam(
            status,
            ["all", "read", "unread"],
            "'status' must be one of 'all', 'read', 'unread'",
        )

        response = self._phone_get(
            endpoint_url=f"/phone/users/{userId}/voice_mails",
            params={"page_size": page_size, "status": status},
            raw=raw,
            key_in_response_to_return="voice_mails",
        )

        return response

    def get_account_call_logs(
        self,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        type_: str = "all",
        page_size: int = 300,
        raw: bool = False,
    ):

        if (to_date - from_date).days > 30:
            raise RuntimeWarning("'from' date and 'to' date must be 30 days or less")

        validateparam(page_size, range(1, 301), "'page_size' must be between 1 - 300")

        validateparam(
            type_,
            ["all", "missed"],
            "Invalid value for 'type' should be either 'all' or 'missed'.",
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

    def list_phone_numbers(
        self,
        type_: str = None,
        extension_type: str = None,
        number_type: str = None,
        pending_numbers: bool = None,
        site_id: str = None,
        page_size: int = 100,
        raw: bool = False,
    ):
        """List all phone numbers on Zoom Phone

        Args:
            type_ (str, optional): can be set to either 'assigned' or 'unassigned'. Omit for both. Defaults to None.
            extension_type (str, optional): Can be set to 'user', 'callQueue', 'autoReceptionist', or 'commonAreaPhone'. Omit to include all. Defaults to None.
            number_type (str, optional): Can be set to either 'toll' or 'tollfree'. Defaults to None.
            pending_numbers (bool, optional): Can be set to 'True' to include pending numbers. Defaults to None.
            site_id (str, optional): Include site ID to filter by this site.  Note this is site ID not site NAME. Defaults to None.
            page_size (int, optional): Page size 1 - 100. Defaults to 100.
            raw (bool, optional): Set to true to receive raw JSON response from API. False to page through all data. Defaults to False.

        Returns:
            [type]: [description]
        """

        params = {}

        if type_:
            validateparam(
                type_,
                ["all", "assigned", "unassigned"],
                "'type' must be either 'all', 'assigned', or 'unassigned'",
            )
            params["type"] = type_

        if extension_type:
            validateparam(
                extension_type,
                ["user", "callQueue", "autoReceptionist", "commonAreaPhone"],
                "'extension_type' must be either 'user', 'callQueue', 'autoReceptionist', or 'commonAreaPhone'",
            )
            params["extension_type"] = extension_type

        if number_type:
            params["number_type"] = number_type

            validateparam(
                number_type,
                ["toll", "tollfree"],
                "'number_type' must be either 'toll' or 'tollfree'",
            )

        if pending_numbers != None:
            params["pending_numbers"] = pending_numbers

        if site_id:
            params["site_id"] = site_id

        validateparam(page_size, range(1, 101), "'page_size' must be between 1 - 100")
        params["page_size"] = page_size

        if extension_type and not type_:
            # if extension_type is set, then we must also set type to assigned, otherwise API will not return desired data.
            type_ = "assigned"

        response = self._phone_get(
            endpoint_url="/phone/numbers",
            raw=raw,
            params=params,
            key_in_response_to_return="phone_numbers",
        )
        return response

    def update_user_profile(
        self, userId: str, extension_number: str = None, site_id: str = None
    ) -> dict:
        data = {}
        # the API will not allow both site_id and extension_number to be changed at the same time.

        if site_id:
            data = {}
            data["site_id"] = site_id
            response = self._phone_patch(
                endpoint_url=f"/phone/users/{userId}", data=data
            )
            # ZP needs some time to process this change before making other changes
            time.sleep(2)

        if extension_number:
            data = {}
            data["extension_number"] = extension_number
            response = self._phone_patch(
                endpoint_url=f"/phone/users/{userId}", data=data
            )

        # read user's profile to verify change
        response = self.get_user_profile(userId=userId)

        if site_id and response["site_id"] != site_id:
            raise ZoomAPIError("Error processing API request")

        if extension_number and response["extension_number"] != int(extension_number):
            raise ZoomAPIError("Error processing API request")

        return response

    def assign_number_to_user(self, userId: str, phone_number_id: str):
        data = {"phone_numbers": [{"id": phone_number_id}]}
        response = self._phone_post(
            endpoint_url=f"/phone/users/{userId}/phone_numbers", data=data
        )
        return response

    def unassign_number_from_user():
        pass
        # TODO - do this next and test the http_delete

    def assign_calling_plan_to_user(self, userId: str, calling_plan_id: int):
        data = {"calling_plans": [{"type": calling_plan_id}]}
        response = self._phone_post(
            endpoint_url=f"/phone/users/{userId}/calling_plans", data=data
        )
        return response

    def unassign_calling_plan_from_user():
        pass
        # TODO - do this next and test the http_delete

    def get_phone_number_details(self, numberId: str) -> dict:
        response = self._phone_get(endpoint_url=f"/phone/numbers/{numberId}", raw=True)
        return response

    def list_calling_plans(self) -> dict:

        response = self._phone_get(
            endpoint_url="/phone/calling_plans",
            raw=True,
            key_in_response_to_return="calling_plans",
        )

        if "calling_plans" in response:
            return response["calling_plans"]
        else:
            ZoomAPIError("Unable to find calling_plans in API response")

    def list_phone_sites(self, page_size: int = 300, raw: bool = False):

        validateparam(page_size, range(1, 301), "'page_size' must be between 1 - 300")

        response = self._phone_get(
            endpoint_url="/phone/sites",
            raw=raw,
            params={"page_size": page_size},
            key_in_response_to_return="sites",
        )
        return response

    def create_phone_site(
        self,
        name: str,
        auto_receptionist_name: str,
        emergency_address_country: str,
        emergency_address_address_line1: str,
        emergency_address_city: str,
        emergency_address_zip: str,
        emergency_address_state_code: str,
        emergency_address_address_line2: str = None,
        site_code: int = None,
        short_extension_length: int = None,
    ):
        # TODO add logic on short extension length and site code

        response = self._phone_post(
            endpoint_url="/phone/sites",
            data={
                "name": name,
                "site_code": site_code,
                "auto_receptionist_name": auto_receptionist_name,
                "default_emergency_address": {
                    "country": emergency_address_country,
                    "address_line1": emergency_address_address_line1,
                    "city": emergency_address_city,
                    "zip": emergency_address_zip,
                    "state_code": emergency_address_state_code,
                    "address_line2": emergency_address_address_line2,
                },
                "short_extension": {"length": short_extension_length},
            },
        )
        return response

    def list_call_queues(self, page_size: int = 100, raw: bool = False):

        validateparam(page_size, range(1, 101), "'page_size' must be between 1 - 100")

        response = self._phone_get(
            endpoint_url="/phone/call_queues",
            raw=raw,
            params={"page_size": page_size},
            key_in_response_to_return="call_queues",
        )
        return response

    def add_members_to_queue(self, callQueueId: str, emails: list):

        user_list = [{"email": email} for email in emails]

        data = {"members": {"users": user_list}}

        response = self._phone_post(
            endpoint_url=f"/phone/call_queues/{callQueueId}/members", data=data
        )
        return response

    def get_call_queue_details(self, callQueueId: str):
        response = self._phone_get(
            endpoint_url=f"/phone/call_queues/{callQueueId}",
            raw=True,
        )
        return response
