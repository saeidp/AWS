import cdk = require("@aws-cdk/core");
import lambda = require("@aws-cdk/aws-lambda");
import s3 = require("@aws-cdk/aws-s3");
import { S3EventSource } from "@aws-cdk/aws-lambda-event-sources";
import { Duration } from "@aws-cdk/core";
import { PolicyStatement, Effect } from "@aws-cdk/aws-iam";
import iam = require("@aws-cdk/aws-iam");
export class DprEmailLambdaCdkStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    let bucketName = this.node.tryGetContext("s3_bucket_name");
    const bucket = new s3.Bucket(this, bucketName, {
      // the default removal policy is RETAIN, which means that cdk destroy will not attempt to delete
      // the new bucket, and it will remain in your account until manually deleted. By setting the policy to
      // dESTROY, cdk destroy will attempt to delete the bucket, but will error if the bucket is not empty.
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      bucketName: bucketName
    });

    let lambdaName = this.node.tryGetContext("lambda_name");
    const handler = new lambda.Function(this, lambdaName, {
      runtime: lambda.Runtime.DOTNET_CORE_2_1,
      code: lambda.AssetCode.fromAsset(
        // path to bundle or the actual zip file.
        "../DprEmail.Lambda/dpr.email.zip"
      ),
      handler:
        "DprEmail.Lambda::DprEmail.Lambda.Function::FunctionHandlerAsync",
      functionName: lambdaName,
      memorySize: 512,
      timeout: Duration.minutes(5)
    });

    bucket.grantReadWrite(handler);

    const statement = new PolicyStatement();
    const arns = ["*"];
    const actions = ["ses:*"];
    statement.addResources(...arns);
    statement.addActions(...actions);
    statement.effect = Effect.ALLOW;

    handler.addToRolePolicy(statement);

    handler.addEventSource(
      new S3EventSource(bucket, {
        events: [s3.EventType.OBJECT_CREATED_PUT],
        filters: [{ suffix: ".pdf" }]
      })
    );

    // create a user mainly to be used by an automated code to push dpr to s3
    const userName = this.node.tryGetContext("user_name");
    const user = new iam.User(this, "myUser", {
      userName: userName
    });
    const accessKey = new iam.CfnAccessKey(this, "myAccessKey", {
      userName: user.userName
    });

    new cdk.CfnOutput(this, "accessKeyId", { value: accessKey.ref });
    new cdk.CfnOutput(this, "secretAccessKey", {
      value: accessKey.attrSecretAccessKey
    });

    const userStatement = new PolicyStatement();
    const user_arns = ["*"];
    const user_actions = ["s3:*"];
    userStatement.addResources(...user_arns);
    userStatement.addActions(...user_actions);
    userStatement.effect = Effect.ALLOW;
    user.addToPolicy(userStatement);
  }
}
