import datetime
import logging
import os
import azure.functions as func
import pytz

from Aries import web
from Aries.excel import ExcelFile
from Aries.files import File, TemporaryFile
from Aries.tasks import FunctionTask
from requests.exceptions import ReadTimeout

from commons import ring_security
from commons.microsoft import OneDriveAPI


ONEDRIVE_ID = os.environ.get("MS_GRAPH_CLIENT_ID")
ONEDRIVE_SECRET = os.environ.get("MS_GRAPH_CLIENT_SECRET")
ONEDRIVE_TOKEN = os.environ.get("ONEDRIVE_REFRESH_TOKEN")
ONEDRIVE_SCOPE = "Files.ReadWrite.All"
ONEDRIVE_FILE_PREFIX = os.environ.get("RING_FILE_PREFIX", "/Ring")
# Video within the hours in the history from the trigger time to be saved.
HISTORY_HOURS = 25


def video_file_path(event):
    return os.path.join(
        ONEDRIVE_FILE_PREFIX,
        event.get("created_at").strftime("%Y/%m/%Y%m%d_%H_%M_%S_") + "%s.mp4" % event.get('kind', "")
    )


def new_workbook(file_path):
    excel = ExcelFile()
    excel.append_row(["ID", "Date", "Time", "Kind", "Answered", "Path", "URL"])
    excel.save(file_path)
    return excel


def upload_video_to_onedrive(device, event, onedrive: OneDriveAPI):
    logging.info("Uploading event ID=%s", event.get("id"))
    url = device.recording_url(event.get("id"))
    # Download video to local
    with TemporaryFile() as temp_file_path:
        web.download(url, temp_file_path)
        # Upload video to Onedrive
        file_path = video_file_path(event)
        response = onedrive.upload_file(temp_file_path, file_path, conflict="skip")
        logging.info("Finished uploading video to %s" % file_path)
        return response


def save_video_to_onedrive(device, event):
    event_time = event.get("created_at")
    date_str = event_time.strftime("%Y%m%d")
    time_str = event_time.strftime("%H:%M:%S")
    workbook_path = os.path.join(
        ONEDRIVE_FILE_PREFIX,
        "Sheets/%s.xlsx" % event_time.strftime("%Y%m")
    )
    onedrive = OneDriveAPI(ONEDRIVE_ID, ONEDRIVE_SECRET, ONEDRIVE_TOKEN, ONEDRIVE_SCOPE)
    with TemporaryFile(suffix=".xlsx") as temp:
        try:
            onedrive.download_file(workbook_path, temp)
            excel = ExcelFile(temp)
        except FileNotFoundError:
            logging.info("Creating new Excel file: %s", workbook_path)
            # Create a new Excel file if one is not found
            excel = new_workbook(temp)

        # Check if event is in workbook
        data = excel.get_data_table()
        id_set = {row[0] for row in data}
        # TODO: ID is None?
        if str(event.get("id")) in id_set:
            logging.info("Event ID=%s already exists.", event.get("id"))
            return "skipped"

        response = upload_video_to_onedrive(device, event, onedrive)
        logging.info(response)
        values = [
            str(event.get("id")), 
            date_str, 
            time_str, 
            event.get("kind"), 
            event.get("answered"),
            os.path.join(response.get("parentReference", {}).get("path"), response.get("name")),
            response.get("webUrl")
        ]
        # logging.info(values)
        excel.append_row(values)
        excel.save()
        onedrive.upload_file(temp, workbook_path, conflict="replace")
        return "uploaded"


def save_to_onedrive():
    if not ONEDRIVE_ID or not ONEDRIVE_SECRET or not ONEDRIVE_TOKEN:
        msg = "OneDrive authentication not found or not valid in environment variables."
        logging.error(msg)
        raise EnvironmentError(msg)
    b64_token = os.environ.get("RING_TOKEN")
    if not b64_token:
        msg = "Ring authentication token (RING_TOKEN) not found or not valid in environment variables."
        raise EnvironmentError(msg)

    agent = os.environ.get("RING_AGENT", "N/A")

    ring = ring_security.authenticate_with_b64_token(agent, b64_token)
    ring.update_data()
    devices = ring.devices()
    # Use the following line to show all ring devices.
    # logging.info(devices)
    doorbell = devices.get("authorized_doorbots")[0]
    time_now = datetime.datetime.now(pytz.timezone(doorbell.timezone))
    # Events in the last 25 hours
    events = ring_security.get_events(doorbell, time_now - datetime.timedelta(hours=HISTORY_HOURS), time_now)
    results = []
    for event in events:
        logging.info("Processing event ID=%s, Created at %s", event.get("id"), event.get("created_at"))
        status = event.get("recording", {}).get("status")
        if status == "ready":
            upload_status = FunctionTask(
                save_video_to_onedrive, doorbell, event
            ).run_and_retry(max_retry=10, exceptions=ReadTimeout, retry_pattern="linear", capture_output=False)
        else:
            logging.info("Event ID=%s is not ready.", event.get("id"))
            upload_status = "Not Ready"
        results.append({
            "id": str(event.get("id")),
            "created_at": str(event.get("created_at")),
            "status": upload_status
        })
    return results
