# TwinklePod Monorepo

Monorepo for TwinklePod MVP - Infrastructure, API, and UI in one place.

## Structure

```
twinklepod/
├── packages/
│   ├── infra/    # AWS CDK infrastructure
│   ├── api/      # Lambda functions (Node.js/TypeScript)
│   └── ui/       # Next.js frontend (coming soon)
└── package.json  # Root workspace config
```

## Quick Start

```bash
# Install all dependencies
npm install

# Build all packages
npm run build

# Deploy to AWS
npm run deploy

# Or deploy specific stage
cd packages/infra && npx cdk deploy --all --context stage=beta
```

## Development

```bash
# Build specific package
npm run build:infra
npm run build:api
npm run build:ui

# Work in a package
cd packages/api
npm run build
```

## Pipeline

CodePipeline automatically deploys on push to `main` branch:
1. Checks out monorepo
2. Runs `npm ci` (installs all workspaces)
3. Runs `npm run build` (builds all packages)
4. Deploys with CDK

## Packages

### @twinklepod/infra
CDK infrastructure stacks (Storage, Database, Auth, API Gateway)

### @twinklepod/api
Lambda function handlers for API endpoints

### @twinklepod/ui
Next.js frontend (coming in Week 1)
