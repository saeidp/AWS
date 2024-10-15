import { DynamoDBChatMessageHistory } from "@langchain/community/stores/message/dynamodb";
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
import { BaseMessage } from '@langchain/core/messages';
import { trimMessages } from '@langchain/core/messages';



async function invokeLLM(
    userPrompt: { type: string, text: string }[],
    client: BedrockRuntimeClient
) {
    const command = new InvokeModelCommand({
        modelId: 'anthropic.claude-3-haiku-20240307-v1:0',  // Model ID for Claude 3 Haiku
        contentType: 'application/json',
        accept: 'application/json',
        body: JSON.stringify({
            anthropic_version: "bedrock-2023-05-31",
            max_tokens: 100,
            // temperature: 0.0,
            // top_p: 1.0,
            system: "You are a friendly and concise assistant. Provide accurate and short answers.",
            messages: [
                {
                    role: "user",
                    content: userPrompt
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

const simpleTokenCounter = (messages: BaseMessage[]): number => {
    // treat each message like it adds 3 default tokens at the beginning
    // of the message and at the end of the message. 3 + 4 + 3 = 10 tokens
    // per message.

    const defaultContentLen = 4;
    const defaultMsgPrefixLen = 3;
    const defaultMsgSuffixLen = 3;

    let count = 0;
    for (const msg of messages) {
        if (typeof msg.content === 'string') {
            count += defaultMsgPrefixLen + defaultContentLen + defaultMsgSuffixLen;
        }
        if (Array.isArray(msg.content)) {
            count += defaultMsgPrefixLen + msg.content.length * defaultContentLen + defaultMsgSuffixLen;
        }
    }
    return count;
};

const generateRollingSynopsis = async (history: DynamoDBChatMessageHistory) => {
    const res = await history.getMessages();
    const rollingSynopsis = await trimMessages(res, {
        maxTokens: 20,
        tokenCounter: simpleTokenCounter,
        strategy: 'last',
    });
    return rollingSynopsis
}

const generateQueryPrompt = (rollingSynopsis: BaseMessage[], question: string) => [
    {
        type: "text",
        text: `Here are the documents you have available, provided in <conversation> tags:

                <conversations>
                ${rollingSynopsis.map((message) => `<conversation>${message.content}</conversation>`).join('')}      
                </conversations>      

                <question>${question}</question>

                Using the conversations and the question above, generate a search query to look up and to get information relevant to the conversation. 
                Only respond in XML in the following format: <response><answer>search query</answer></response>`
    }
]



async function main() {
    const client = new BedrockRuntimeClient({ region: 'ap-southeast-2' });
    const history = new DynamoDBChatMessageHistory({
        tableName: "285833d_langchain", partitionKey: "id", sessionId: "1111"
        // if you have sortkey then you can use it as well. By default sessionId is mapped to partitionKey
        // in this scenario using key you can define different values for partitionKey and sortKey
        // tableName: "285833d_langchain", sessionId: "1111",  sortKey:"111111", key: {
        // id: { S: sessionId },
        // sk: { S: sortkey }
        // }

    });

    const rollingSynopsis = await generateRollingSynopsis(history);
    console.log(rollingSynopsis);
    // console.log({ messages: rollingSynopsis.map((m) => JSON.stringify(m.content)) });
    const question = "What did I just say my name was?";
    const userPrompt = generateQueryPrompt(rollingSynopsis, question);
    console.log(userPrompt);
    const result = await invokeLLM(userPrompt, client);
    console.log(result["content"][0]["text"]);








    // ------------------------  getting history ------------------------
    // const res = await history.getMessages();
    // console.log({ res });


    // ---------------------- Add new user and AI prompt to the dynamodb history -------------------
    // const userPrompt = [{
    //     type: "text",
    //     text: "Hi! I'm Saeid"
    // }];
    // const result = await invokeLLM(userPrompt);
    // console.log(result["content"][0]["text"]);
    // history.addUserMessage(userPrompt[0].text);
    // history.addAIMessage(result["content"][0]["text"]);




}

main();
