# Azure Function to Obtain OAuth 2.0 Tokens from Google
This function is designed to obtain OAuth 2.0 access token and refresh token from Google APIs. The tokens can be used to make further API calls by other functions.

The authorization level of this function is set to anonymous. Because the `code` parameter for Azure function authorization is also used by OAuth. Once OAuth authorization is successful, the OAuth server responds to the request by redirecting the URL with an authorization code in the `code` parameter (e.g. https://oauth2.example.com/auth?code=4/P7q7W91a-oMsCeLvIaQm6bTrgtp7).

To use this function, the following environment variables must be set in the function app:
* `GOOGLE_CLIENT_ID`
* `GOOGLE_CLIENT_SECRET`
* `GOOGLE_DEFAULT_SCOPE`
