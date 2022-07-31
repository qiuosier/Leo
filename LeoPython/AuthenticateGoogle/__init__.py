import logging
import os

import azure.functions as func
import requests


# See also: https://developers.google.com/identity/protocols/OAuth2WebServer
TOKEN_ENDPOINT = "https://www.googleapis.com/oauth2/v4/token"
OAUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

# See also: https://developers.google.com/identity/protocols/oauth2/scopes
DEFAULT_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


def main(req: func.HttpRequest) -> func.HttpResponse:
    """This function is designed to authenticate with Google APIs and obtain the access token and refresh token.

    This function is intended to be used locally or anonymously.
    This function cannot work with function key in URL since
    Azure Function uses the same "code" parameter for the function key to access the function.
 
    Before using this function, config GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET as environment variables.
    They can be obtained from:
    https://console.cloud.google.com/apis/credentials

    Raises
    ------
    EnvironmentError
        If GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not found in the environment variables.
    """
    logging.info('Authenticate Google function processing a request.')

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id:
        raise EnvironmentError("GOOGLE_CLIENT_ID not found in environment variable.")
    if not client_secret:
        raise EnvironmentError("GOOGLE_CLIENT_SECRET not found in environment variable.")

    # The "scope" parameter is used to generate the authorization request.
    # The "redirect_url" parameter specify the URL for Google to redirect to once the user authorized the access.
    # Once authorized, Google will redirect the HTTP GET request with "code" and "scope" as parameter.
    # The "code" and "scope" parameter is used after user signed in with Google and authorized the access.
    scope = req.params.get('scope', DEFAULT_SCOPE)
    redirect_uri = req.params.get('redirect_url', req.url.split("?", 1)[0])
    code = req.params.get('code')
    logging.info(f"Scope: {scope}")
    logging.info(f'Redirect URL: {redirect_uri}')
    
    if not code:
        auth_url = f"{OAUTH_ENDPOINT}?client_id={client_id}&redirect_uri={redirect_uri}&access_type=offline" \
            f"&scope={scope}&response_type=code"
        logging.info(f"Redirecting to: {auth_url}")
        return func.HttpResponse(
            "Redirecting to Google ...",
            status_code=302,
            headers=dict(location=auth_url)
        )

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(TOKEN_ENDPOINT, data)
    logging.info(f"Token Response: {token_response}")
    return func.HttpResponse(token_response.content, status_code=200)
