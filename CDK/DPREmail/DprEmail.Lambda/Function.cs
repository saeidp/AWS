using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.S3Events;
using Amazon.S3;
using Amazon;
using Amazon.S3.Model;
using Amazon.SimpleEmail;
using Amazon.SimpleEmail.Model;
using Auth0.AuthenticationApi;
using Auth0.AuthenticationApi.Models;
using MimeKit;
using Newtonsoft.Json;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.Json.JsonSerializer))]

namespace DprEmail.Lambda
{
    public class Function
    {

        // The email body for recipients with non-HTML email clients.
        private static readonly string s_TextBody = "Daily project Status\r\n";

        // The HTML body of the email.
        private static string s_HtmlBody = @"<html>
        <head></head>
            <body>
              <h1>Daily Project Status</h1>
              <p>
                <a href='https://altitude.next.roames.com'>Altitude</a>
             </body>
        </html>";

        /// <summary>
        /// This method is called for every Lambda invocation. This method takes in an S3 event object and can be used
        /// to respond to S3 notifications.
        /// </summary>
        /// <param name="s3Event"></param>
        /// <param name="context"></param>
        /// <returns></returns>
        public static async Task FunctionHandlerAsync(S3Event s3Event, ILambdaContext context)
        {
            try
            {
                var s3Client = new AmazonS3Client(RegionEndpoint.APSoutheast2);
                string functionName = context.FunctionName;
                context.Logger.LogLine($"Invoking lambda function: {functionName}");

                if (!GetConfigFile(functionName, out string configFile))
                {
                    context.Logger.LogLine($"Unable to find config file: {configFile}");
                    return;
                }

                string path = Path.Combine(Directory.GetCurrentDirectory(), configFile);

                if (!ReadConfig(path, out string clientId, out string clientSecret, out string audience, out string url, out string dprBucketName, out string domain))
                {
                    context.Logger.LogLine($"Unable to extract clientId from config file: {path}");
                    return;
                }


                var accessToken = await GetAccessTokenAsync(clientId, clientSecret, audience, domain).ConfigureAwait(false);
                if (accessToken == null)
                {
                    context.Logger.LogLine($"Unable to get Token from auth0 for clientId: {clientId}");
                    return;
                }

                List<string> recipients = await GetRecipientListAsync(s3Client, context, dprBucketName).ConfigureAwait(false);
                if (recipients.Count == 0)
                {
                    context.Logger.LogLine("Unable to get the recipients");
                    return;
                }

                foreach (var record in s3Event.Records)
                {
                    var bucketName = record.S3.Bucket.Name;
                    var objectKey = record.S3.Object.Key.Replace('+', ' ');
                    context.Logger.LogLine($"Receiving object {objectKey} from bucket {bucketName}");

                    string campaignId = await GetCampaignIdAsync(objectKey, accessToken, url, context).ConfigureAwait(false);

                    if (!string.IsNullOrEmpty(campaignId))
                    {
                        string html = await GetBodyHtmlAsync(url, campaignId, accessToken).ConfigureAwait(false);
                        if (!string.IsNullOrEmpty(html))
                        {
                            s_HtmlBody = html;
                        }

                    }
                    else
                    {
                        context.Logger.LogLine($"Unable to get the campaignId: {campaignId}");

                    }


                    var response = await s3Client.GetObjectAsync(bucketName, objectKey).ConfigureAwait(false);
                    using (var stream = response.ResponseStream)
                    {
                        await SendRawEmailAsync(context, objectKey, stream, recipients).ConfigureAwait(false);
                    }
                }
            }
            catch (Exception e)
            {
                context.Logger.LogLine(e.Message);
                context.Logger.LogLine(e.StackTrace);
                throw;
            }
        }

        private static async Task<string> GetCampaignIdAsync(string objectKey, string token, string url, ILambdaContext context)
        {
            char[] separator = { '_' };
            var parts = objectKey.Split(separator);
            if (parts.Length == 4)
            {
                var projectName = parts[2];

                string path = $"{url}/api/projectList";
                HttpClient client = new HttpClient();
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
                HttpResponseMessage response = await client.GetAsync(path).ConfigureAwait(false);
                if (response.IsSuccessStatusCode)
                {
                    string json = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
                    var projects = JsonConvert.DeserializeObject<List<ProjectDetail>>(json);
                    var projectFound = projects.FirstOrDefault(x => x.Project.Equals(projectName, StringComparison.OrdinalIgnoreCase));
                    if (projectFound != null)
                    {
                        string campaignId = projectFound.CampaignId;
                        context.Logger.Log($"Found CampaignId: {campaignId} from project: {projectName}");
                        return campaignId;
                    }
                }

            }
            return string.Empty;
        }

        private static async Task<List<string>> GetRecipientListAsync(AmazonS3Client s3Client, ILambdaContext context, string dprBucketName)
        {
            string fileName = "recipients.json";
            var recipients = new List<string>();
            try
            {
                GetObjectRequest request = new GetObjectRequest
                {
                    BucketName = dprBucketName,
                    Key = fileName
                };
                GetObjectResponse response = await s3Client.GetObjectAsync(request).ConfigureAwait(false);
                StreamReader reader = new StreamReader(response.ResponseStream);
                var json = await reader.ReadToEndAsync().ConfigureAwait(false);
                if (json.Length > 0)
                {
                    var emailRecipients = JsonConvert.DeserializeObject<List<EmailRecipient>>(json);
                    emailRecipients.ForEach(emailRecipient => recipients.Add(emailRecipient.Email));
                }

                return recipients;
            }
            catch (Exception)
            {
                context.Logger.LogLine($"Unable to get the recipients from {fileName}");
                return recipients;
            }

        }

        private static async Task<string> GetBodyHtmlAsync(string url, string campaignId, string token)
        {
            string html = string.Empty;
            string path = $"{url}/Email/DprSummary?campaignid={campaignId}";
            HttpClient client = new HttpClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            HttpResponseMessage response = await client.GetAsync(path).ConfigureAwait(false);
            if (response.IsSuccessStatusCode)
            {
                html = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            }
            return html;
        }

        private static MemoryStream GetMessageStream(string fileName, Stream fileStream, List<string> recipients)
        {
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress("DPR", "noreply-next@fugro.com.au"));
            recipients.ForEach(recipient => message.To.Add(new MailboxAddress(string.Empty, recipient)));
            message.Subject = "Daily project Status";

            var body = new BodyBuilder()
            {
                HtmlBody = s_HtmlBody,
                TextBody = s_TextBody,
            };
            body.Attachments.Add(fileName, fileStream);

            message.Body = body.ToMessageBody();

            var stream = new MemoryStream();
            message.WriteTo(stream);
            return stream;
        }

        private static async Task SendRawEmailAsync(ILambdaContext context, string fileName, Stream fileStream, List<string> recipients)
        {

            using (var client = new AmazonSimpleEmailServiceClient(RegionEndpoint.APSoutheast2))
            {
                var sendRequest = new SendRawEmailRequest
                {
                    RawMessage = new RawMessage(GetMessageStream(fileName, fileStream, recipients))
                };

                try
                {
                    context.Logger.LogLine("Sending email using Amazon SES...");
                    var response = await client.SendRawEmailAsync(sendRequest).ConfigureAwait(false);
                    context.Logger.LogLine("The email was sent successfully.");
                    context.Logger.LogLine(response.HttpStatusCode.ToString());

                }
                catch (Exception e)
                {
                    context.Logger.LogLine("The email was not sent.");
                    context.Logger.LogLine("Error message: " + e.Message);
                }

            }
        }

        private static bool GetConfigFile(string functionName, out string configFile)
        {
            string configFileTemplate = "dpremail.{0}.config";
            configFile = string.Empty;

            if (functionName.Contains("dev", StringComparison.OrdinalIgnoreCase))
            {
                configFile = string.Format(configFileTemplate, "dev");
            }
            else if (functionName.Contains("uat", StringComparison.OrdinalIgnoreCase))
            {
                configFile = string.Format(configFileTemplate, "uat");
            }
            else if (functionName.Contains("prod", StringComparison.OrdinalIgnoreCase))
            {
                configFile = string.Format(configFileTemplate, "prod");
            }
            else
            {
                return false;
            }

            return true;
        }

        private static bool ReadConfig(string file,
                                            out string clientId,
                                            out string clientSecret,
                                            out string audience,
                                            out string url,
                                            out string dprBucketName,
                                            out string domain)
        {
            bool result = false;
            clientId = string.Empty;
            clientSecret = string.Empty;
            audience = string.Empty;
            url = string.Empty;
            dprBucketName = string.Empty;
            domain = string.Empty;

            try
            {
                if (File.Exists(file))
                {
                    /* get file contents */
                    string[] fileContents = File.ReadAllLines(file);

                    var configCount = fileContents.Length;
                    if (fileContents.Length > 0)
                    {
                        dprBucketName = fileContents[configCount - 6].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];
                        url = fileContents[configCount - 5].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];
                        domain = fileContents[configCount - 4].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];
                        clientId = fileContents[configCount - 3].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];
                        clientSecret = fileContents[configCount - 2].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];
                        audience = fileContents[configCount - 1].Split('=', StringSplitOptions.RemoveEmptyEntries)[1];

                        result = true;
                    }
                }

                return result;
            }
            catch (Exception)
            {
                return false;
            }
        }

        private static async Task<string> GetAccessTokenAsync(string clientId, string clientSecret, string audience, string domain)
        {
            try
            {
                var authenticationApiClient = new AuthenticationApiClient(domain);

                // Get the access token
                var token = await authenticationApiClient.GetTokenAsync(new ClientCredentialsTokenRequest
                {
                    ClientId = clientId,
                    ClientSecret = clientSecret,
                    Audience = audience
                }).ConfigureAwait(false);

                return token.AccessToken;
            }
            catch (Exception)
            {
                return null;
            }
        }

    }
}
