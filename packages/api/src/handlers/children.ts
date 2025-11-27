import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { PutCommand, GetCommand, QueryCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { v4 as uuidv4 } from 'uuid';
import { docClient, TableNames } from '../utils/dynamodb';
import { success, error } from '../utils/response';
import { ChildProfile } from '../types';

const getUserId = (event: APIGatewayProxyEvent): string | null => {
  return event.requestContext.authorizer?.claims?.sub || null;
};

export const list = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const userId = getUserId(event);
    if (!userId) return error('Unauthorized', 401);

    const result = await docClient.send(new QueryCommand({
      TableName: TableNames.CHILDREN,
      IndexName: 'user_id-index',
      KeyConditionExpression: 'user_id = :userId',
      ExpressionAttributeValues: { ':userId': userId },
    }));

    return success({ children: result.Items || [] });
  } catch (err: any) {
    return error(err.message || 'Failed to list children', 500);
  }
};

export const create = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const userId = getUserId(event);
    if (!userId) return error('Unauthorized', 401);

    const body = JSON.parse(event.body || '{}');
    const { name, age } = body;

    if (!name || !age) {
      return error('Name and age are required', 400);
    }

    const child: ChildProfile = {
      child_id: uuidv4(),
      user_id: userId,
      name,
      age: parseInt(age),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    await docClient.send(new PutCommand({
      TableName: TableNames.CHILDREN,
      Item: child,
    }));

    return success(child, 201);
  } catch (err: any) {
    return error(err.message || 'Failed to create child', 500);
  }
};

export const update = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const userId = getUserId(event);
    if (!userId) return error('Unauthorized', 401);

    const childId = event.pathParameters?.id;
    if (!childId) return error('Child ID is required', 400);

    const existing = await docClient.send(new GetCommand({
      TableName: TableNames.CHILDREN,
      Key: { child_id: childId },
    }));

    if (!existing.Item || existing.Item.user_id !== userId) {
      return error('Child not found or unauthorized', 404);
    }

    const body = JSON.parse(event.body || '{}');
    const { name, age } = body;

    const updated: ChildProfile = {
      ...existing.Item as ChildProfile,
      ...(name && { name }),
      ...(age && { age: parseInt(age) }),
      updated_at: new Date().toISOString(),
    };

    await docClient.send(new PutCommand({
      TableName: TableNames.CHILDREN,
      Item: updated,
    }));

    return success(updated);
  } catch (err: any) {
    return error(err.message || 'Failed to update child', 500);
  }
};

export const remove = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const userId = getUserId(event);
    if (!userId) return error('Unauthorized', 401);

    const childId = event.pathParameters?.id;
    if (!childId) return error('Child ID is required', 400);

    const existing = await docClient.send(new GetCommand({
      TableName: TableNames.CHILDREN,
      Key: { child_id: childId },
    }));

    if (!existing.Item || existing.Item.user_id !== userId) {
      return error('Child not found or unauthorized', 404);
    }

    await docClient.send(new DeleteCommand({
      TableName: TableNames.CHILDREN,
      Key: { child_id: childId },
    }));

    return success({ message: 'Child deleted successfully' });
  } catch (err: any) {
    return error(err.message || 'Failed to delete child', 500);
  }
};
