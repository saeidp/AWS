import * as fs from "fs";
import * as path from "path";
import {
  APIGatewayProxyEvent,
  APIGatewayProxyResult,
  APIGatewayProxyHandler,
} from "aws-lambda";

// Define the type for the objects in the JSON file
interface Agent {
  ID: number;
  Name: string;
  description: string;
}

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    // Path to the data.json file inside the Lambda environment
    const filePath = path.join(__dirname, "agent.json");

    // Read and parse the file
    const fileContent = fs.readFileSync(filePath, "utf-8");
    const agents: Agent[] = JSON.parse(fileContent);

    // Return the items as a JSON response
    return {
      statusCode: 200,
      body: JSON.stringify(agents),
      // body: JSON.stringify("hello"),

      headers: {
        "Content-Type": "application/json", // Ensures JSON response
      },
    };
  } catch (error) {
    console.error("Error reading or parsing the file:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Internal Server Error" }),
    };
  }
};

(async () => {
  const tokenPath = path.join(__dirname, "token.txt");
  const encodedToken = fs.readFileSync(tokenPath, "utf-8");

  const mockEvent: APIGatewayProxyEvent = {
    headers: {
      Authorization: `Bearer ${encodedToken}`,
    },
    // Add other necessary properties here for the APIGatewayProxyEvent
  } as any;

  const response = await handler(mockEvent, {} as any, {} as any);
  console.log(response);
})();
