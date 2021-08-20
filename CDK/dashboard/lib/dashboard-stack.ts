import * as cdk from '@aws-cdk/core';
import * as cloudwatch from '@aws-cdk/aws-cloudwatch';
import { LogQueryVisualizationType, LogQueryWidget, GraphWidget, Metric } from "@aws-cdk/aws-cloudwatch";


export class DashboardStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const dashboard = new cloudwatch.Dashboard(this, "myDashboard", {
      dashboardName: 'cdk-dashboard'
    });

    dashboard.addWidgets(new LogQueryWidget({
      logGroupNames: ['/aws/lambda/HelloWorld'],
      view: LogQueryVisualizationType.TABLE,
      queryLines: [
        'fields @timestamp, @message',
      ],
      width: 24
    }));

    const invocationWidget = new GraphWidget({
      width: 24,
      left: [new Metric({
        metricName: 'Invocations',
        namespace: "AWS/Lambda",
        dimensions: { 'FunctionName': 'HelloWorld' },
        statistic: 'sum',
        label: 'Count',
      })]
    });
    const latencyWidget = new GraphWidget({
      width: 24,
      title: 'Durations',
      left: [new Metric({
        metricName: 'Duration',
        namespace: 'AWS/Lambda',
        dimensions: { 'FunctionName': 'HelloWorld' },
        statistic: 'avg',
        label: 'AVG',
      }), new Metric({
        metricName: 'Duration',
        namespace: 'AWS/Lambda',
        dimensions: { 'FunctionName': 'HelloWorld' },
        statistic: 'max',
        label: 'MAX',
      })]
    });
    dashboard.addWidgets(invocationWidget);
    dashboard.addWidgets(latencyWidget);
  }
}
