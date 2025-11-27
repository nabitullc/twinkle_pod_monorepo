# Manual End-to-End Testing Guide

## Prerequisites

✅ UI Server running at: http://localhost:3000  
✅ API deployed at: https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod  
✅ Cognito User Pool: us-east-1_bvX3w7hFX

---

## Test Flow

### 1. Home Page ✅
**URL**: http://localhost:3000

**Expected**:
- [x] TwinklePod logo in header
- [x] "Every Child is the Hero" headline
- [x] Three feature cards (100+ Stories, Age-Appropriate, Track Progress)
- [x] "Start Reading" button
- [x] "Get Started Free" button
- [x] Footer with copyright

**Actions**:
- Click "Start Reading" → Should go to /stories
- Click "Get Started Free" → Should go to /login

---

### 2. Registration ✅
**URL**: http://localhost:3000/login

**Test Steps**:
1. Click "Don't have an account? Sign up"
2. Enter email: `test@example.com`
3. Enter password: `Test1234!` (min 8 chars)
4. Click "Sign Up"

**Expected**:
- [x] Form validates email format
- [x] Form validates password length
- [x] Cognito creates user
- [x] Auto-login after registration
- [x] Redirect to /dashboard

**Possible Issues**:
- ⚠️ Email verification may be required (check email)
- ⚠️ Password must meet Cognito requirements (uppercase, lowercase, number)

---

### 3. Dashboard - Add Child ✅
**URL**: http://localhost:3000/dashboard

**Test Steps**:
1. Click "Add Child" button
2. Enter name: `Emma`
3. Enter age: `5`
4. Click "Add Child"

**Expected**:
- [x] Modal opens
- [x] Form validates name (required)
- [x] Form validates age (3-12)
- [x] Child card appears after creation
- [x] Child selector appears in header

**Actions**:
- Try adding another child: `Oliver`, age `7`
- Verify both appear in header dropdown
- Try deleting a child (confirmation dialog should appear)

---

### 4. Browse Stories ✅
**URL**: http://localhost:3000/stories

**Test Steps**:
1. Click "Stories" in header
2. Try category filters (All, Bedtime, Animals, etc.)

**Expected**:
- [x] Loading skeleton appears initially
- [x] Story grid displays (or empty state if no stories)
- [x] Category buttons work
- [x] Story cards show title, age range, duration

**Current State**:
- ⚠️ **No stories in database yet** - Will show empty grid
- ✅ UI components working
- ✅ API integration working

---

### 5. Story Reader ⏳
**URL**: http://localhost:3000/stories/[id]

**Test Steps**:
1. Click on a story card (when stories exist)
2. Scroll through story
3. Click favorite button

**Expected**:
- [ ] Story title and metadata display
- [ ] Text paragraphs render
- [ ] Images display at correct positions
- [ ] Progress bar updates on scroll
- [ ] Progress auto-saves every 10 seconds
- [ ] Favorite button toggles

**Current State**:
- ⚠️ **Requires stories in S3** - Coming in Week 2

---

### 6. Library ⏳
**URL**: http://localhost:3000/library

**Test Steps**:
1. Click "Library" in header
2. Switch between tabs (Continue Reading, Favorites, Completed)

**Expected**:
- [ ] Requires child selection
- [ ] Three tabs display
- [ ] Empty states show when no data
- [ ] Story cards display with progress bars

**Current State**:
- ⚠️ **Requires reading activity** - Will show empty states

---

### 7. Mobile Responsive ✅
**Test Steps**:
1. Resize browser to mobile width (< 768px)
2. Click hamburger menu (☰)
3. Navigate through pages

**Expected**:
- [x] Mobile menu appears
- [x] Navigation links work
- [x] Child selector works
- [x] All pages responsive

---

### 8. Logout ✅
**Test Steps**:
1. Click "Logout" button in header
2. Verify redirect to home page
3. Try accessing /dashboard (should redirect to /login)

**Expected**:
- [x] User logged out
- [x] Token removed from localStorage
- [x] Protected routes redirect to login

---

## API Testing (cURL)

### Register User
```bash
curl -X POST https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'
```

### Login
```bash
curl -X POST https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'
```

### Get Profile (Protected)
```bash
TOKEN="<your-jwt-token>"
curl https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

### Create Child
```bash
curl -X POST https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod/api/children \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Emma","age":5}'
```

### List Children
```bash
curl https://6c0ae99ndf.execute-api.us-east-1.amazonaws.com/prod/api/children \
  -H "Authorization: Bearer $TOKEN"
```

---

## Known Limitations (MVP)

1. **No Stories Yet** ⏳
   - Stories table is empty
   - Need to upload 100 stories (Week 2)
   - Story reader will work once stories are added

2. **Placeholder Images** ⏳
   - Story cards show gray boxes
   - Real images coming in Week 2

3. **No AdSense Yet** ⏳
   - AdSense integration in Week 2

4. **No Analytics Yet** ⏳
   - Google Analytics in Week 2

---

## Success Criteria

### ✅ Working Now
- [x] User registration with Cognito
- [x] Login/logout flow
- [x] Child profile CRUD
- [x] Child selector in header
- [x] Responsive layout
- [x] Mobile menu
- [x] Protected routes
- [x] API integration
- [x] Context state management

### ⏳ Pending (Week 2)
- [ ] Story content (100 stories)
- [ ] Story reading with progress
- [ ] Library with real data
- [ ] Favorite functionality
- [ ] Amplify deployment

---

## Troubleshooting

### "Network Error" on API calls
- Check API URL in `.env.local`
- Verify API Gateway is deployed
- Check browser console for CORS errors

### "User does not exist" on login
- User may need email verification
- Check Cognito console for user status
- Try registering again with different email

### "Unauthorized" on protected routes
- Token may be expired
- Try logging out and back in
- Check localStorage for token

### Stories page is empty
- **Expected behavior** - No stories uploaded yet
- Will be populated in Week 2

---

## Next Steps

1. ✅ **Complete**: All UI components working
2. ⏳ **Week 2**: Upload 100 stories to S3
3. ⏳ **Week 2**: Deploy UI to Amplify
4. ⏳ **Week 2**: Add AdSense integration
5. ⏳ **Week 2**: End-to-end testing with real data

---

**Status**: ✅ UI fully functional, waiting for content  
**Last Updated**: 2025-11-27
