import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { CognitoIdentityProviderClient, SignUpCommand, InitiateAuthCommand, GetUserCommand } from '@aws-sdk/client-cognito-identity-provider';
import { PutCommand, GetCommand } from '@aws-sdk/lib-dynamodb';
import { docClient, TableNames } from '../utils/dynamodb';
import { success, error } from '../utils/response';
import { User } from '../types';

const cognito = new CognitoIdentityProviderClient({ region: process.env.AWS_REGION || 'us-east-1' });
const CLIENT_ID = process.env.COGNITO_CLIENT_ID || 'hbrnn4qbumoou59854fif8ivv';

export const register = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const body = JSON.parse(event.body || '{}');
    const { email, password } = body;

    if (!email || !password) {
      return error('Email and password are required', 400);
    }

    const signUpResult = await cognito.send(new SignUpCommand({
      ClientId: CLIENT_ID,
      Username: email,
      Password: password,
      UserAttributes: [{ Name: 'email', Value: email }],
    }));

    const user: User = {
      user_id: signUpResult.UserSub!,
      email,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    await docClient.send(new PutCommand({
      TableName: TableNames.USERS,
      Item: user,
    }));

    return success({ message: 'User registered successfully', user_id: user.user_id }, 201);
  } catch (err: any) {
    return error(err.message || 'Registration failed', 500);
  }
};

export const login = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const body = JSON.parse(event.body || '{}');
    const { email, password } = body;

    if (!email || !password) {
      return error('Email and password are required', 400);
    }

    const authResult = await cognito.send(new InitiateAuthCommand({
      ClientId: CLIENT_ID,
      AuthFlow: 'USER_PASSWORD_AUTH',
      AuthParameters: { USERNAME: email, PASSWORD: password },
    }));

    return success({
      access_token: authResult.AuthenticationResult?.AccessToken,
      id_token: authResult.AuthenticationResult?.IdToken,
      refresh_token: authResult.AuthenticationResult?.RefreshToken,
      expires_in: authResult.AuthenticationResult?.ExpiresIn,
    });
  } catch (err: any) {
    return error(err.message || 'Login failed', 401);
  }
};

export const getProfile = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const userId = event.requestContext.authorizer?.claims?.sub;
    if (!userId) {
      return error('Unauthorized', 401);
    }

    const result = await docClient.send(new GetCommand({
      TableName: TableNames.USERS,
      Key: { user_id: userId },
    }));

    if (!result.Item) {
      return error('User not found', 404);
    }

    return success(result.Item);
  } catch (err: any) {
    return error(err.message || 'Failed to get profile', 500);
  }
};
