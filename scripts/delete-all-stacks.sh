#!/bin/bash
set -e

REGION="us-east-1"
STAGE="beta"

echo "=== Deleting TwinklePod Stacks in Correct Order ==="
echo ""

# Function to wait for stack deletion
wait_for_deletion() {
    local stack_name=$1
    echo "Waiting for $stack_name to delete..."
    aws cloudformation wait stack-delete-complete \
        --stack-name "$stack_name" \
        --region "$REGION" 2>/dev/null || true
    echo "✓ $stack_name deleted"
}

# Function to delete stack if it exists
delete_stack() {
    local stack_name=$1
    local status=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --region "$REGION" \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "DOES_NOT_EXIST")
    
    if [ "$status" = "DOES_NOT_EXIST" ]; then
        echo "✓ $stack_name does not exist (already deleted)"
        return
    fi
    
    if [ "$status" = "DELETE_IN_PROGRESS" ]; then
        echo "⏳ $stack_name is already deleting..."
        wait_for_deletion "$stack_name"
        return
    fi
    
    echo "Deleting $stack_name (current status: $status)..."
    aws cloudformation delete-stack \
        --stack-name "$stack_name" \
        --region "$REGION"
    wait_for_deletion "$stack_name"
}

# Delete in reverse dependency order
echo "Step 1: Delete Amplify (depends on API, Auth, Storage)"
delete_stack "TwinklePod-Amplify-$STAGE"

echo ""
echo "Step 2: Delete API (depends on Auth, Database)"
delete_stack "TwinklePod-Api-$STAGE"

echo ""
echo "Step 3: Delete Database stacks (both old and new)"
delete_stack "TwinklePod-Database-v2-$STAGE"
delete_stack "TwinklePod-Database-$STAGE"

echo ""
echo "Step 4: Delete Auth"
delete_stack "TwinklePod-Auth-$STAGE"

echo ""
echo "Step 5: Delete Storage"
delete_stack "TwinklePod-Storage-$STAGE"

echo ""
echo "Step 6: Delete Pipeline"
delete_stack "TwinklePod-Pipeline-$STAGE"

echo ""
echo "=== All stacks deleted successfully ==="
echo ""
echo "Note: DynamoDB tables with RETAIN policy were kept."
echo "To list them: aws dynamodb list-tables --region $REGION --query 'TableNames[?contains(@, \`twinklepod\`)]'"
