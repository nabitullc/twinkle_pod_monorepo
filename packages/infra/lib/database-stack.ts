import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

interface DatabaseStackProps extends cdk.StackProps {
  stage: string;
}

export class DatabaseStack extends cdk.Stack {
  public readonly usersTable: dynamodb.Table;
  public readonly childProfilesTable: dynamodb.Table;
  public readonly storiesTable: dynamodb.Table;
  public readonly progressTable: dynamodb.Table;
  public readonly eventsTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props: DatabaseStackProps) {
    super(scope, id, props);

    this.usersTable = new dynamodb.Table(this, 'Users', {
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    this.childProfilesTable = new dynamodb.Table(this, 'ChildProfiles', {
      partitionKey: { name: 'child_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.childProfilesTable.addGlobalSecondaryIndex({
      indexName: 'user-index',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
    });

    this.storiesTable = new dynamodb.Table(this, 'Stories', {
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    this.progressTable = new dynamodb.Table(this, 'Progress', {
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.progressTable.addGlobalSecondaryIndex({
      indexName: 'user-child-progress-index',
      partitionKey: { name: 'user_child_key', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'last_read', type: dynamodb.AttributeType.STRING },
    });

    this.eventsTable = new dynamodb.Table(this, 'Events', {
      partitionKey: { name: 'event_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    this.eventsTable.addGlobalSecondaryIndex({
      indexName: 'user-child-events-index',
      partitionKey: { name: 'user_child_key', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
    });
    this.eventsTable.addGlobalSecondaryIndex({
      indexName: 'user-child-story-events-index',
      partitionKey: { name: 'user_child_story_key', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
    });

    new cdk.CfnOutput(this, 'UsersTableName', { value: this.usersTable.tableName });
    new cdk.CfnOutput(this, 'ChildProfilesTableName', { value: this.childProfilesTable.tableName });
    new cdk.CfnOutput(this, 'StoriesTableName', { value: this.storiesTable.tableName });
    new cdk.CfnOutput(this, 'ProgressTableName', { value: this.progressTable.tableName });
    new cdk.CfnOutput(this, 'EventsTableName', { value: this.eventsTable.tableName });
  }
}
