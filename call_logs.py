import argparse
import csv
import time
import datetime
import json

from zoomus import ZoomClient
import zoomus_pagination


def get_call_logs(
    API_KEY: str,
    API_SECRET: str,
    from_date: datetime.datetime,
    number_of_days: int = 1,
    call_direction: str = "all",
):
    """
    Script to access Zoom Phone Call Log via marketplace.zoom.us API

    --call_direction can be used to limit results to 'outbound' or 'inbound' calls.
    """

    client = ZoomClient(API_KEY, API_SECRET)

    # Get all Zoom Users
    user_list = zoomus_pagination.all_zoom_users(client=client)

    # Get all ZP Users
    phone_user_list = zoomus_pagination.all_zp_users(client=client)

    # Set Call Log Query Parameters
    page_size = 300

    # Set end date based on from_date + number of days ( zoom Call log API is limited to max 30 days in a single query)
    end_date = from_date + datetime.timedelta(days=number_of_days)

    # Set headers for CSV file
    headers = [
        "email",
        "dept",
        "job_title",
        "caller_number",
        "caller_number_type",
        "caller_name",
        "callee_number",
        "callee_number_type",
        "callee_name",
        "direction",
        "duration",
        "result",
        "date_time",
    ]

    error_count = 0

    # Create CSV file, query Call Log API, and write data
    filename = datetime.datetime.now().strftime("call-logs-%Y-%m-%d-%H-%M.csv")
    with open(filename, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(
            output_file, extrasaction="ignore", fieldnames=headers
        )
        dict_writer.writeheader()

        # iterate phone users
        for user in phone_user_list:
            time.sleep(
                1.25
            )  # delay due to Zoom Phone Call Log API rate limit ( 1 request per second )
            print(f" Getting Call Logs for user {user['email']}")
            try:
                # find the ZP users ZM user profile
                zm_user_info_temp = ""
                zm_user_info_temp = next(
                    item
                    for item in user_list
                    if item["email"].lower() == user["email"].lower()
                )

                # Handle users that don't have a department specified. ( Set 'dept' to '' to prevent future error)
                if "dept" not in zm_user_info_temp:
                    zm_user_info_temp["dept"] = ""

                # Get Title from user profile ( title is not provided in the list ZM users API call, so need to query each ZM user to get this. )
                user_get_response = client.user.get(id=user["email"])
                user_get = json.loads(user_get_response.content)

                if "job_title" in user_get:
                    user_title_temp = user_get["job_title"]
                else:
                    user_title_temp = ""

                # Get Call Logs for this user
                next_page_token = ""
                first_run = True

                while next_page_token != "" or first_run:

                    phone_user_call_logs_response = client.phone.user_call_logs(
                        page_size=page_size,
                        email=user["email"],
                        start_date=from_date,
                        end_date=end_date,
                        next_page_token=next_page_token,
                    )
                    phone_user_call_logs = json.loads(
                        phone_user_call_logs_response.content
                    )

                    if phone_user_call_logs["total_records"] > 0:

                        # filter call logs as needed
                        if call_direction == "inbound":
                            # only keep inbound calls
                            phone_user_call_logs["call_logs"] = [
                                x
                                for x in phone_user_call_logs["call_logs"]
                                if x["direction"] == "inbound"
                            ]
                        elif call_direction == "outbound":
                            # only keep outbound calls
                            phone_user_call_logs["call_logs"] = [
                                x
                                for x in phone_user_call_logs["call_logs"]
                                if x["direction"] == "outbound"
                            ]

                        # loop through all returned call logs & add data for additional columns as required
                        for user_call_log in phone_user_call_logs["call_logs"]:
                            user_call_log.update(
                                {
                                    "email": zm_user_info_temp["email"],
                                    "dept": zm_user_info_temp["dept"],
                                    "job_title": user_title_temp,
                                }
                            )

                        dict_writer.writerows(phone_user_call_logs["call_logs"])

                    next_page_token = phone_user_call_logs["next_page_token"]
                    first_run = False
            except Exception as e:
                print(f" FAILED retrieving call Logs for user {user['email']}")
                error_count += 1
                print("Error at %s", "division", exc_info=e)
                exit()

    # Print error count
    print(f"Errors encountered: {error_count}")


# Run this script using argparse

if __name__ == "__main__":

    # Run script with ArgParser

    parser = argparse.ArgumentParser(
        prog="Zoom Phone Call Log Exporter",
        description="Script to access Zoom Phone Call Logs via marketplace.zoom.us API.",
    )
    parser.add_argument("API_KEY", type=str, help="API key for Zoom account.")
    parser.add_argument("API_SECRET", type=str, help="API secret for Zoom account.")
    parser.add_argument(
        "--from_date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
        default=datetime.datetime.today(),
        help="Starting date for call log query. (e.g. 2019-12-31)",
    )
    parser.add_argument(
        "--number_of_days",
        type=int,
        default=1,
        help="Number of days to pull call logs. Max 30 days.",
    )
    parser.add_argument(
        "--call_direction",
        type=str,
        default="all",
        help="Specify 'all', 'inbound', or 'outbound'",
    )

    args = parser.parse_args()

    get_call_logs(
        args.API_KEY,
        args.API_SECRET,
        args.from_date,
        args.number_of_days,
        args.call_direction,
    )

    # This script can run using the below configuration and removing the above argparse

    """
    # API KEY and SECRET come from JWT token created on marketplace.zoom.us 
    API_KEY = ''                              # Store API_KEY and API_SECRET confidentially as this provides admin level access to the Zoom account
    API_SECRET = input("Enter API_SECRET: ")
    from_date = datetime.datetime(2020, 5, 1)
    number_of_days = 30  # API will not return more than 30 days, do not use a value > 30
    call_direction = 'outbound' # 'outbound', 'inbound', 'all'
    get_call_logs(API_KEY, API_SECRET, from_date, number_of_days, call_direction)
    """

