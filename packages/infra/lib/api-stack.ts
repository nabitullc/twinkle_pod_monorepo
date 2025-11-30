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
  tableNames: {
    users: string;
    children: string;
    stories: string;
    progress: string;
    events: string;
  };
}

export class ApiStack extends cdk.Stack {
  public readonly apiUrl: string;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const { stage, userPoolId, userPoolClientId, tablesArns, tableNames } = props;

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

    // Stories handlers
    const listStoriesFn = new lambda.Function(this, 'ListStoriesFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/stories.list',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_STORIES_TABLE: tableNames.stories,
      },
    });

    const getStoryFn = new lambda.Function(this, 'GetStoryFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/stories.get',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_STORIES_TABLE: tableNames.stories,
        S3_BUCKET_NAME: `twinklepod-stories-${stage}`,
      },
    });

    // Progress handlers
    const saveProgressFn = new lambda.Function(this, 'SaveProgressFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/progress.save',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_PROGRESS_TABLE: `twinklepod-progress-${stage}`,
      },
    });

    const getProgressFn = new lambda.Function(this, 'GetProgressFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/progress.getProgress',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_PROGRESS_TABLE: `twinklepod-progress-${stage}`,
      },
    });

    // Interaction handlers
    const saveInteractionFn = new lambda.Function(this, 'SaveInteractionFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/interactions.save',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_EVENTS_TABLE: `twinklepod-events-${stage}`,
      },
    });

    const getLibraryFn = new lambda.Function(this, 'GetLibraryFn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'handlers/interactions.getLibrary',
      code: lambda.Code.fromAsset('../api/dist'),
      role: lambdaRole,
      environment: {
        DYNAMODB_PROGRESS_TABLE: `twinklepod-progress-${stage}`,
        DYNAMODB_EVENTS_TABLE: `twinklepod-events-${stage}`,
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

    // Stories routes (public)
    const stories = api.root.addResource('stories');
    stories.addResource('list').addMethod('GET', new apigateway.LambdaIntegration(listStoriesFn));
    stories.addResource('{id}').addMethod('GET', new apigateway.LambdaIntegration(getStoryFn));

    // Progress routes (protected)
    const apiResource = api.root.getResource('api') || api.root.addResource('api');
    const progress = apiResource.addResource('progress');
    progress.addMethod('POST', new apigateway.LambdaIntegration(saveProgressFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    progress.addMethod('GET', new apigateway.LambdaIntegration(getProgressFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    // Interaction routes (protected)
    const interaction = apiResource.addResource('interaction');
    interaction.addMethod('POST', new apigateway.LambdaIntegration(saveInteractionFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    const library = apiResource.addResource('library');
    library.addMethod('GET', new apigateway.LambdaIntegration(getLibraryFn), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    this.apiUrl = api.url;

    new cdk.CfnOutput(this, 'ApiUrl', { value: api.url });
  }
}
