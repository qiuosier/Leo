# Authenticate with Google API using OAuth
This function is designed to obtain "refresh token" and "access token" for server-to-server interaction with Google APIs. An access token is used to authenticate with Google APIs. Each access token expires after a certain period, e.g. 3600 seconds. An refresh token can be used to obtain a new access token.

See also: [Using OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)

**Function Name**: AuthenticateGoogle

**Trigger**: HTTP Request

## Environment Variables
This function uses an "OAuth 2.0 Client ID" created from the [Google API Credentials](https://console.developers.google.com/apis/credentials).
* **GoogleClientID**: Client ID obtained from Google API Credentials
* **GoogleClientSecret**: Client Secret obtained from Google API Credentials

## Parameters
* scope: The scope to request for data access.
* redirect: the URL to be redirect to after authentication. The domain of this URL must be added to authorized domains in the Google "OAuth Consent Screen".

See also [OAuth 2.0 API Scopes](https://developers.google.com/identity/protocols/oauth2/scopes).

## Response
This function returns a JSON response once the authentication is finished successfully. The response includes a "refresh token" and a "access token". The "refresh token" can be saved to the environment variable (manually), so that it can be used by other functions to obtain a new access token in the future.

## OAuth Consent Screen
Google requires configuring the OAuth consent screen before users can authenticate.
1. The "scopes" must be added to the "Scopes for Google APIs" section in the OAuth Consent Screen" page before the authentication.
2. The domain hosting this app must be added to the authorized domains.

Although the consent screen requires submission/verification by Google before it is published, this is not needed for personal or internal use with less than 100 users. Google will display "unverified app" warning to users before the consent screen is verified.
