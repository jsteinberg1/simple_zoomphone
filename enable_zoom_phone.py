import sys
import argparse
import time

from zoomphone import ZoomAPIClient


def enable_zoom_phone(
    zoomapi: ZoomAPIClient,
    userId: str,
    site_name: str,
    calling_plan_name: str = None,
    extension_number: str = None,
    phone_number: str = None,
):
    """Enable Zoom Phone on existing Zoom user

    Args:
        userId (str): userId or email address
        site_id (str): Zoom Phone Site ID
        extension_number (str): Extension number to assign to user.  If extension is omited, then the next available extension will be assigned.
        phone_number (str): Phone Number to assign to user.  To assign a random phone number from the unassigned list on the ZP site, set to 'auto'
    """
    # TODO:
    """
    add logic to auto assign next available extension
    """

    if phone_number != None and calling_plan_name == None:
        print("Must specify calling plan when assigning phone number")
        sys.exit(1)

    # Search for ZP Site Name, check if zoom phone site exists, and get ZP Site ID
    if site_name:
        site_response = zoomapi.phone().list_phone_sites()
        try:
            site = next(item for item in site_response if item["name"] == site_name)
            site_id = site["id"]
        except StopIteration:
            print(f"Unable to find ZP site with name {site_name}")
            sys.exit(1)

    # check if user already has Zoom Phone enabled
    if userId:
        response = zoomapi.users().get_user_settings(userId=userId)
        try:
            zoom_phone_enabled = response["feature"]["zoom_phone"]
        except:
            print(f"Unable to determine Zoom Phone license status for user {userId}")
            sys.exit(1)
        else:
            # enable Zoom Phone for existing Zoom User
            if zoom_phone_enabled == True:
                print(f"User {userId} is already enabled for Zoom Phone")
                sys.exit(1)

    # check for valid calling plan
    if calling_plan_name:
        calling_plan_id = None
        calling_plan_list = zoomapi.phone().list_calling_plans()
        try:
            calling_plan = next(
                item
                for item in calling_plan_list
                if item["name"].lower() == calling_plan_name.lower()
            )
        except:
            Print(f"{calling_plan_name} is not a valid calling plan")
            sys.exit(1)

        if "type" in calling_plan:
            calling_plan_id = calling_plan["type"]

        if "available" in calling_plan:
            if calling_plan["available"] == 0:
                print(
                    f"Calling Plan {calling_plan_name} does not have any available licenses to allocate."
                )
                sys.exit(1)

    # check for extension - if not provided, then find next available extension for this user
    if extension_number == None:
        extension_number = "tbd"  # TODO - find APIs to get the next available extension in the ZP site.
        print(
            "Automatic assignment of extension is not currently working, please manually specify extension."
        )
        sys.exit(1)

    # Find phone number to assign to user
    if phone_number:
        site_unassigned_phone_number_list = zoomapi.phone().list_phone_numbers(
            type_="unassigned", number_type="toll", site_id=site_id
        )

        if phone_number == "auto":
            # assign first available number in site
            phone_number = site_unassigned_phone_number_list[0]
        else:
            # find number specified for user
            try:
                phone_number = next(
                    item
                    for item in site_unassigned_phone_number_list
                    if item["number"] == phone_number
                )
            except StopIteration:
                print(
                    f"Specified {phone_number} was not found as an 'unassigned' number on ZP site {site_name}. Phone number must be specified in E.164 format"
                )
                sys.exit(1)

    response = zoomapi.users().update_user_settings(
        userId=userId,
        data={
            "feature": {"zoom_phone": True}
        },  # this will temporarily assign an extension but we may change it later
    )
    time.sleep(2)  # give time for ZP to provision user

    # change site and extension
    response = zoomapi.phone().update_user_profile(
        userId=userId, extension_number=extension_number, site_id=site_id
    )

    # assign calling plan
    if calling_plan_id:
        assign_calling_plan_response = zoomapi.phone().assign_calling_plan_to_user(
            userId=userId, calling_plan_id=calling_plan_id
        )

    # assign phone number
    if phone_number != None:
        assign_phone_number_response = zoomapi.phone().assign_number_to_user(
            userId=userId, phone_number_id=phone_number["id"]
        )

    # Perform validation
    user_profile_response = zoomapi.phone().get_user_profile(userId=userId)
    if user_profile_response:
        print(f"Finished adding user {user_profile_response['email']}")
        print(f"Extension: {user_profile_response['extension_number']}")
        if len(user_profile_response["calling_plans"]) > 0:
            print(f"Calling Plan: {user_profile_response['calling_plans'][0]['name']}")
        if len(user_profile_response["phone_numbers"]) > 0:
            print(
                f"Phone Number: {user_profile_response['phone_numbers'][0]['number']}"
            )
    else:
        print("Unable to determine status of script execution.")


if __name__ == "__main__":

    # Run script with ArgParser

    parser = argparse.ArgumentParser(
        prog="Zoom Phone User Provisioning",
        description="Script to enable Zoom Phone feature for existing Zoom user via marketplace.zoom.us API.",
    )
    parser.add_argument("API_KEY", type=str, help="API key for Zoom account.")
    parser.add_argument("API_SECRET", type=str, help="API secret for Zoom account.")
    parser.add_argument(
        "email",
        type=str,
        default="",
        help="Specify the email address to download recordings for a single user, otherwise will download all user recordings",
    )
    parser.add_argument(
        "site_name",
        type=str,
        default="",
        help="Specify the Zoom Phone Site Name where this user should be assigned.",
    )
    parser.add_argument(
        "--extension",
        type=str,
        default=None,
        help="Specify the Zoom Phone Extension to assign to this user. Omit to have extension automatically assigned.",
    )
    parser.add_argument(
        "--calling_plan_name",
        type=str,
        default=None,
        help="Specify the Zoom Phone Calling Plan to assign to this user.",
    )
    parser.add_argument(
        "--phone_number",
        type=str,
        default=None,
        help="Specify the Zoom Phone DID/DDI to assign to this user.  Set to 'auto' to automatically assign an available DID/DDI at the Zoom Phone site.",
    )

    args = parser.parse_args()

    zoomapi = ZoomAPIClient(API_KEY=args.API_KEY, API_SECRET=args.API_SECRET)

    enable_zoom_phone(
        zoomapi=zoomapi,
        userId=args.email,
        site_name=args.site_name,
        calling_plan_name=args.calling_plan_name,
        extension_number=args.extension,
        phone_number=args.phone_number,
    )
