using System;
using System.Collections.Generic;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Leo
{
    public static class TurnOffDevice
    {
        /// <summary>
        /// When triggered by a message from Azure Service Bus, turns off a device by sending out a HTTP GET request.
        /// The message from Azure Service Bus should be a JSON serialized dictionary with two keys:
        /// device: The name of the device([Device Name]) to be turned off.
        ///     The URL for turning off the device by HTTP GET request must be stored as an environment variable with the name "[Device Name]Off".
        ///     For example, if device=light, then the environment variable should be named "lightOff".
        /// sender: Optional. The name of the device triggering the function. This is used in logging only.
        /// </summary>
        /// <param name="myQueueItem">JSON serialized dictionary from Azure Service Bus</param>
        /// <param name="log">Logger</param>
        [FunctionName("TurnOffDevice")]
        public static void Run([ServiceBusTrigger(Leo.turnOffDeviceQueueName, Connection = "ServiceBusConnectionString")]string myQueueItem, ILogger log)
        {
            log.LogInformation($"{DateTime.Now} :: Turn Off Device Queue trigger function processing: {myQueueItem}");
            Dictionary<string, string> dict = JsonConvert.DeserializeObject<Dictionary<string, string>>(myQueueItem);
            dict.TryGetValue("device", out string deviceName);
            if (deviceName != null)
            {
                TurnOffDeviceByHttpRequest(log, deviceName);
            } else
            {
                log.LogError($"\"device\" parameter not found.");
            }
        }

        /// <summary>
        /// Turns off a device by sending a HTTP request.
        /// </summary>
        /// <param name="log">Logger</param>
        /// <param name="deviceName">The name of the device, corresponding to the environment variable defined in settings.</param>
        public static void TurnOffDeviceByHttpRequest(ILogger log, string deviceName)
        {
            string envVariable = deviceName + "Off";
            string deviceOffUrl = Environment.GetEnvironmentVariable(envVariable);
            if (deviceOffUrl != null) Leo.GetHttpResponse(log, deviceOffUrl, 3);
            else log.LogError($"Trigger for turning off {deviceName} not found.");
        }
    }
}
