"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.documentClient = void 0;
const dynamodb_toolbox_1 = require("dynamodb-toolbox");
const client_dynamodb_1 = require("@aws-sdk/client-dynamodb");
const lib_dynamodb_1 = require("@aws-sdk/lib-dynamodb");
const client = new client_dynamodb_1.DynamoDBClient({ region: 'ap-southeast-2' });
const translateConfig = {
    marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: false
    }
};
exports.documentClient = lib_dynamodb_1.DynamoDBDocumentClient.from(client, translateConfig);
// Define a table
const MyTable = new dynamodb_toolbox_1.Table({
    name: '285833d-table',
    partitionKey: { name: 'PK', type: 'string' },
    sortKey: { name: 'SK', type: 'string' },
    documentClient: exports.documentClient,
});
const scanCommand = MyTable.build(dynamodb_toolbox_1.ScanCommand);
(async () => {
    const params = scanCommand.params();
    const { Items } = await scanCommand.send();
    console.log(Items);
})();
