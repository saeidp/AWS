import * as fs from 'fs';
import * as path from 'path';
import { APIGatewayProxyHandler } from 'aws-lambda';
import type { Handler } from 'aws-lambda';

// Define the type for the objects in the JSON file
interface Item {
  ID: number;
  Name: string;
  description: string;
}

// const corsHeaders = {
//   'Access-Control-Allow-Origin': '*',
//   'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
//   'Access-Control-Allow-Methods': 'OPTIONS,GET'
// };
// The handler function
export const handler: Handler = async (event: any) => {

  try {
    // Path to the data.json file inside the Lambda environment
    const filePath = path.join(__dirname, 'data.json');

    // Read and parse the file
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const items: Item[] = JSON.parse(fileContent);

    // Return the items as a JSON response
    return {
      statusCode: 200,
      body: JSON.stringify(items),
      headers: {
          "Content-Type": "application/json", // Ensures JSON response
      },

    };
  } catch (error) {
    console.error('Error reading or parsing the file:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Internal Server Error' }),
    };
  }

}
