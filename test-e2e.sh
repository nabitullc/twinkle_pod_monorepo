#!/bin/bash

API_URL="https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod"
UI_URL="http://localhost:3000"

echo "🧪 TwinklePod End-to-End Test"
echo "=============================="
echo ""

# Test 1: UI is running
echo "✓ Test 1: UI Server"
if curl -s "$UI_URL" | grep -q "TwinklePod"; then
    echo "  ✅ UI is running at $UI_URL"
else
    echo "  ❌ UI is not responding"
    exit 1
fi
echo ""

# Test 2: API is accessible
echo "✓ Test 2: API Health"
if curl -s "$API_URL/stories/list" | grep -q "stories"; then
    echo "  ✅ API is accessible at $API_URL"
else
    echo "  ❌ API is not responding"
    exit 1
fi
echo ""

# Test 3: List stories (public endpoint)
echo "✓ Test 3: List Stories (Public)"
STORIES=$(curl -s "$API_URL/stories/list?limit=5")
if echo "$STORIES" | grep -q "story_id"; then
    echo "  ✅ Stories endpoint working"
    echo "  📚 Sample: $(echo $STORIES | jq -r '.[0].title' 2>/dev/null || echo 'N/A')"
else
    echo "  ❌ Stories endpoint failed"
fi
echo ""

# Test 4: Register new user
echo "✓ Test 4: User Registration"
TIMESTAMP=$(date +%s)
TEST_EMAIL="test$TIMESTAMP@twinklepod.com"
TEST_PASSWORD="Test1234!"

REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/users/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$REGISTER_RESPONSE" | grep -q "UserSub"; then
    echo "  ✅ User registration successful"
    echo "  👤 Email: $TEST_EMAIL"
else
    echo "  ⚠️  Registration response: $REGISTER_RESPONSE"
fi
echo ""

# Test 5: Login
echo "✓ Test 5: User Login"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token' 2>/dev/null)

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "  ✅ Login successful"
    echo "  🔑 Token: ${TOKEN:0:20}..."
else
    echo "  ⚠️  Login response: $LOGIN_RESPONSE"
    TOKEN=""
fi
echo ""

# Test 6: Get Profile (protected)
if [ ! -z "$TOKEN" ]; then
    echo "✓ Test 6: Get Profile (Protected)"
    PROFILE=$(curl -s "$API_URL/users/profile" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$PROFILE" | grep -q "email"; then
        echo "  ✅ Profile endpoint working"
        echo "  📧 Email: $(echo $PROFILE | jq -r '.email' 2>/dev/null)"
    else
        echo "  ❌ Profile endpoint failed"
    fi
    echo ""

    # Test 7: Create child profile
    echo "✓ Test 7: Create Child Profile"
    CHILD_RESPONSE=$(curl -s -X POST "$API_URL/api/children" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"Emma","age":5}')
    
    CHILD_ID=$(echo "$CHILD_RESPONSE" | jq -r '.child_id' 2>/dev/null)
    
    if [ ! -z "$CHILD_ID" ] && [ "$CHILD_ID" != "null" ]; then
        echo "  ✅ Child profile created"
        echo "  👧 Name: Emma, Age: 5"
        echo "  🆔 ID: $CHILD_ID"
    else
        echo "  ⚠️  Child creation response: $CHILD_RESPONSE"
    fi
    echo ""

    # Test 8: List children
    echo "✓ Test 8: List Children"
    CHILDREN=$(curl -s "$API_URL/api/children" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$CHILDREN" | grep -q "child_id"; then
        echo "  ✅ Children list working"
        echo "  👶 Count: $(echo $CHILDREN | jq 'length' 2>/dev/null || echo '1')"
    else
        echo "  ❌ Children list failed"
    fi
    echo ""
fi

echo "=============================="
echo "✅ End-to-End Test Complete!"
echo ""
echo "📝 Manual Testing:"
echo "  1. Open $UI_URL in browser"
echo "  2. Click 'Login' and create account"
echo "  3. Add a child profile"
echo "  4. Browse stories"
echo "  5. Read a story (progress tracking)"
echo "  6. Check library tabs"
echo ""
