import { Duration } from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Construct } from 'constructs';
import * as path from 'path';

export class BundlePythonFunctionLambda extends Construct {

    constructor(scope: Construct, id: string) {
        super(scope, id);
        const pyLambda = new PythonFunction(this, "py-lambda,", {
            entry: path.join(__dirname, '../../../../applications/bundle-python-function'), // required
            index: 'bundle_python_function.py', // optional, defaults to 'index.py'
            handler: 'lambda_handler', // optional, defaults to 'handler'
            runtime: lambda.Runtime.PYTHON_3_10,
        })
    }
}