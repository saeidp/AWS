import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({ region: 'ap-southeast-2' });  // Adjust to your region
async function invokeClaude3Haiku(prompt) {
    const command = new InvokeModelCommand({
        modelId: 'anthropic.claude-3-haiku-20240307-v1:0',  // Model ID for Claude 3 Haiku
        contentType: 'application/json',
        accept: 'application/json',
        body: JSON.stringify({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": prompt
                      }]
                }
            ]
            
        })
    });

    try {
        // Send the request to the Bedrock model and wait for the response
        const response = await client.send(command);

        // Parse the response body
        const responseBody = JSON.parse(Buffer.from(response.body).toString());
        return responseBody;

    } catch (err) {
        console.error("Error invoking Claude 3 model:", err);
    }
}

export const handler = async (event) => {
    console.log(event);
    // console.log(event["inputTranscript"])
    
    // event["inputTranscript"]
    const result = await invokeClaude3Haiku(event["inputTranscript"]);
    console.log(result["content"][0]["text"]);
    
    const custom_response = {
        messages: [
            {
                "content": result["content"][0]["text"],
                "contentType": "PlainText"
            }
        ],
        requestAttributes: {},
        sessionState: {
            "sessionAttributes": {},
            "dialogAction": {
              "type": "Close",  // This indicates Lex should close the conversation after sending the message
              "fulfillmentState": "Fulfilled"  // Set the fulfillment state
            },        
            "intent": {
                "name": "285833d-intent",
                "slots": {},
                "state": "Fulfilled",
                "confirmationState": "None"
            }
        }
    };

    return custom_response;
};
    