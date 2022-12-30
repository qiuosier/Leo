import logging

import azure.functions as func

from commons import oauth


# See also:
# https://developers.google.com/identity/protocols/OAuth2WebServer
# https://developers.google.com/identity/protocols/oauth2/scopes
TOKEN_ENDPOINT = "https://www.googleapis.com/oauth2/v4/token"
OAUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

# Set the values of the following variable in environment variables or local.settings.json
# e.g. the environment variable GOOGLE_CLIENT_ID should be set to the Google API client ID
#
# To obtain the client ID and client secret,
# create OAuth Client ID in Google Cloud Console -> APIs & Services -> Credentials.
CLIENT_ID_KEY = "GOOGLE_CLIENT_ID"
CLIENT_SECRET_KEY = "GOOGLE_CLIENT_SECRET"
DEFAULT_SCOPE_KEY = "GOOGLE_DEFAULT_SCOPE"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Authenticate Google function processing a request.')
    return oauth.authorize(req, OAUTH_ENDPOINT, TOKEN_ENDPOINT, CLIENT_ID_KEY, CLIENT_SECRET_KEY, DEFAULT_SCOPE_KEY)
