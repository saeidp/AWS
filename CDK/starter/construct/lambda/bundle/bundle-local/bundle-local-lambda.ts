
// tested this approach but it didn't work. It fails in cdk synth step

import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';

import { execSync } from 'child_process';
import path = require('path');



export class BundleLocalLambda extends Construct {

    constructor(scope: Construct, id: string) {
        super(scope, id);

        const pythonLambdaFunction = new lambda.Function(this, 'python-lambda', {
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'bundle_local_lambda.handler',
            code: lambda.Code.fromAsset('./applications/bundle-local-lambda', {
                bundling: {
                    image: lambda.Runtime.PYTHON_3_10.bundlingImage,
                    command: [],
                    local: {
                        tryBundle(outputDir: string) {
                            try {
                                execSync('pip --version');
                            } catch {
                                return false;
                            }

                            const commands = [
                                `cd applications/bundle-local-lambda`,
                                `pip install -r requirements.txt -t ${outputDir}`,
                                `cp -a . ${outputDir}`
                            ];

                            execSync(commands.join(' && '));
                            return true;
                        }
                    }
                }
            }),
            memorySize: 1024,
            functionName: 'bundle-local-lambda',
            timeout: Duration.seconds(1)
        });

    }

}