import logging
import os

import azure.functions as func
import requests


def authorize(
    req: func.HttpRequest,
    oauth_endpoint: str,
    token_endpoint: str,
    client_id_key: str,
    client_secret_key: str,
    default_scope_key: str = None
):
    """This function is designed to authenticate with OAuth APIs and obtain the access token and refresh token.

    Parameters
    ----------
    req : HttpRequest
        Http request of the Azure function
    oauth_endpoint : str
        URL of the OAuth authorization endpoint.
    token_endpoint : str
        URL of the OAuth token endpoint.
    client_id_key : str
        The name of the environment variable storing the OAuth client ID.
    client_secret_key : str
        The name of the environment variable storing the OAuth client secret.
    default_scope_key : str, optional
        The name of the environment variable storing the default scope for the authorization, by default None.

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    EnvironmentError
        If client ID or client secret is not found in the environment variables.
    """

    if req.params.get('error'):
        return func.HttpResponse(str(req.params), status_code=400)

    client_id = os.environ.get(client_id_key)
    client_secret = os.environ.get(client_secret_key)

    if not client_id:
        raise EnvironmentError(f"{client_id_key} not found in environment variable.")
    if not client_secret:
        raise EnvironmentError(f"{client_secret_key} not found in environment variable.")

    default_scope = os.environ.get(default_scope_key) if default_scope_key else None
    scope = req.params.get('scope', default_scope)
    if not scope:
        return func.HttpResponse("Please specify the scope.", status_code=400)

    redirect_uri = req.params.get('redirect_url', req.url.split("?", 1)[0])
    code = req.params.get('code')
    logging.info(f"Scope: {scope}")
    logging.info(f'Redirect URL: {redirect_uri}')

    if not code:
        auth_url = f"{oauth_endpoint}?client_id={client_id}&redirect_uri={redirect_uri}&access_type=offline" \
            f"&scope={scope}&response_type=code"
        message = f"Redirecting to: {auth_url}"
        logging.info(message)
        return func.HttpResponse(
            message,
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
    token_response = requests.post(token_endpoint, data)
    logging.info(f"Token Response: {token_response}")
    return func.HttpResponse(token_response.content, status_code=200)