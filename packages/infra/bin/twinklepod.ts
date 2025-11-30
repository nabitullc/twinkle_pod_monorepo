#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { StorageStack } from '../lib/storage-stack';
import { DatabaseStack } from '../lib/database-stack';
import { AuthStack } from '../lib/auth-stack';
import { ApiStack } from '../lib/api-stack';
import { AmplifyStack } from '../lib/amplify-stack';
import { PipelineStack } from '../lib/pipeline-stack';

const app = new cdk.App();

const stage = app.node.tryGetContext('stage') || 'beta';
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
};

// Application stacks
const storageStack = new StorageStack(app, `TwinklePod-Storage-${stage}`, { env, stage });
const databaseStack = new DatabaseStack(app, `TwinklePod-Database-${stage}`, { env, stage });
const authStack = new AuthStack(app, `TwinklePod-Auth-${stage}`, { env, stage });

// API stack (depends on auth and database)
const apiStack = new ApiStack(app, `TwinklePod-Api-${stage}`, {
  env,
  stage,
  userPoolId: authStack.userPoolId,
  userPoolClientId: authStack.userPoolClient.userPoolClientId,
  tablesArns: {
    users: databaseStack.usersTable.tableArn,
    children: databaseStack.childProfilesTable.tableArn,
    stories: databaseStack.storiesTable.tableArn,
    progress: databaseStack.progressTable.tableArn,
    events: databaseStack.eventsTable.tableArn,
  },
  tableNames: {
    users: databaseStack.usersTable.tableName,
    children: databaseStack.childProfilesTable.tableName,
    stories: databaseStack.storiesTable.tableName,
    progress: databaseStack.progressTable.tableName,
    events: databaseStack.eventsTable.tableName,
  },
});

// Amplify stack (depends on API and Auth)
new AmplifyStack(app, `TwinklePod-Amplify-${stage}`, {
  env,
  stage,
  apiUrl: `https://${apiStack.restApiId}.execute-api.${env.region}.amazonaws.com/${stage}`,
  userPoolId: authStack.userPoolId,
  userPoolClientId: authStack.userPoolClient.userPoolClientId,
  cloudfrontUrl: storageStack.cloudfrontUrl || '',
});

// Pipeline stack (only for beta/prod, not for local dev)
if (process.env.DEPLOY_PIPELINE === 'true') {
  new PipelineStack(app, `TwinklePod-Pipeline-${stage}`, {
    env,
    stage,
    githubOwner: process.env.GITHUB_OWNER || 'nabitullc',
    githubRepo: 'twinkle_pod_monorepo',
    githubBranch: 'main',
    userPoolId: authStack.userPool.userPoolId,
    userPoolClientId: authStack.userPoolClient.userPoolClientId,
    apiUrl: `https://api-${stage}.twinklepod.com`,
    cloudfrontUrl: `https://cdn-${stage}.twinklepod.com`,
  });
}

app.synth();

