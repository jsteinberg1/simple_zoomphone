import argparse
import csv
import time
import datetime
import json

from zoomphone import ZoomAPIClient


def get_call_logs(
    API_KEY: str,
    API_SECRET: str,
    from_date: datetime.datetime,
    number_of_days: int = 1,
    department: str = "",
    job_title: str = "",
    call_direction: str = "all",
):
    """
    Script to access Zoom Phone Call Log via marketplace.zoom.us API

    --call_direction can be used to limit results to 'outbound' or 'inbound' calls.
    """

    zoom_api_client = ZoomAPIClient(API_KEY, API_SECRET)

    # Get all Zoom Users
    user_list = zoom_api_client.users_list_users()

    # Get all ZP Users
    phone_user_list = zoom_api_client.phone_list_users()

    # Set Call Log Query Parameters
    page_size = 300

    # Set end date based on from_date + number of days ( zoom Call log API is limited to max 30 days in a single query)
    to_date = from_date + datetime.timedelta(days=number_of_days)

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

    download_count = 0
    error_count = 0

    # Create CSV file, query Call Log API, and write data
    filename = datetime.datetime.now().strftime("call-logs-%Y-%m-%d-%H-%M.csv")
    with open(filename, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(
            output_file, extrasaction="ignore", fieldnames=headers
        )
        dict_writer.writeheader()

        # iterate phone users
        for this_user in phone_user_list:

            # find the ZP users ZM user profile - this is used to merge data from overall ZM users into ZP call log
            this_user_zm_info = ""
            this_user_zm_info = next(
                item
                for item in user_list
                if item["email"].lower() == this_user["email"].lower()
            )

            # Handle users that don't have a department specified. ( Set 'dept' to '' to prevent future error)
            if "dept" not in this_user_zm_info:
                this_user_zm_info["dept"] = ""

            # check whether optional department parameter was included in filter
            if department != "":
                # we only want users from a specific department in CSV output
                if department.lower() != this_user_zm_info["dept"].lower():
                    # this user is not in the correct department, so skip to next users
                    continue

            # Get Title from user profile ( title is not provided in the list ZM users API call, so need to query each ZM user to get this. )
            this_user_get = zoom_api_client.users_get_user(userId=this_user["email"])

            if "job_title" in this_user_get:

                this_user_title_temp = this_user_get["job_title"]
            else:
                this_user_title_temp = ""

            # check whether optional job_title parameter was included in filter
            if job_title != "":
                # we only want users with a specific job_title in CSV output
                if job_title.lower() != this_user_title_temp.lower():
                    # this user does not have the correct job title, so skip to next users
                    continue

            print(f"Getting Call Logs for user {this_user['email']}", end="")
            try:
                # get this user's call logs
                this_user_call_logs = []

                this_user_call_logs = zoom_api_client.phone_get_user_call_logs(
                    userId=this_user["email"], from_date=from_date, to_date=to_date
                )

                # filter call logs as needed
                if len(this_user_call_logs) > 0:
                    if call_direction == "inbound":
                        # only keep inbound calls
                        this_user_call_logs = [
                            x
                            for x in this_user_call_logs
                            if x["direction"] == "inbound"
                        ]
                    elif call_direction == "outbound":
                        # only keep outbound calls
                        this_user_call_logs = [
                            x
                            for x in this_user_call_logs
                            if x["direction"] == "outbound"
                        ]

                    # loop through all returned call logs & add data for additional columns as required
                    for user_call_log in this_user_call_logs:
                        user_call_log.update(
                            {
                                "email": this_user_zm_info["email"],
                                "dept": this_user_zm_info["dept"],
                                "job_title": this_user_title_temp,
                            }
                        )

                    dict_writer.writerows(this_user_call_logs)
                print(f" - {len(this_user_call_logs)} call logs retrieved.")
                download_count += 1

            except Exception as e:
                print(f" - Warning: {e}")
                error_count += 1

    # Print error count
    print(f"Users downloaded: {download_count}")
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
        "--department",
        type=str,
        default="",
        help="Specify Department to only export Call Logs for users with this department",
    )
    parser.add_argument(
        "--job_title",
        type=str,
        default="",
        help="Specify Job Title to only export Call Logs for users with this title.",
    )
    parser.add_argument(
        "--call_direction",
        type=str,
        default="all",
        help="Specify 'all', 'inbound', or 'outbound'",
    )

    args = parser.parse_args()

    get_call_logs(
        API_KEY=args.API_KEY,
        API_SECRET=args.API_SECRET,
        from_date=args.from_date,
        number_of_days=args.number_of_days,
        department=args.department,
        job_title=args.job_title,
        call_direction=args.call_direction,
    )

    # This script can run using the below configuration and removing the above argparse

    """
    # API KEY and SECRET come from JWT token created on marketplace.zoom.us 
    API_KEY = ''                              # Store API_KEY and API_SECRET confidentially as this provides admin level access to the Zoom account
    API_SECRET = input("Enter API_SECRET: ")
    from_date = datetime.datetime(2020, 5, 1)
    number_of_days = 30  # API will not return more than 30 days, do not use a value > 30
    job_title = ''
    department = ''
    call_direction = 'outbound' # 'outbound', 'inbound', 'all'
    get_call_logs(API_KEY, API_SECRET, from_date, number_of_days, call_direction)
    """
