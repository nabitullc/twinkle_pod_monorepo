import * as cdk from 'aws-cdk-lib';
import * as amplify from 'aws-cdk-lib/aws-amplify';
import * as route53 from 'aws-cdk-lib/aws-route53';
import { Construct } from 'constructs';

interface AmplifyStackProps extends cdk.StackProps {
  stage: string;
  apiUrl: string;
  userPoolId: string;
  userPoolClientId: string;
  cloudfrontUrl: string;
  hostedZone: route53.IHostedZone;
}

export class AmplifyStack extends cdk.Stack {
  public readonly appId: string;
  public readonly defaultDomain: string;

  constructor(scope: Construct, id: string, props: AmplifyStackProps) {
    super(scope, id, props);

    const { stage, apiUrl, userPoolId, userPoolClientId, cloudfrontUrl } = props;

    const amplifyApp = new amplify.CfnApp(this, 'App', {
      name: `twinklepod-ui-${stage}`,
      repository: 'https://github.com/nabitullc/twinkle_pod_monorepo',
      accessToken: cdk.SecretValue.secretsManager('github-token').unsafeUnwrap(),
      buildSpec: `version: 1
applications:
  - appRoot: packages/ui
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*`,
      environmentVariables: [
        { name: 'NEXT_PUBLIC_API_URL', value: apiUrl },
        { name: 'NEXT_PUBLIC_COGNITO_USER_POOL_ID', value: userPoolId },
        { name: 'NEXT_PUBLIC_COGNITO_CLIENT_ID', value: userPoolClientId },
        { name: 'NEXT_PUBLIC_COGNITO_REGION', value: this.region },
        { name: 'NEXT_PUBLIC_CLOUDFRONT_URL', value: cloudfrontUrl },
        { name: 'AMPLIFY_MONOREPO_APP_ROOT', value: 'packages/ui' },
      ],
      platform: 'WEB_COMPUTE',
    });

    const branch = new amplify.CfnBranch(this, 'MainBranch', {
      appId: amplifyApp.attrAppId,
      branchName: 'main',
      enableAutoBuild: true,
      framework: 'Next.js - SSR',
    });

    const domain = new amplify.CfnDomain(this, 'Domain', {
      appId: amplifyApp.attrAppId,
      domainName: 'twinklepod.com',
      subDomainSettings: [
        {
          branchName: branch.branchName,
          prefix: stage === 'beta' ? 'stagingbeta' : '',
        },
      ],
    });

    this.appId = amplifyApp.attrAppId;
    this.defaultDomain = amplifyApp.attrDefaultDomain;

    new cdk.CfnOutput(this, 'AppId', { value: amplifyApp.attrAppId });
    new cdk.CfnOutput(this, 'DefaultDomain', { value: amplifyApp.attrDefaultDomain });
    new cdk.CfnOutput(this, 'CustomDomain', { 
      value: stage === 'beta' ? 'https://stagingbeta.twinklepod.com' : 'https://twinklepod.com' 
    });
  }
}
