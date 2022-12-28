# Azure Function to Obtain OAuth 2.0 Tokens from Microsoft Graph
This function is designed to obtain OAuth 2.0 access token and refresh token from Microsoft Graph APIs. The tokens can be used to make further API calls by other functions.

The authorization level of this function is set to anonymous. Because the `code` parameter for Azure function authorization is also used by OAuth. Once OAuth authorization is successful, the OAuth server responds to the request by redirecting the URL with an authorization code in the `code` parameter (e.g. https://oauth2.example.com/auth?code=4/P7q7W91a-oMsCeLvIaQm6bTrgtp7).

To use this function, the following environment variables must be set in the function app:
* `MS_GRAPH_CLIENT_ID`
* `MS_GRAPH_CLIENT_SECRET`
* `MS_GRAPH_DEFAULT_SCOPE`

They can be obtained by registering the application in Azure Active Directory admin center: https://aad.portal.azure.com/ (Azure Active Directory -> App registrations)

See also: 
* https://docs.microsoft.com/en-us/graph/overview
* https://docs.microsoft.com/en-us/graph/auth-v2-user#authorization-request
