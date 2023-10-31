import * as cdk from 'aws-cdk-lib';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cr from 'aws-cdk-lib/custom-resources';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import fs = require('fs');

export interface CustomResourceProviderProps {
    /**
     * Message to echo
     */
    Message: string;
}

export class CustomResourceProvider extends Construct {
    public readonly response: string;

    constructor(scope: Construct, id: string, props: CustomResourceProviderProps) {
        super(scope, id);


        const onEvent = new lambda.SingletonFunction(this, 'Singleton', {
            uuid: 'f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc',
            code: new lambda.InlineCode(fs.readFileSync('applications/custom-resource-provider-lambda/custom_resource_provider_lambda.py', { encoding: 'utf-8' })),
            handler: 'index.on_event',
            timeout: cdk.Duration.seconds(300),
            runtime: lambda.Runtime.PYTHON_3_9,
        });

        const myProvider = new cr.Provider(this, 'MyProvider', {
            onEventHandler: onEvent,
            // isCompleteHandler: isComplete,        // optional async "waiter" lambda, see custom-resource-handler.py
            logRetention: logs.RetentionDays.ONE_DAY   // default is INFINITE
        });

        const resource = new cdk.CustomResource(this, 'Resource1', { serviceToken: myProvider.serviceToken, properties: props });

        this.response = resource.getAtt('Response').toString();

    }
}