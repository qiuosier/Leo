"""This module contains classes and functions for accessing Microsoft Graph APIs v1.0
https://docs.microsoft.com/en-us/graph/overview?view=graph-rest-1.0
"""
import os
import requests
import logging
from Aries.oauth import OAuth2
from Aries.web import WebAPI, download
from Aries.storage import StorageFile
from Aries.files import TemporaryFile
from Aries.excel import ExcelFile
logger = logging.getLogger(__name__)


AUTH_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/"


class GraphAPI:
    def __init__(self, client_id, client_secret, refresh_token, scope) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.scope = scope
        self.api = self.authenticate()

    def authenticate(self):
        access_token = OAuth2(
            self.client_id, self.client_secret, AUTH_ENDPOINT, TOKEN_ENDPOINT
        ).refresh_access_token(self.refresh_token, self.scope)
        api = WebAPI(GRAPH_ENDPOINT)
        api.add_header(Authorization="Bearer %s" % access_token)
        return api


class OneDriveAPI(GraphAPI):

    CHUNK_SIZE = 327680 * 10

    def get_item_url(self, item_path):
        rel_path = item_path.lstrip("/")
        base = rel_path.split("/", 1)[0]
        remote_info = self.get_item_info_with_url(f"/me/drive/items/root:/{base}").get("remoteItem")

        # remote_info exists for shared item
        if remote_info:
            drive_id = remote_info.get("parentReference", {}).get("driveId")
            item_id = remote_info.get("id")

            if "/" in rel_path:
                # item is inside the shared folder
                file_path = rel_path.split("/", 1)[1]
                return f"/drives/{drive_id}/items/{item_id}:/{file_path}"
            else:
                # item is a shared folder
                return f"/drives/{drive_id}/items/{item_id}"
        return f"/me/drive/items/root:/{rel_path}"

    def get_item_info(self, file_path):
        item_url = self.get_item_url(file_path)
        return self.get_item_info_with_url(item_url)

    def get_item_info_with_url(self, item_url):
        response = self.api.get_json(item_url)
        if "error" in response:
            logging.info(response)
            error_code = response.get("error", {}).get("code")
            if error_code == "itemNotFound":
                raise FileNotFoundError(item_url)
            raise Exception(response.get("error").get("message"))
        return response

    def get_upload_session_url(self, dest_path):
        item_url = self.get_item_url(dest_path)
        return f"{item_url}:/createUploadSession"

    def create_upload_session(self, dest_path, spec=None):
        logging.info("OneDrive path: %s", dest_path)
        upload_session_url = self.get_upload_session_url(dest_path)
        logging.info("Upload Session URL: %s", upload_session_url)
        if not spec:
            spec = {}
        res = self.api.post(upload_session_url, spec)
        if res.status_code == 409:
            raise FileExistsError()
        res = res.json()

        # if "error" in res and res.get("error").get("code") == "InvalidAuthenticationToken":
        #     self.api = authenticate()
        
        upload_url = res.get("uploadUrl")
        if not upload_url:
            logger.error(res)
            raise ValueError()
        return upload_url

    def upload_file(self, source_path, dest_path, conflict="fail"):
        conflict_behavior = conflict
        if conflict == "skip":
            conflict_behavior = "fail"
        spec = {
            "item": {
                "@microsoft.graph.conflictBehavior": conflict_behavior,
                "name": os.path.basename(dest_path)
            }
        }

        try:
            upload_url = self.create_upload_session(dest_path, spec)
            logging.info("Upload URL: %s", upload_url)
        except FileExistsError:
            logger.info("File %s exists." % dest_path)
            if conflict == "skip":
                logger.info("Skipping uploading...")
                return self.get_item_info(dest_path)
            else:
                raise

        with StorageFile.init(source_path, 'rb') as f:
            file_size = f.size
            while True:
                start = f.tell()
                # logger.debug(start)
                chunk = f.read(self.CHUNK_SIZE)
                size = len(chunk)
                headers = {
                    "Content-Length": str(size),
                    "Content-Range": "bytes %s-%s/%s" % (start, start + size - 1, file_size)
                }
                # logger.info(headers)
                res = requests.put(upload_url, chunk, headers=headers)
                if res.status_code not in [200, 201, 202]:
                    logger.info(res.json())
                    raise ValueError("Data upload error")
                if size < self.CHUNK_SIZE:
                    return res.json()

    def download_file(self, onedrive_path, to_path):
        item_url = self.get_item_url(onedrive_path)
        response = self.api.request("GET", f"{item_url}:/content", allow_redirects=False)
        if response.status_code == 302:
            pre_auth_url = response.headers["Location"]
            download(pre_auth_url, to_path)
        else:
            raise FileNotFoundError(onedrive_path)

    def new_workbook(self, file_path):
        with TemporaryFile() as temp_file_path:
            ExcelFile().save(save_as_file_path=temp_file_path)
            self.upload_file(temp_file_path, file_path)

