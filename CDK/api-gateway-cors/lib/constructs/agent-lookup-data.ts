// This construct creates the Lambda function and API Gateway for the agents service. 
// It  handles CORS in API Gateway and lambda. 
import { BaseLambdaFunction } from '@assembly-line-base/lambda-function';
import { AppConfig } from '@assembly-line-core/common';
import { ApiGatewayRestApi } from '@assembly-line-base/apigateway-restapi';
import { Duration, Stack } from 'aws-cdk-lib';
import { AuthorizationType, LambdaIntegration, MockIntegration, PassthroughBehavior, RestApi, Cors } from 'aws-cdk-lib/aws-apigateway';
import { Code, LayerVersion, Runtime, Tracing } from 'aws-cdk-lib/aws-lambda';
import { Role, ServicePrincipal, Effect, PolicyDocument, PolicyStatement } from 'aws-cdk-lib/aws-iam';

import { Construct } from 'constructs';
import * as path from 'path';


export interface AgentLookupDataProps {
  appConfig: AppConfig;
}

export class AgentLookupData extends Construct {
  private readonly _restApi: RestApi;
  private readonly _apiKeySecret: string;
private readonly _agentLookupLambda: BaseLambdaFunction;
  
  constructor(scope: Construct, id: string, props: AgentLookupDataProps) {
    super(scope, id);
    const { appConfig } = props;
    const { envName } = appConfig;
    const { region, account } = Stack.of(this);

    
    const powertoolsLayer = LayerVersion.fromLayerVersionArn(
      this,
      'PowertoolsLayer',
      `arn:aws:lambda:${region}:094274105915:layer:AWSLambdaPowertoolsTypeScript:29`
    );

    const lambdaRole = new Role(this, 'LambdaExecutionRole', {
      assumedBy: new ServicePrincipal('lambda.amazonaws.com'), // Lambda service
      description: 'Role for Lambda to access DynamoDB read-only',
    });

    // 2. Attach an inline policy to give DynamoDB table read-only access
    lambdaRole.addToPolicy(new PolicyStatement({
      actions: [
        'dynamodb:GetItem',
        'dynamodb:Query',
        'dynamodb:Scan',
        'dynamodb:BatchGetItem',
        'cloudwatch:*',
      ],
      resources: ["*"], // Restrict to specific DynamoDB table
    }));

    
    this._agentLookupLambda = new BaseLambdaFunction(scope, 'agent-Lookup-Lambda', {
      appConfig: appConfig,
      runtime: Runtime.NODEJS_20_X,
      code: Code.fromAsset(path.join(__dirname, '../../lambda'), {
        // exclude: ['*.ts', '../../lambda//folder/*']
      }),
      handler: 'agent-lookup-data.handler',
      memorySize: 512,
      timeout: Duration.minutes(1),
      role: lambdaRole,
      environment: {
        ENVIRONMENT: envName,
        REGION: region,
        POWERTOOLS_SERVICE_NAME: 'agent-lookup-lambda',
        POWERTOOLS_LOGGER_LOG_LEVEL: appConfig.envName !== 'prod' ? 'DEBUG' : 'WARN',
        POWERTOOLS_LOGGER_SAMPLE_RATE: '1.0',
        NODE_OPTIONS: '--enable-source-maps', // see https://docs.aws.amazon.com/lambda/latest/dg/typescript-exceptions.html,
      }
    });

    this._agentLookupLambda.lambdaFunction.addLayers(powertoolsLayer);
    
    const apigateway = new ApiGatewayRestApi(this, 'api-gateway', {
      appConfig,
      description: 'Agent data lookup API',
      cloudWatchRole: true,
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
      }
    });

    const apiResource = apigateway.restApi.root.addResource('api');
    apiResource.addResource('getAgent').addMethod('GET', new LambdaIntegration(this._agentLookupLambda.lambdaFunction));
    
    this._restApi = apigateway.restApi;
    this._apiKeySecret = apigateway.buildApiKey('apiKey');
     
  }
  
  get restApi(): RestApi {
    return this._restApi;
  }

  get apiKeySecret(): string {
    return this._apiKeySecret;
  }
}



