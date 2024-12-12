
import { Table, Entity, schema, string, number, PutItemCommand } from 'dynamodb-toolbox';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb'

// Initialize a DynamoDB client
const client = new DynamoDBClient({ region: 'ap-southeast-2' });

const translateConfig = {
    marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: true
    }
}

export const documentClient = DynamoDBDocumentClient.from(
    client,
    translateConfig
)
// Define a table
const MyTable = new Table({
    name: '285833d-table',
    partitionKey: { name: 'PK', type: 'string' },
    sortKey: { name: 'SK', type: 'string' },
    documentClient: documentClient,
    // _et is used for multiple entities in a single table
    entityAttributeSavedAs: 'item'
});

const myEntitySchema = schema({
    PK: string().key(),
    SK: string().key(),
    name: string(),
    age: number(),

    // ... other attributes
});
// Define an entity
const MyEntity = new Entity({
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
        await MyEntity.build(PutItemCommand).item({
            PK: 'user#123',
            SK: 'profile',
            name: 'John Doe',
            age: 30,
        }).send();

        console.log('Item inserted');

    } catch (error) {
        console.error('Error inserting item:', error);
    }
})();
