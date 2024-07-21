import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as CdkHelloWorld from '../lib/cdk-hello-world-stack';

const app = new cdk.App();
const stack = new CdkHelloWorld.CdkHelloWorldStack(app, 'MyTestStack');
const template = Template.fromStack(stack);

describe('Test the Starter app', () => {
    test('The app can synthesise fully', () => {
        expect(() => {
            app.synth();
        }).not.toThrow();
    });
});


describe('Hello World', () => {
    test('should have a Lambda function', () => {
        template.hasResourceProperties('AWS::Lambda::Function', {
            Runtime: 'nodejs20.x',
            Handler: 'hello.handler',
        });
    })
});




