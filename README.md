# Simple Zoom Phone

These scripts are sample scripts for Zoom Phone. See Zoom API documentation on marketplace.zoom.us

This repo is a work in progress and the endoints below are still outstanding:
* /phone/blocked_list
* /phone/call_queues/
* /phone/devices
* /phone/shared_line_groups/
* /phone/sites
* /phone/common_area_phones


## Installation

1. Install Python 3.8+
2. Install required Libraries

```bash
pip install -r requirements.txt
```

## Example Library Usage

from zoomphone import ZoomAPIClient

zoomapi = ZoomAPIClient(
    API_KEY=" <Zoom API KEY here> ", API_SECRET=" <Zoom API Secret here>  "
)

result = zoomapi.users().list_users()
print(result)

result = zoomapi.phone().list_users()
print(result)


## Sample Script Usage

### Call Log Exporter

python call_logs.py -h

python call_logs.py <API_KEY> <API_SECRET> --from_date=2019-12-31 --number_of_days=30 --department="Sales" --job_title="Inside Sales Representative" --call_direction=all

### Call Recording Exporter

Download call recordings MP3 files. Specify email address for a single user or omit for all users

python call_recordings.py -h

python call_recordings.py <API_KEY> <API_SECRET> --email=bill.smith@email.com
