# Simple Zoom Phone

Opinionated REST api client for Zoom Phone.

See Zoom API documentation on marketplace.zoom.us

This repo is currently under development and the endoints below are still outstanding:

* /phone/blocked_list
* /phone/call_queues/
* /phone/devices
* /phone/shared_line_groups/
* /phone/sites
* /phone/common_area_phones


## Package Installation




```bash
pip install simple-zoomphone
```

## Example Package Usage
```
from simple-zoomphone import ZoomAPIClient

zoomapi = ZoomAPIClient(
    API_KEY=" <Zoom API KEY here> ", API_SECRET=" <Zoom API Secret here>  "
)

result = zoomapi.users.list_users()
print(result)

result = zoomapi.phone.list_users()
print(result)
```

## Sample Script Usage

### Zoom Phone User Provisioning

user_provisioning.py -h

user_provisioning.py -API_KEY <API_KEY> -API_SECRET <API_SECRET> -email bill.smith@email.com -site_name "Los Angeles" -calling_plan_name "Zoom Phone Pro" -phone_number "auto"

### Call Log Exporter

call_logs.py -h

call_logs.py -API_KEY <API_KEY> -API_SECRET <API_SECRET> -from_date 2019-12-31 -number_of_days 30 -department "Sales" -job_title "Inside Sales Representative" -call_direction all

### Call Recording Exporter

Download call recordings MP3 files. Specify email address for a single user or omit for all users
call_recordings.py -h

call_recordings.py -API_KEY <API_KEY> -API_SECRET <API_SECRET> -email bill.smith@email.com
