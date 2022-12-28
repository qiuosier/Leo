import logging

import azure.functions as func

from commons import oauth


# See also: 
# https://docs.microsoft.com/en-us/graph/overview
# https://docs.microsoft.com/en-us/graph/auth-v2-user#authorization-request
# 
# Register application on Azure Active Directory admin center
# https://aad.portal.azure.com/
# Azure Active Directory -> App registrations
# to obtain client ID and client secret.
# Make sure to add the redirect URI to Web Redirect URIs.
TOKEN_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
OAUTH_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/"

# Set the values of the following variable in environment variables or local.settings.json
# e.g. the environment variable MS_GRAPH_CLIENT_ID should be set to the Microsoft Graph client ID
CLIENT_ID_KEY = "MS_GRAPH_CLIENT_ID"
CLIENT_SECRET_KEY = "MS_GRAPH_CLIENT_SECRET"
DEFAULT_SCOPE_KEY = "MS_GRAPH_DEFAULT_SCOPE"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Authenticate Microsoft Graph function processing a request.')
    return oauth.authorize(req, OAUTH_ENDPOINT, TOKEN_ENDPOINT, CLIENT_ID_KEY, CLIENT_SECRET_KEY, DEFAULT_SCOPE_KEY)
