import { Table, ScanCommand } from 'dynamodb-toolbox';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb'

const client = new DynamoDBClient({ region: 'ap-southeast-2' });

const translateConfig = {
    marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: false
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
});

const scanCommand = MyTable.build(ScanCommand);

(async () => {
    const params = scanCommand.params()
    const { Items } = await scanCommand.send()
    console.log(Items)
})()
