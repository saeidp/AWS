import * as fs from 'fs';
import * as path from 'path';
// import jwt from 'jsonwebtoken'
import * as jwt from 'jsonwebtoken';
import { fileURLToPath } from 'url';

// Construct __dirname manually - because of module in tsconfig
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

interface Agent {
  ID: number;
  Name: string;
  description: string;
}

function readJsonFile(filePath: string): Agent[] {
  try {
    // Read the file synchronously
    const fileContent = fs.readFileSync(filePath, 'utf-8');

    // Parse the JSON content
    const data: Agent[] = JSON.parse(fileContent);

    return data;
  } catch (err) {
    console.error('Error reading or parsing the file:', err);
    return [];
  }
}

function decodeToken(token: string) {

  const decodedToken = jwt.decode(token) as jwt.JwtPayload;
  return decodedToken;  
};

export function getUserGroup(token : jwt.JwtPayload): string {
  try {
    return token['custom:groups']?.toString() || '';
  } catch (error) {
    console.error('Error getting user group:', error);
    return '';
  }
}

export function filterAgentsByUserGroup(agents: Agent[], userGroup: string): Agent[] {
  const agentByGroup = []
  
  if (userGroup.match('PRIV-AIDA-(dev|test|prod)-Health_Science-(admin|users)')) {
    agentByGroup.push(...agents.filter((agent) => agent.Name === 'HEALTH-SCIENCE'));
  }

  if (userGroup.match('PRIV-AIDA-(dev|test|prod)-LITEC-(admin|users)')) {
    agentByGroup.push(...agents.filter((agent) => agent.Name === 'LITEC'));
  }

  return agentByGroup;
}


const filePath = path.join(__dirname, 'agent.json')
const agents = readJsonFile(filePath);

const tokenPath = path.join(__dirname, 'token.txt');
const encodedToken = fs.readFileSync(tokenPath, 'utf-8');

const token = decodeToken(encodedToken)

const userGroup = getUserGroup(token);

const filteredAgents = filterAgentsByUserGroup(agents, userGroup);
console.log(filteredAgents);
  
  



// IIFE
// (async () => {
  
// })()



// // if token is sent as bearer token then use the following code to retrive the token.
// // please also make sure API gateway is configured with Authorization header as Bearer

// const authHeader = event.headers['Authorization'] || event.headers['authorization']; // Case-insensitive
// if (!authHeader || !authHeader.startsWith('Bearer ')) {
//   return {
//     statusCode: 401,
//     body: JSON.stringify({ message: 'Unauthorized' }),
//   };
// }

// // Extract the token by removing "Bearer " from the header value
// const jwtToken = authHeader.slice(7);

// // Proceed with processing the token (e.g., verifying it, extracting data)
// console.log("Received JWT Token:", jwtToken);


// // sending token with fetch example
// const jwtToken = "your-jwt-token";

// fetch('https://your-api-gateway-url.com/endpoint', {
//   method: 'GET', // or 'POST' based on your API
//   headers: {
//     'Authorization': `Bearer ${jwtToken}`, // Send JWT as Bearer token
//     'Content-Type': 'application/json',
//   },
// })
//   .then(response => response.json())
//   .then(data => console.log(data))
//   .catch(error => console.error("Error:", error));