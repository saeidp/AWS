import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import { PythonFunction } from "@aws-cdk/aws-lambda-python";
import * as path from 'path';

export class TsPyLambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // If requirements.txt or Pipfile exists at the entry path, the construct will handle 
    // installing all required modules in a Lambda compatible Docker container according to the runtime.
    const pyLambda = new PythonFunction(this, "py-lambda,", {
      entry: path.join(__dirname, '/../src/lambda/'), // required
      index: 'index.py', // optional, defaults to 'index.py'
      handler: 'lambda_handler', // optional, defaults to 'handler'
      runtime: lambda.Runtime.PYTHON_3_8,
    })

    // This is another way of installing the lambda and dependencies using bash
    // const pyLambda = new lambda.Function(this, 'py-lambda', {
    //   code: lambda.Code.fromAsset(path.join(__dirname, '/../src/lambda/'), {
    //     bundling: {
    //       image: lambda.Runtime.PYTHON_3_8.bundlingImage,
    //       command: [
    //         'bash', '-c',
    //         'pip3 install -r requirements.txt -t /asset-output && cp -au . /asset-output'
    //       ],
    //     },
    //   }),
    //   runtime: lambda.Runtime.PYTHON_3_8,
    //   handler: 'index.lambda_handler',
    //   tracing: lambda.Tracing.ACTIVE,
    //   memorySize: 1024,
    //   timeout: cdk.Duration.seconds(5),
    // });
  
  }

}
