"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.documentClient = void 0;
const dynamodb_toolbox_1 = require("dynamodb-toolbox");
const client_dynamodb_1 = require("@aws-sdk/client-dynamodb");
const lib_dynamodb_1 = require("@aws-sdk/lib-dynamodb");
// Initialize a DynamoDB client
const client = new client_dynamodb_1.DynamoDBClient({ region: 'ap-southeast-2' });
const translateConfig = {
    marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: true
    }
};
exports.documentClient = lib_dynamodb_1.DynamoDBDocumentClient.from(client, translateConfig);
// Define a table
const MyTable = new dynamodb_toolbox_1.Table({
    name: '285833d-table',
    partitionKey: { name: 'PK', type: 'string' },
    sortKey: { name: 'SK', type: 'string' },
    documentClient: exports.documentClient,
    // _et is used for multiple entities in a single table
    entityAttributeSavedAs: 'item'
});
const myEntitySchema = (0, dynamodb_toolbox_1.schema)({
    PK: (0, dynamodb_toolbox_1.string)().key(),
    SK: (0, dynamodb_toolbox_1.string)().key(),
    name: (0, dynamodb_toolbox_1.string)(),
    age: (0, dynamodb_toolbox_1.number)(),
    // ... other attributes
});
// Define an entity
const MyEntity = new dynamodb_toolbox_1.Entity({
    name: 'MyEntity',
    schema: myEntitySchema,
    table: MyTable,
    // disable timestamp _ct and _md (created and modified) _et still
    timestamps: false,
    // entity: A string attribute that tags your items with the Entity name.
    entityAttributeHidden: true,
    entityAttributeName: 'item',
});
// Example: Put an item
(async () => {
    try {
        await MyEntity.build(dynamodb_toolbox_1.PutItemCommand).item({
            PK: 'user#123',
            SK: 'profile',
            name: 'John Doe',
            age: 30,
        }).send();
        console.log('Item inserted');
    }
    catch (error) {
        console.error('Error inserting item:', error);
    }
})();
