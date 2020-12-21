#!/usr/bin/env python3

import sys
import logging
import argparse
import time

from simple_zoomphone.exceptions import ZoomAPIError

from simple_zoomphone import ZoomAPIClient

logger = logging.getLogger("zp")
logger.setLevel(logging.INFO)


def remove_zoom_phone(zoomapi: ZoomAPIClient, userId: str):
    """Disable Zoom Phone on existing Zoom user.  Will remove the DID and return to available pool, remove extension, and delete Zoom Phone license.

    Args:
        userId (str): userId or email address
    """


if __name__ == "__main__":
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    # Run script with ArgParser
    parser = argparse.ArgumentParser(
        prog="Zoom Phone User Provisioning",
        description="Script to enable Zoom Phone feature for existing Zoom user via marketplace.zoom.us API.",
    )
    parser.add_argument(
        "-API_KEY", type=str, help="API key for Zoom account.", required=True
    )
    parser.add_argument(
        "-API_SECRET", type=str, help="API secret for Zoom account.", required=True
    )
    parser.add_argument(
        "-email",
        type=str,
        default="",
        help="Specify the email address to download recordings for a single user, otherwise will download all user recordings",
        required=True,
    )

    args = parser.parse_args()

    zoomapi = ZoomAPIClient(API_KEY=args.API_KEY, API_SECRET=args.API_SECRET)

    enable_zoom_phone(zoomapi=zoomapi, userId=args.email)
