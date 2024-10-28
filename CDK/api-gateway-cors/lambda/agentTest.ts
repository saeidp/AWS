import * as fs from 'fs';
import * as path from 'path';
// import jwt from 'jsonwebtoken'
import * as jwt from 'jsonwebtoken';

interface Item {
  ID: number;
  Name: string;
  description: string;
}

function readJsonFile(filePath: string): Item[] {
  try {
    // Read the file synchronously
    const fileContent = fs.readFileSync(filePath, 'utf-8');

    // Parse the JSON content
    const data: Item[] = JSON.parse(fileContent);

    return data;
  } catch (err) {
    console.error('Error reading or parsing the file:', err);
    return [];
  }
}

function decodeToken(token: string) {

  const decoded = jwt.decode(token);
  return decoded;  
} 

// const token = "eyJraWQiOiJ6elVDN3g5MG9TUmlIOVorWlhqZ2t1dGd3Y0lUVkF5S2podlpSU2dtbEZZPSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiQkRmQTBCMDJmRHU1ZUFGbmlreGRvZyIsInN1YiI6ImE5OWU1NGE4LTAwNTEtNzA2Ni1kZjM1LTczM2IyOGZkZTljZCIsImN1c3RvbTpwb3NpdGlvbnR5cGUiOiJTdHVkZW50IiwiY29nbml0bzpncm91cHMiOlsiYXAtc291dGhlYXN0LTJfcDNCUzJLQ2lkX2NoYXRib3QtZGV2LWNvZ25pdG8iXSwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTIuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTJfcDNCUzJLQ2lkIiwiY29nbml0bzp1c2VybmFtZSI6ImNoYXRib3QtZGV2LWNvZ25pdG9fNGNydGt3czBiMl8xaHNkYTgyMHJzbWJpMW5jMm1jZXM0M3hzXzV5YXY3bSIsImdpdmVuX25hbWUiOiJFbW1hIiwibm9uY2UiOiJRWVFHQ1VtSF84SzBaRUJxM0FUSDIzRXhtNFhTUVhWOWxlbUswN3VkZDhCRDQwcTBvaUxVMUdRX3BGbnNNdUVFYk93N1FGVElXejhjSEhaWlNpd24xb1plaTZ3UmhXTWtWc05Nektyd3JYM09ZX1pZUjBZeFpfU3JCMVlza09NWHNSMkNLTndkb2xlZW9jN0pGS2kwME9ORXRMWGJLem1zb1Jya2p4NVItdHMiLCJjdXN0b206Z3JvdXBzIjoiW1BSSVYtQUlEQS1kZXYtSGVhbHRoX1NjaWVuY2UtdXNlcnMsIFBSSVYtQUlEQS1kZXYtQ3VydGluX0Nvbm5lY3QtdXNlcnNdIiwib3JpZ2luX2p0aSI6IjAyM2EyZTUzLTYzYzItNDQ3ZS1iYjA2LTk3NTA0YWMxZjE3MCIsImF1ZCI6IjRpc3RlZjlwNzg2YXU1djJqdWdpcmVvOWlpIiwiaWRlbnRpdGllcyI6W3siZGF0ZUNyZWF0ZWQiOiIxNzI5MjYzNDIzODc1IiwidXNlcklkIjoiNGNSdGtXUzBiMl8xSFNEQTgyMHJTTWJJMW5jMk1DRXM0M1hTXzVZYXY3TSIsInByb3ZpZGVyTmFtZSI6ImNoYXRib3QtZGV2LWNvZ25pdG8iLCJwcm92aWRlclR5cGUiOiJTQU1MIiwiaXNzdWVyIjpudWxsLCJwcmltYXJ5IjoidHJ1ZSJ9XSwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3Mjk1ODYxMTEsImV4cCI6MTcyOTU4OTcxMSwiaWF0IjoxNzI5NTg2MTExLCJmYW1pbHlfbmFtZSI6IldlbGxzIiwianRpIjoiMzc1YTkzNjYtM2FkOC00NzdkLWEyNWQtZTMxM2YwZGQyZDdmIiwiZW1haWwiOiJFbW1hLldlbGxzQHRlc3QuY3VydGluLmVkdS5hdSJ9.CbgXH5kZUzYQdZ5Ea80C1L-B6TOIz4NVKX_mqoFFip_eB4e9TJ-UbjObpU41_WJKpL_cYRXu3NtVbNi_2DhTNN0VxlIjFjyUVel3DfKzLOVU5vZ8fJ9Jjz6Tqep1tuuTm7-gOCPoEFErFcCOH4N_-MSkKMbvkw0_8UFepWRRtBeENFkdVUSC2lalH2FxaeTPID9bOp8eI1reMEFr7pgvl3FwhbU-T3G3SYhJaP3bRl4oTk3NQz4fYPneZNTz0wJmoP2vcMK_kNmVr_1WMwskyV8HAK127teMu-3m8gIBR7NmeSkkzWt5p14iGg7BC9dZxnL_IMdjdYAy23I_Rdbt7g"
// const decodedToken = decodeToken(token)
// console.log(decodedToken)


const filePath = path.join(__dirname, 'agent.json')
const items = readJsonFile(filePath);
console.log(items);





