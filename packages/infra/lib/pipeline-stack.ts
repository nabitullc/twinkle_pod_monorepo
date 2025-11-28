import * as cdk from 'aws-cdk-lib';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

interface PipelineStackProps extends cdk.StackProps {
  stage: string;
  githubOwner: string;
  githubRepo: string;
  githubBranch: string;
  userPoolId?: string;
  userPoolClientId?: string;
  apiUrl?: string;
  cloudfrontUrl?: string;
}

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: PipelineStackProps) {
    super(scope, id, props);

    const sourceOutput = new codepipeline.Artifact();

    // Source: GitHub (monorepo)
    const sourceAction = new codepipeline_actions.GitHubSourceAction({
      actionName: 'GitHub_Source',
      owner: props.githubOwner,
      repo: props.githubRepo,
      branch: props.githubBranch,
      oauthToken: cdk.SecretValue.secretsManager('github-token'),
      output: sourceOutput,
    });

    // Build: CDK Deploy
    const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
      projectName: `twinklepod-${props.stage}`,
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        computeType: codebuild.ComputeType.SMALL,
      },
      environmentVariables: {
        NEXT_PUBLIC_COGNITO_USER_POOL_ID: {
          value: props.userPoolId || '',
        },
        NEXT_PUBLIC_COGNITO_CLIENT_ID: {
          value: props.userPoolClientId || '',
        },
        NEXT_PUBLIC_COGNITO_REGION: {
          value: this.region,
        },
        NEXT_PUBLIC_API_URL: {
          value: props.apiUrl || '',
        },
        NEXT_PUBLIC_CLOUDFRONT_URL: {
          value: props.cloudfrontUrl || '',
        },
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          install: {
            'runtime-versions': {
              nodejs: '20',
            },
            commands: [
              'npm ci',
            ],
          },
          build: {
            commands: [
              'npm run build',
              `cd packages/infra && npx cdk deploy --all --require-approval never --context stage=${props.stage}`,
            ],
          },
        },
      }),
    });

    // Grant CDK deployment permissions
    buildProject.addToRolePolicy(new iam.PolicyStatement({
      actions: ['sts:AssumeRole'],
      resources: [`arn:aws:iam::${this.account}:role/cdk-*`],
    }));

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'CDK_Deploy',
      project: buildProject,
      input: sourceOutput,
    });

    // Pipeline
    new codepipeline.Pipeline(this, 'Pipeline', {
      pipelineName: `twinklepod-${props.stage}`,
      stages: [
        {
          stageName: 'Source',
          actions: [sourceAction],
        },
        {
          stageName: 'Deploy',
          actions: [buildAction],
        },
      ],
    });

    new cdk.CfnOutput(this, 'PipelineName', {
      value: `twinklepod-${props.stage}`,
    });
  }
}
