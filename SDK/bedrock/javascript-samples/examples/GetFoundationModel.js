import { fileURLToPath } from "url";

import {
  BedrockClient,
  GetFoundationModelCommand,
} from "@aws-sdk/client-bedrock";

/**
 * Get details about an Amazon Bedrock foundation model.
 *
 * @return {FoundationModelDetails} - The list of available bedrock foundation models.
 */
export const getFoundationModel = async () => {
  const client = new BedrockClient();

  const command = new GetFoundationModelCommand({
    modelIdentifier: "anthropic.claude-3-haiku-20240307-v1:0",
  });

  const response = await client.send(command);

  return response.modelDetails;
};

// Invoke main function if this file was run directly.
// if (process.argv[1] === fileURLToPath(import.meta.url)) {
//   const model = await getFoundationModel();
//   console.log(model);
// }

const model = await getFoundationModel();
console.log(model);
