import { BufferMemory } from "langchain/memory";
import { DynamoDBChatMessageHistory } from "@langchain/community/stores/message/dynamodb";
import { ConversationChain } from "langchain/chains";
import { ChatBedrockConverse } from "@langchain/aws";


const llm = new ChatBedrockConverse({
    model: "anthropic.claude-3-haiku-20240307-v1:0",
    region: "ap-southeast-2",
    maxTokens: 300,
    temperature: 0.1,
    topP: 0.9
    // region: process.env.BEDROCK_AWS_REGION,
    // credentials: {
    //   accessKeyId: process.env.BEDROCK_AWS_ACCESS_KEY_ID!,
    //   secretAccessKey: process.env.BEDROCK_AWS_SECRET_ACCESS_KEY!,
    // },
});


const memory = new BufferMemory({
    chatHistory: new DynamoDBChatMessageHistory({
        tableName: "285833d_langchain",
        partitionKey: "id",
        // sessionId: new Date().toISOString(), // Or some other unique identifier for the conversation
        sessionId: "1111", // Or some other unique identifier for the conversation
        // config: {
        //     region: "us-east-2",
        //     credentials: {
        //         accessKeyId: "<your AWS access key id>",
        //         secretAccessKey: "<your AWS secret access key>",
        //     },
        // },
    }),
});

const model = llm
const chain = new ConversationChain({ llm: model, memory });
async function main() {
    const res1 = await chain.invoke({ input: "Hi! I'm Jim." });
    console.log({ res1 });
    /*
    {
      res1: {
        text: "Hello Jim! It's nice to meet you. My name is AI. How may I assist you today?"
      }
    }
    */

    const res2 = await chain.invoke({ input: "What did I just say my name was?" });
    console.log({ res2 });

}

main();


/*
{
  res1: {
    text: "You said your name was Jim."
  }
}
*/