# CI/CD Pipeline Setup

This guide explains how to set up automated deployments using AWS CodePipeline.

## Architecture

```
GitHub Push → CodePipeline → CodeBuild → CDK Deploy → AWS Resources
```

**Components:**
- **CodePipeline**: Orchestrates the deployment workflow
- **CodeBuild**: Runs `npm install`, `npm test`, and `cdk deploy`
- **GitHub**: Source repository (triggers on push)
- **IAM Roles**: Secure permissions (no credentials stored)

## One-Time Setup

### 1. Store GitHub Token in Secrets Manager

```bash
# Create a GitHub personal access token with 'repo' scope
# https://github.com/settings/tokens/new

aws secretsmanager create-secret \
  --name github-token \
  --secret-string "ghp_your_token_here" \
  --region us-east-1
```

### 2. Bootstrap CDK (if not done)

```bash
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

### 3. Deploy the Pipeline

```bash
# For beta environment
DEPLOY_PIPELINE=true cdk deploy TwinklePod-Pipeline-beta --context stage=beta

# For production environment
DEPLOY_PIPELINE=true cdk deploy TwinklePod-Pipeline-prod --context stage=prod
```

## How It Works

### Automatic Deployments

**Beta Environment:**
- Triggers on push to `beta` branch
- Deploys to beta stage

**Production Environment:**
- Triggers on push to `main` branch
- Deploys to prod stage

### Manual Deployments

You can still deploy manually:

```bash
# Deploy all stacks manually
cdk deploy --all --context stage=beta

# Deploy specific stack
cdk deploy TwinklePod-Storage-beta --context stage=beta
```

## Pipeline Workflow

1. **Source Stage**: Pulls code from GitHub
2. **Deploy Stage**: 
   - Installs dependencies (`npm ci`)
   - Builds TypeScript (`npm run build`)
   - Runs tests (`npm test`)
   - Deploys CDK stacks (`cdk deploy --all`)

## Monitoring

### View Pipeline Status

```bash
# AWS Console
https://console.aws.amazon.com/codesuite/codepipeline/pipelines

# CLI
aws codepipeline get-pipeline-state \
  --name twinklepod-infra-beta
```

### View Build Logs

```bash
# Get latest build ID
BUILD_ID=$(aws codebuild list-builds-for-project \
  --project-name twinklepod-infra-beta \
  --query 'ids[0]' --output text)

# View logs
aws codebuild batch-get-builds \
  --ids $BUILD_ID \
  --query 'builds[0].logs'
```

## Troubleshooting

### Pipeline Fails on CDK Deploy

**Issue**: Insufficient permissions

**Fix**: Ensure CodeBuild role has CDK bootstrap permissions:
```bash
aws iam attach-role-policy \
  --role-name codebuild-twinklepod-infra-beta-service-role \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### GitHub Token Expired

**Fix**: Update secret in Secrets Manager:
```bash
aws secretsmanager update-secret \
  --secret-id github-token \
  --secret-string "ghp_new_token_here"
```

### Pipeline Not Triggering

**Fix**: Check webhook in GitHub:
- Go to repo Settings → Webhooks
- Verify AWS CodePipeline webhook exists
- Check recent deliveries for errors

## Cost Estimate

```yaml
CodePipeline: $1/month (per pipeline)
CodeBuild: $0.005/minute (typically 2-3 minutes per build)
Secrets Manager: $0.40/month (per secret)

Total: ~$2-3/month for beta + prod pipelines
```

## Branch Strategy

```
main (prod)
  ↑
  merge from beta after testing
  ↑
beta (staging)
  ↑
  feature branches
```

**Workflow:**
1. Create feature branch from `beta`
2. Push to feature branch (no deployment)
3. Merge to `beta` → auto-deploys to beta
4. Test in beta environment
5. Merge to `main` → auto-deploys to prod

## Disabling Pipeline

To deploy without pipeline (local development):

```bash
# Don't set DEPLOY_PIPELINE env var
cdk deploy --all --context stage=beta
```

## Next Steps

After pipeline is set up:
1. Push to `beta` branch to trigger first deployment
2. Monitor pipeline in AWS Console
3. Verify stacks deployed successfully
4. Set up CloudWatch alarms for pipeline failures
