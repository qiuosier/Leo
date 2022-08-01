import logging

import azure.functions as func

from commons import oauth


# See also:
# https://developers.google.com/identity/protocols/OAuth2WebServer
# https://developers.google.com/identity/protocols/oauth2/scopes
TOKEN_ENDPOINT = "https://www.googleapis.com/oauth2/v4/token"
OAUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

# Set the following values in environment variables or local.settings.json
CLIENT_ID_KEY = "GOOGLE_CLIENT_ID"
CLIENT_SECRET_KEY = "GOOGLE_CLIENT_SECRET"
DEFAULT_SCOPE_KEY = "GOOGLE_DEFAULT_SCOPE"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Authenticate Google function processing a request.')
    return oauth.authorize(req, OAUTH_ENDPOINT, TOKEN_ENDPOINT, CLIENT_ID_KEY, CLIENT_SECRET_KEY, DEFAULT_SCOPE_KEY)
