import json
import logging
import os

import azure.functions as func
from commons.microsoft import OneDriveAPI


ONEDRIVE_ID = os.environ.get("MS_GRAPH_CLIENT_ID")
ONEDRIVE_SECRET = os.environ.get("MS_GRAPH_CLIENT_SECRET")
ONEDRIVE_TOKEN = os.environ.get("ONEDRIVE_REFRESH_TOKEN")
ONEDRIVE_SCOPE = "Files.ReadWrite.All"
ONEDRIVE_FILE_PREFIX = os.environ.get("RING_FILE_PREFIX", "/Ring")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Running integration tests...')

    # Tests OneDrive APIs
    onedrive = OneDriveAPI(ONEDRIVE_ID, ONEDRIVE_SECRET, ONEDRIVE_TOKEN, ONEDRIVE_SCOPE)
    onedrive_tests = [
        {
            "name": "Get user folder info under root",
            "path": "/MyFolder"
        },
        {
            "name": "Get user file info under root",
            "path": "Getting started with OneDrive.pdf"
        },
        {
            "name": "Get shared folder info",
            "path": "/Ring"
        },
        {
            "name": "Get info of a folder inside the shared folder",
            "path": "/Ring/Sheets"
        },
        {
            "name": "Get info of a file inside the shared folder",
            "path": "/Ring/test.txt"
        },
    ]
    for test_case in onedrive_tests:
        try:
            logging.info(onedrive.get_item_info(test_case.get("path")))
            test_case["status"] = "passed"
        except:
            test_case["status"] = "failed"


    return func.HttpResponse(
        json.dumps({"tests": onedrive_tests}),
        status_code=200,
        mimetype="application/json"
    )
