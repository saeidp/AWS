import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as appflow from 'aws-cdk-lib/aws-appflow';

export class AppflowCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create an S3 bucket to use as a destination
    const destinationBucket = new s3.Bucket(this, 'Servicenow-Bucket-1258', {
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For testing purposes, remove in production
      autoDeleteObjects: true, // For testing purposes, remove in production
    });

    const bucketPolicy = new iam.PolicyStatement({
      actions: ['s3:*'], // Specify the S3 actions
      resources: [`${destinationBucket.bucketArn}`, `${destinationBucket.bucketArn}/*`], // Grant access to all objects in the bucket
      principals: [new iam.ServicePrincipal('appflow.amazonaws.com')], // Allow access to anyone
    });
    destinationBucket.addToResourcePolicy(bucketPolicy);

    // Create an IAM role for AppFlow
    const appFlowRole = new iam.Role(this, 'AppFlowRole', {
      assumedBy: new iam.ServicePrincipal('appflow.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAppFlowFullAccess'),
      ],
    });

    // Allow AppFlow to access the S3 bucket
    destinationBucket.grantReadWrite(appFlowRole);

    const connectorProfile = new appflow.CfnConnectorProfile(this, 'ServiceNowConnectorProfile', {
      connectionMode: 'Public',
      connectorProfileName: 'ServiceNowProfile1258',
      connectorType: 'Servicenow',
      connectorProfileConfig: {
        connectorProfileProperties: {
          serviceNow: {
            instanceUrl: 'https://curtinsandbox.service-now.com', // ServiceNow instance URL
          },
        },
        // connectorProfileCredentials: {
        //   serviceNow: {
        //     username: serviceNowCredentials.secretValueFromJson('username').toString(),
        //     password: serviceNowCredentials.secretValueFromJson('password').toString(),
        //   },
        connectorProfileCredentials: {
          serviceNow: {
            username: "appFlow.knowledge.connector",
            password: "xxxxxxxxxxxxxxxx"
          },


        },
      },
    });

    const appFlow = new appflow.CfnFlow(this, 'ServiceNowToS3Flow', {
      flowName: 'ia-servicenow-1258',
      triggerConfig: {
        triggerType: 'OnDemand', // Can be 'Scheduled' for scheduled flows
      },

      sourceFlowConfig: {
        connectorType: 'Servicenow', // Specify ServiceNow as the data source
        connectorProfileName: connectorProfile.ref, // Profile created in AWS Console
        sourceConnectorProperties: {
          serviceNow: {
            object: 'kb_knowledge', // Specify the ServiceNow object (table) to pull data from
          },
        },
      },
      destinationFlowConfigList: [
        {
          connectorType: 'S3',
          destinationConnectorProperties: {
            s3: {
              bucketName: destinationBucket.bucketName,
              bucketPrefix: '', // Optional prefix in the bucket
            },
          },
        },
      ],
      tasks: [
        {
          sourceFields: ['number', 'short_description', 'text'], // Fields to be transferred from ServiceNow
          taskType: 'Filter',
          connectorOperator: {
            serviceNow: 'PROJECTION', // No operation, just transfer as is
          },
        },
        {
          sourceFields: ['number'],
          destinationField: 'number',
          taskType: 'Map'
        },
        {
          sourceFields: ['short_description'],
          destinationField: 'short_description',
          taskType: 'Map'
        },
        {
          sourceFields: ['text'],
          destinationField: 'text',
          taskType: 'Map'
        }
      ],
    });
    appFlow.node.addDependency(connectorProfile);
    appFlow.node.addDependency(appFlowRole);
  }
}
