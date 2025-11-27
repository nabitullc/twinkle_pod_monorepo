import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

interface ApiStackProps extends cdk.StackProps {
  stage: string;
  userPoolId: string;
  userPoolClientId: string;
  tablesArns: {
    users: string;
    children: string;
    stories: string;
    progress: string;
    events: string;
  };
}

export class ApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const { stage, userPoolId, userPoolClientId, tablesArns } = props;

    // Lambda execution role
    const lambdaRole = new iam.Role(this, 'LambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    });

    // Grant DynamoDB permissions
    Object.values(tablesArns).forEach(arn => {
      lambdaRole.addToPolicy(new iam.PolicyStatement({
        actions: ['dynamodb:*'],
        resources: [arn, `${arn}/index/*`],
      }));
    });

    // Grant Cognito permissions
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['cognito-idp:*'],
      resources: [`arn:aws:cognito-idp:${this.region}:${this.account}:userpool/${userPoolId}`],
    }));

    // Auth handlers
    const registerFn = new lambda.Function(this, 'RegisterFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/auth.register',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        COGNITO_CLIENT_ID: userPoolClientId,
        DYNAMODB_USERS_TABLE: `twinklepod-users-${stage}`,
      },
    });

    const loginFn = new lambda.Function(this, 'LoginFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/auth.login',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        COGNITO_CLIENT_ID: userPoolClientId,
      },
    });

    const getProfileFn = new lambda.Function(this, 'GetProfileFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/auth.getProfile',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_USERS_TABLE: `twinklepod-users-${stage}`,
      },
    });

    // Children handlers
    const listChildrenFn = new lambda.Function(this, 'ListChildrenFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/children.list',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_CHILDREN_TABLE: `twinklepod-child-profiles-${stage}`,
      },
    });

    const createChildFn = new lambda.Function(this, 'CreateChildFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/children.create',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_CHILDREN_TABLE: `twinklepod-child-profiles-${stage}`,
      },
    });

    const updateChildFn = new lambda.Function(this, 'UpdateChildFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/children.update',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_CHILDREN_TABLE: `twinklepod-child-profiles-${stage}`,
      },
    });

    const deleteChildFn = new lambda.Function(this, 'DeleteChildFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/children.remove',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_CHILDREN_TABLE: `twinklepod-child-profiles-${stage}`,
      },
    });

    // API Gateway
    const api = new apigateway.RestApi(this, 'Api', {
      restApiName: `twinklepod-api-${stage}`,
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // Cognito authorizer
    const userPool = cognito.UserPool.fromUserPoolId(this, 'UserPool', userPoolId);
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'Authorizer', {
      cognitoUserPools: [userPool],
    });

    // Auth routes (public)
    const users = api.root.addResource('users');
    users.addResource('register').addMethod('POST', new apigateway.LambdaIntegration(registerFn));
    users.addResource('login').addMethod('POST', new apigateway.LambdaIntegration(loginFn));
    users.addResource('profile').addMethod('GET', new apigateway.LambdaIntegration(getProfileFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    // Children routes (protected)
    const children = api.root.addResource('api').addResource('children');
    children.addMethod('GET', new apigateway.LambdaIntegration(listChildrenFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    children.addMethod('POST', new apigateway.LambdaIntegration(createChildFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    const childById = children.addResource('{id}');
    childById.addMethod('PUT', new apigateway.LambdaIntegration(updateChildFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    childById.addMethod('DELETE', new apigateway.LambdaIntegration(deleteChildFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    new cdk.CfnOutput(this, 'ApiUrl', { value: api.url });
  }
}
