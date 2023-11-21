import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

import path = require("path");


export class DynamodbSimpleLambda extends Construct {
    public readonly table: dynamodb.Table;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        console.log(path.join(__dirname, '../../../../applications/dynamodb-simple-lambda'));

        this.table = new dynamodb.Table(this, 'Person', {
            partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'name', type: dynamodb.AttributeType.STRING },
            tableName: 'Person',
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            // The default removal policy is RETAIN, which means that cdk destroy will not
            // delete the DynamoDB table. If you want the table to be destroyed when the
            // stack is destroyed, uncomment the line below.
            // removalPolicy: cdk.RemovalPolicy.DESTROY, // NOT recommended for production code
        })

        const lambdaFunction = new lambda.Function(this, `dynamodb-simple-lambda`, {
            runtime: lambda.Runtime.PYTHON_3_11,
            memorySize: 1024,
            timeout: cdk.Duration.seconds(5),
            handler: 'dynamodb_simple_lambda.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../../../applications/dynamodb-simple-lambda')),
        });

        this.table.grantReadData(lambdaFunction)

    }
}

