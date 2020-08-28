import json
from datetime import datetime

from zoomus import ZoomClient


def all_zoom_users(client: ZoomClient):
    """
    Used to page through all ZM users on the account to get all users
    """

    all_user_list = []

    page_number = 1
    page_count = 0
    page_size = 300

    while page_number <= page_count or page_count == 0:

        current_user_list_response = client.user.list(
            page_size=page_size, page_number=page_number
        )
        current_user_list = json.loads(current_user_list_response.content)

        all_user_list = all_user_list + current_user_list["users"]
        page_number = current_user_list["page_number"] + 1
        page_count = current_user_list["page_count"]

    return all_user_list


def all_zp_users(client: ZoomClient):
    """
    Used to page through all ZP users on the account to get all users
    """

    next_page_token = ""
    page_size = 300
    first_run = True

    all_user_list = []

    while next_page_token != "" or first_run == True:

        current_user_list_response = client.phone.users(
            page_size=page_size, next_page_token=next_page_token
        )
        current_user_list = json.loads(current_user_list_response.content)

        all_user_list = all_user_list + current_user_list["users"]

        next_page_token = current_user_list["next_page_token"]
        first_run = False

    return all_user_list


def all_zp_user_call_logs(
    client: ZoomClient, email: str, from_date: datetime, to_date: datetime
):
    # Get Call Logs for this user

    next_page_token = ""
    page_size = 300
    first_run = True

    all_user_call_logs = []

    while next_page_token != "" or first_run:

        phone_user_call_logs_response = client.phone.user_call_logs(
            page_size=page_size,
            email=email,
            from_date=from_date,
            to_date=to_date,
            next_page_token=next_page_token,
        )

        phone_user_call_logs = json.loads(phone_user_call_logs_response.content)

        if "call_logs" in phone_user_call_logs:
            all_user_call_logs = all_user_call_logs + phone_user_call_logs["call_logs"]

        next_page_token = phone_user_call_logs["next_page_token"]

        if next_page_token != "":
            time.sleep(
                0.25
            )  # delay due to Zoom Phone Call Log API rate limit ( 1 request per second )

        first_run = False

    return all_user_call_logs


def all_zp_user_recordings(client: ZoomClient, email: str):
    # Get Call Recordings for this user

    next_page_token = ""
    page_size = 300
    first_run = True

    all_zp_user_recordings = []

    while next_page_token != "" or first_run:

        zp_user_recordings_response = client.phone.user_recordings(
            page_size=page_size, email=email, next_page_token=next_page_token,
        )

        zp_user_recordings = json.loads(zp_user_recordings_response.content)

        if "recordings" in zp_user_recordings:
            all_zp_user_recordings = (
                all_zp_user_recordings + zp_user_recordings["recordings"]
            )

        next_page_token = zp_user_recordings["next_page_token"]

        if next_page_token != "":
            time.sleep(
                0.25
            )  # delay due to Zoom Phone Call Log API rate limit ( 1 request per second )

        first_run = False

    return all_zp_user_recordings
