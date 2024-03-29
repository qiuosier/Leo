using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http.Extensions;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace Leo
{
    // See also: https://developers.google.com/identity/protocols/OAuth2WebServer
    public static class AuthenticateGoogle
    {
        static readonly string TOKEN_ENDPOINT = "https://www.googleapis.com/oauth2/v4/token";
        static readonly string OAUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth";
        static readonly string DEFAULT_SCOPE = "https://www.googleapis.com/auth/gmail.readonly";

        [FunctionName("AuthenticateGoogle")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("HTTP trigger function processed Authenticate Google request.");

            string code = req.Query["code"];
            string scope = req.Query["scope"];
            string redirectUrl = UriHelper.GetDisplayUrl(req);
            log.LogInformation(redirectUrl);
            string redirect = string.IsNullOrEmpty(req.Query["redirect"].ToString()) ? redirectUrl : req.Query["redirect"].ToString();
            
            string clientID = Environment.GetEnvironmentVariable("GoogleClientID");
            string clientSecret = Environment.GetEnvironmentVariable("GoogleClientSecret");

            string endpoint = OAUTH_ENDPOINT;
            string authUrl = endpoint + "?client_id=" + clientID + "&redirect_uri=" + redirect + "&access_type=offline" +
                "&scope=" + DEFAULT_SCOPE +
                "&response_type=code";


            if (code == null) return new RedirectResult(authUrl);

            Dictionary<string, string> data = new Dictionary<string, string>
            {
                { "code", code },
                { "client_id", clientID },
                { "client_secret", clientSecret },
                { "redirect_uri", redirect },
                { "grant_type", "authorization_code" }
            };
            dynamic token_response = Leo.PostJSONResponse(log, TOKEN_ENDPOINT, data);
            log.LogInformation((string)JsonConvert.SerializeObject(token_response));
            dynamic result = token_response.Result;
            return new OkObjectResult(
                $"Code: {code}\n" +
                $"Scope: {scope}\n" +
                $"Access Token: {result?.access_token}\n" +
                $"Refresh Token: {result?.refresh_token}\n" +
                $"Expires In: {result?.expires_in}");
        }

        /// <summary>
        /// Obtain a new access token using the refresh token from environment variable.
        /// </summary>
        /// <param name="log"></param>
        /// <returns></returns>
        public static async Task<string> RefreshAccessToken(ILogger log)
        {
            log.LogInformation("Refreshing Access Token");
            string clientID = Environment.GetEnvironmentVariable("GoogleClientID");
            string clientSecret = Environment.GetEnvironmentVariable("GoogleClientSecret");
            string refreshToken = Environment.GetEnvironmentVariable("GmailRefreshToken");

            // Get access token
            Dictionary<string, string> data = new Dictionary<string, string>
            {
                { "refresh_token", refreshToken },
                { "client_id", clientID },
                { "client_secret", clientSecret },
                { "grant_type", "refresh_token" }
            };
            dynamic token_response = await Leo.PostJSONResponse(log, TOKEN_ENDPOINT, data);
            log.LogInformation((string)JsonConvert.SerializeObject(token_response));
            return token_response?.access_token;
        }
    }
}
