#!/usr/bin/env node
import "source-map-support/register";
import cdk = require("@aws-cdk/core");
import { DprEmailLambdaCdkStack } from "../lib/dpr.email.lambda.cdk-stack";

const app = new cdk.App();

new DprEmailLambdaCdkStack(app, `${process.env.STAGE}DprEmailLambdaCdkStack`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});
