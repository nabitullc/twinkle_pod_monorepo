import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { QueryCommand, GetCommand } from '@aws-sdk/lib-dynamodb';
import { GetObjectCommand, S3Client } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { docClient, TableNames } from '../utils/dynamodb';
import { success, error } from '../utils/response';

const s3Client = new S3Client({ region: process.env.AWS_REGION || 'us-east-1' });
const BUCKET_NAME = process.env.S3_BUCKET_NAME || 'twinklepod-stories-beta';

export const list = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const { category, age_range, page = '1', limit = '20' } = event.queryStringParameters || {};
    
    let pk = 'PUBLISHED#true';
    if (category) {
      pk = `CATEGORY#${category}`;
    } else if (age_range) {
      pk = `AGE#${age_range}`;
    }
    
    const result = await docClient.send(new QueryCommand({
      TableName: TableNames.STORIES,
      KeyConditionExpression: 'pk = :pk',
      ExpressionAttributeValues: {
        ':pk': pk,
      },
      Limit: parseInt(limit),
      ScanIndexForward: false, // newest first
    }));

    return success({
      stories: result.Items || [],
      page: parseInt(page),
      limit: parseInt(limit),
      total: result.Count || 0,
    });
  } catch (err: any) {
    return error(err.message || 'Failed to list stories', 500);
  }
};

export const get = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const storyId = event.pathParameters?.id;
    if (!storyId) return error('Story ID is required', 400);

    const result = await docClient.send(new GetCommand({
      TableName: TableNames.STORIES,
      Key: { 
        pk: storyId,
        sk: storyId
      },
    }));

    if (!result.Item) {
      return error('Story not found', 404);
    }

    // Generate signed URL for story JSON
    const s3Key = result.Item.s3_key;
    const signedUrl = await getSignedUrl(
      s3Client,
      new GetObjectCommand({
        Bucket: BUCKET_NAME,
        Key: s3Key,
      }),
      { expiresIn: 3600 } // 1 hour
    );

    return success({
      ...result.Item,
      s3_url: signedUrl,
    });
  } catch (err: any) {
    return error(err.message || 'Failed to get story', 500);
  }
};
