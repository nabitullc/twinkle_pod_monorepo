#!/bin/bash
# Simulate pipeline build locally

set -e

echo "=== Simulating Pipeline Build ==="

# Step 1: Install dependencies
echo "Step 1: npm ci"
npm ci

# Step 2: Build infrastructure
echo "Step 2: npm run build"
npm run build

# Step 3: Build API code (if exists)
if [ -d "../twinkle_pod_api" ]; then
  echo "Step 3: Building API code"
  cd ../twinkle_pod_api
  npm ci
  npm run build
  cd ../twinkle_pod_infra
else
  echo "Step 3: Skipping API build (directory not found)"
fi

# Step 4: CDK synth (dry run)
echo "Step 4: CDK synth"
npx cdk synth --context stage=beta

echo "=== Pipeline simulation complete ==="
