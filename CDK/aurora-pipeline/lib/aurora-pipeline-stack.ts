import * as cdk from '@aws-cdk/core';
import { Artifact, IStage, Pipeline } from "@aws-cdk/aws-codepipeline";
import { CloudFormationCreateUpdateStackAction, CodeBuildAction, CodeStarConnectionsSourceAction } from "@aws-cdk/aws-codepipeline-actions";
import { BuildSpec, LinuxBuildImage, PipelineProject } from "@aws-cdk/aws-codebuild";
import { AuroraStack } from './aurora-stack';
export class AuroraPipelineStack extends cdk.Stack {
  private readonly pipeline: Pipeline;
  private readonly auroraPipelineSourceOutput: Artifact;
  private readonly auroraPipelineBuildOutput: Artifact;
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.pipeline = new Pipeline(this, "AuroraPipeline", {
      pipelineName: "AuroraPipeline",
      crossAccountKeys: true,
      restartExecutionOnUpdate: true
    });

    this.auroraPipelineSourceOutput = new Artifact("AuroraPipelineSourceOutput");
    this.auroraPipelineBuildOutput = new Artifact("AuroraPipelineBuildOutput");

    this.pipeline.addStage({
      stageName: "Bitbucket_Source",
      actions: [
        new CodeStarConnectionsSourceAction({
          actionName: 'Pipeline_Source',
          owner: 'data-mesh-foundation',
          repo: 'aurora-pipeline',
          branch: "master",
          output: this.auroraPipelineSourceOutput,
          connectionArn: 'arn:aws:codestar-connections:ap-southeast-2:447421689278:connection/b3a45c41-32b7-4453-96b6-d17e77a9462b',

        }),
      ]
    });
    this.pipeline.addStage({
      stageName: "Build",
      actions: [
        new CodeBuildAction({
          actionName: "Pipeline_Build",
          input: this.auroraPipelineSourceOutput,
          outputs: [this.auroraPipelineBuildOutput],
          project: new PipelineProject(this, "CdkBuildProject", {
            environment: {
              buildImage: LinuxBuildImage.STANDARD_5_0,
            },
            buildSpec: BuildSpec.fromSourceFilename(
              "build-specs/aurora-pipeline-build-spec.yml"
            ),
          }),
        }),
      ],
    });

    this.pipeline.addStage({
      stageName: "Pipeline_Update",
      actions: [
        new CloudFormationCreateUpdateStackAction({
          actionName: "Pipeline_Update",
          stackName: "AuroraPipelineStack",
          templatePath: this.auroraPipelineBuildOutput.atPath("AuroraPipelineStack.template.json"),
          adminPermissions: true,
        }),
      ],
    });

  }

  public addAuroraStage(auroraStack: AuroraStack, stageName: string): IStage {
    return this.pipeline.addStage({
      stageName: stageName,
      actions: [
        new CloudFormationCreateUpdateStackAction({
          actionName: "Aurora_Update",
          account: auroraStack.account,
          region: auroraStack.region,
          stackName: auroraStack.stackName,
          templatePath: this.auroraPipelineBuildOutput.atPath(`${auroraStack.stackName}.template.json`),
          adminPermissions: true,
        })
      ]

    });
  }

}
