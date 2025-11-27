import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({ region: process.env.AWS_REGION || 'us-east-1' });

export const docClient = DynamoDBDocumentClient.from(client, {
  marshallOptions: {
    removeUndefinedValues: true,
  },
});

export const TableNames = {
  USERS: process.env.DYNAMODB_USERS_TABLE || 'twinklepod-users-beta',
  CHILDREN: process.env.DYNAMODB_CHILDREN_TABLE || 'twinklepod-child-profiles-beta',
  STORIES: process.env.DYNAMODB_STORIES_TABLE || 'twinklepod-stories-beta',
  PROGRESS: process.env.DYNAMODB_PROGRESS_TABLE || 'twinklepod-progress-beta',
  EVENTS: process.env.DYNAMODB_EVENTS_TABLE || 'twinklepod-events-beta',
};
