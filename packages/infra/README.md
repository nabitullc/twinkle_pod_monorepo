# TwinklePod Infrastructure

AWS CDK infrastructure for TwinklePod MVP.

## Stacks

- **StorageStack**: S3 bucket + CloudFront for story content
- **DatabaseStack**: DynamoDB tables (users, child_profiles, stories, progress, events)
- **AuthStack**: Cognito User Pool for authentication

## Setup

```bash
npm install
npm run build
```

## Deploy

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks to beta
cdk deploy --all

# Deploy to specific stage
cdk deploy --all --context stage=prod
```

## Useful Commands

- `npm run build` - Compile TypeScript
- `cdk synth` - Synthesize CloudFormation templates
- `cdk diff` - Compare deployed stack with current state
- `cdk deploy` - Deploy stacks to AWS
- `cdk destroy` - Remove stacks from AWS

## Outputs

After deployment, note these outputs:
- S3 bucket name
- CloudFront distribution domain
- DynamoDB table names
- Cognito User Pool ID and Client ID

See [twinkle_pod_specs](https://github.com/nabitullc/twinkle_pod_specs) for complete specifications.
