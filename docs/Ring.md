# Trigger Actions base on Ring Alarm Status
_"Turn on the indoor camera when ring alarm is set to **Away**."_

As of early 2020, the [Ring Alarm Security System](https://shop.ring.com/pages/security-system) does not offer any integration with other services or systems. However, it has the option of sending email notifications about the alarm and device status. We can use these email notifications to trigger other actions. This following shows a way to use Azure functions to monitor a Gmail account and receive updates on the Ring alarm security system.

**Function Name**: HomeStatus

**Trigger**: HTTP Request

## Environment Variables
* **TimeZone**. Your local timezone. This is used to convert the timestamp in Gmail message to your local time. The available timezones depends on the system running the Azure function. The Azure server may have different timezones than the ones available on the local computer. Use the [TimeZone](TimeZone.md) function to list all available timezones.
* **GmailRefreshToken**. The refresh token for obtaining access token and accessing Gmail messages, which can be obtained by using the [AuthenticateGoogle](AuthenticateGoogle.md) function.

## Parameters

## Access Gmail Messages
We can setup email notifications in the Ring App to send emails to a Gmail account. Then, we can get the status of the Ring system by reading the emails with Azure function.

This function uses OAuth 2.0 authentication with access Google API. A "Refresh token" is needed to allow Azure functions to access Gmail without user interaction. This can be obtained by using the [AuthenticateGoogle](AuthenticateGoogle.md) function and authorized with the Gmail account receiving ring notifications. The "refresh token" should be stored as the **GmailRefreshToken** environment variable in the Azure function settings.

Since the "refresh token" allows offline access to any messages in the Gmail account. For better security, it is recommended that an independent Gmail account is used for just receiving Ring notifications.

## Set up Push Notifications
The "refresh token" allows this this function to access Gmail in the background. To trigger this function, we need to setup push notification via Google PubSub to send HTTP request.

See also: [Push Notifications](https://developers.google.com/gmail/api/guides/push), [Watch Gmail](https://developers.google.com/gmail/api/v1/reference/users/watch)

## Trigger Actions