import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch'
import path = require("path");

export class CloudWatchSimple extends Construct {
    constructor(scope: Construct, id: string,) {
        super(scope, id);
        console.log(path.join(__dirname, '/../../../applications/tagging-lambda'));

        const lambdaFunction = new lambda.Function(this, `cloudwatch-lambda`, {
            runtime: lambda.Runtime.NODEJS_18_X,
            memorySize: 1024,
            timeout: cdk.Duration.seconds(5),
            handler: 'index.main',
            code: lambda.Code.fromAsset(path.join(__dirname, '/../../../applications/cloudwatch-lambda')),
        });
        // define a metric for lambda errors. If no statistics then Sum is used
        const functionErrors = lambdaFunction.metricErrors({
            period: cdk.Duration.minutes(1),
        });

        // define a metric for lambda invocations
        const functionInvocation = lambdaFunction.metricInvocations({
            period: cdk.Duration.minutes(1),
            statistic: cloudwatch.Stats.SUM
        });

        // create an Alarm using the Alarm construct
        new cloudwatch.Alarm(this, 'lambda-errors-alarm', {
            metric: functionErrors,
            threshold: 1,
            comparisonOperator:
                cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            evaluationPeriods: 1,
            alarmDescription:
                'Alarm if the SUM of Errors is greater than or equal to the threshold (1) for 1 evaluation period',
        });

        // create an Alarm directly on the Metric
        functionInvocation.createAlarm(this, 'lambda-invocation-alarm', {
            threshold: 1,
            evaluationPeriods: 1,
            alarmDescription:
                'Alarm if the SUM of Lambda invocations is greater than or equal to the  threshold (1) for 1 evaluation period',
        });



        // If your service soesn't have the function to create metric.
        // manually instantiate a Metric
        // Create alarm for any errors
        // const error_alarm = new cloudwatch.Alarm(this, "error_alarm", {
        //     metric: new cloudwatch.Metric({
        //         namespace: 'cloudmapper',
        //         metricName: "errors",
        //         statistic: "Sum"
        //     }),
        //     threshold: 0,
        //     evaluationPeriods: 1,
        //     datapointsToAlarm: 1,
        //     treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
        //     alarmDescription: "Detect errors",
        //     alarmName: "cloudmapper_errors"
        // });

        // // Create SNS for alarms to be sent to
        // const sns_topic = new sns.Topic(this, 'cloudmapper_alarm', {
        //     displayName: 'cloudmapper_alarm'
        // });

        // // Connect the alarm to the SNS
        // error_alarm.addAlarmAction(new cloudwatch_actions.SnsAction(sns_topic));


    }
}
