#!/bin/bash
# Create stories table with composite PK for denormalized records

aws dynamodb create-table \
  --table-name twinklepod-stories-beta-v2 \
  --attribute-definitions \
    AttributeName=pk,AttributeType=S \
    AttributeName=sk,AttributeType=S \
  --key-schema \
    AttributeName=pk,KeyType=HASH \
    AttributeName=sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "✅ Table created: twinklepod-stories-beta-v2"
