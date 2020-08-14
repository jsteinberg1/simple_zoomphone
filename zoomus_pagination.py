import json

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
