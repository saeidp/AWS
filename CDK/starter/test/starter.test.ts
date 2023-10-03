import * as cdk from 'aws-cdk-lib';
import { StarterStack } from '../lib/starter-stack';

const app = new cdk.App();

describe('Test the Starter app', () => {
    test('The app can synthesise fully', () => {
        expect(() => {
            app.synth();
        }).not.toThrow();
    });

    test('Creates the stack without exception', () => {
        expect(() => {
            new StarterStack(app, 'my-cdk-Stack', {
                appConfig: { appName: 'starter', envName: 'dev' },
                env: { account: 'fakeaccount', region: 'fakeregion' }
            });
        }).not.toThrow();
    });
});
