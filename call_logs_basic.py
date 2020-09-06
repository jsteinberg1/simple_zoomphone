#!/usr/bin/env python3

import logging
import argparse
import csv
import datetime

from zoomphone import ZoomAPIClient

logger = logging.getLogger("zp")
logger.setLevel(logging.INFO)


def get_call_logs(
    API_KEY: str,
    API_SECRET: str,
    from_date: datetime.datetime,
    number_of_days: int = 1,
    call_direction: str = "all",
):
    """
    Script to access Zoom Phone Call Log via marketplace.zoom.us API

    """

    zoomapi = ZoomAPIClient(API_KEY, API_SECRET)

    # Get all ZP Users
    phone_user_list = zoomapi.phone().list_users()

    # Set Call Log Query Parameters
    page_size = 300

    # Set end date based on from_date + number of days ( zoom Call log API is limited to max 30 days in a single query)
    to_date = from_date + datetime.timedelta(days=number_of_days)

    # Set headers for CSV file
    headers = [
        "email",
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
        for this_user in phone_user_list:
            logger.info(f"Getting Call Logs for user {this_user['email']}", end="")
            try:
                # get this user's call logs
                this_user_call_logs = []

                this_user_call_logs = zoomapi.phone().get_user_call_logs(
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
                        user_call_log.update({"email": this_user["email"]})

                    dict_writer.writerows(this_user_call_logs)

                    logger.info(f" - {len(this_user_call_logs)} call logs retrieved.")

            except Exception as e:
                logger.info(f" - Warning: {e}")
                error_count += 1

    # Print error count
    logger.info(f"Errors encountered: {error_count}")


# Run this script using argparse

if __name__ == "__main__":
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

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
