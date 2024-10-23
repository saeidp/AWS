import { Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';

import { execSync } from 'child_process';

export class BundleLocalLambdaTypescript extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const bundleLocalLambdaTypescript = new lambda.Function(this, 'BundleLocalLambdaTypescript', {
            runtime: lambda.Runtime.NODEJS_LATEST,
            handler: 'bundleLocalLambdaTypescript.handler',
            code: lambda.Code.fromAsset('./applications/bundle-local-lambda-typescript', {
                bundling: {
                    image: lambda.Runtime.NODEJS_LATEST.bundlingImage,
                    command: [],
                    local: {
                        tryBundle(outputDir: string) {
                            try {
                                execSync('npm --version');
                            } catch {
                                return false;
                            }

                            const commands = [
                                'cd applications/bundle-local-lambda-typescript',
                                'npm i',
                                `cp -a . ${outputDir}`
                            ];

                            execSync(commands.join(' && '));
                            return true;
                        }
                    }
                }
            }),
            memorySize: 1024,
            functionName: 'bundleLocalLambdaTypescript',
            timeout: Duration.seconds(1)
        });
    }
}