# Complete Political Voter Management Platform - API Documentation

## 🔐 Authentication Endpoints

### Create Super Admin
```
POST /api/auth/create-super-admin
```

### Login
```
POST /api/auth/login
Body: { "username": "string", "password": "string" }
Returns: { "access_token": "string", "token_type": "bearer", "user": {...} }
```

### Get Current User
```
GET /api/auth/me
Headers: Authorization: Bearer {token}
```

### Register User (Role-based)
```
POST /api/auth/register
Headers: Authorization: Bearer {token}
Body: {
  "username": "string",
  "email": "string",
  "full_name": "string",
  "phone": "string",
  "role": "admin|karyakarta",
  "password": "string"
}
```

### List Users
```
GET /api/auth/users?role=admin
Headers: Authorization: Bearer {token}
```

### Deactivate User
```
PUT /api/auth/users/{user_id}/deactivate
Headers: Authorization: Bearer {token}
```

## 👥 Voter Management Endpoints

### Create Voter
```
POST /api/voters/
Headers: Authorization: Bearer {token}
Body: VoterCreate schema
```

### Get Voters (with Filters)
```
GET /api/voters/?page=1&limit=50&search=query&gender=male&age_min=18&age_max=65&area=xyz&ward=1&booth_number=123&caste=xyz&visited=true&voted=false&assigned_to=user_id
Headers: Authorization: Bearer {token}
Returns: { "voters": [...], "total": 1000, "page": 1, "limit": 50, "pages": 20 }
```

### Get Single Voter
```
GET /api/voters/{voter_id}
Headers: Authorization: Bearer {token}
```

### Update Voter
```
PUT /api/voters/{voter_id}
Headers: Authorization: Bearer {token}
Body: VoterCreate schema
```

### Delete Voter
```
DELETE /api/voters/{voter_id}
Headers: Authorization: Bearer {token}
```

### Assign Voters
```
POST /api/voters/assign
Headers: Authorization: Bearer {token}
Body: {
  "voter_ids": ["id1", "id2"],
  "karyakarta_id": "user_id",
  "mode": "manual"
}
```

### Bulk Update Voters
```
POST /api/voters/bulk-update
Headers: Authorization: Bearer {token}
Body: {
  "voter_ids": ["id1", "id2"],
  "updates": { "voted_status": true }
}
```

### Mark Voter Visited
```
POST /api/voters/{voter_id}/mark-visited
Headers: Authorization: Bearer {token}
```

### Mark Voter Voted
```
POST /api/voters/{voter_id}/mark-voted
Headers: Authorization: Bearer {token}
```

### Get Voter Stats
```
GET /api/voters/stats/summary
Headers: Authorization: Bearer {token}
Returns: {
  "total": 10000,
  "visited": 5000,
  "voted": 3000,
  "pending": 5000,
  "visit_percentage": 50,
  "turnout_percentage": 30,
  "gender_distribution": [...],
  "age_distribution": [...]
}
```

## 📋 Survey Endpoints

### Create Survey Template
```
POST /api/surveys/templates
Headers: Authorization: Bearer {token}
Body: {
  "template_name": "string",
  "questions": [{
    "id": "q1",
    "type": "mcq|yesno|rating|text|number|dropdown|phone",
    "question_text": "string",
    "question_text_marathi": "string",
    "options": ["option1", "option2"],
    "required": true,
    "conditional_logic": {
      "show_if_question_id": "q0",
      "show_if_answer": "yes"
    }
  }],
  "consent_question": "string",
  "is_default": false
}
```

### Get Survey Templates
```
GET /api/surveys/templates
Headers: Authorization: Bearer {token}
```

### Get Single Template
```
GET /api/surveys/templates/{template_id}
Headers: Authorization: Bearer {token}
```

### Submit Survey
```
POST /api/surveys/submit
Headers: Authorization: Bearer {token}
Body: {
  "voter_id": "string",
  "template_id": "string",
  "responses": [{
    "question_id": "q1",
    "answer": "value"
  }],
  "gps_location": {
    "latitude": 18.5204,
    "longitude": 73.8567
  },
  "photos": ["base64_string1", "base64_string2"],
  "audio_notes": ["base64_audio"],
  "device_id": "string"
}
```

### Get Voter Surveys
```
GET /api/surveys/voter/{voter_id}
Headers: Authorization: Bearer {token}
```

### Get My Surveys (Karyakarta)
```
GET /api/surveys/my-surveys
Headers: Authorization: Bearer {token}
```

### Get Survey Statistics
```
GET /api/surveys/statistics
Headers: Authorization: Bearer {token}
```

## 📝 Task Management Endpoints

### Create Task
```
POST /api/tasks/
Headers: Authorization: Bearer {token}
Body: {
  "assigned_to": "user_id",
  "task_type": "visit|survey|follow_up",
  "description": "string",
  "target_voters": ["voter_id1", "voter_id2"],
  "target_area": "string",
  "target_booth": "string",
  "due_date": "2025-12-31T00:00:00"
}
```

### Get My Tasks
```
GET /api/tasks/assigned-to-me?status=pending
Headers: Authorization: Bearer {token}
```

### Update Task Status
```
PUT /api/tasks/{task_id}
Headers: Authorization: Bearer {token}
Body: {
  "status": "pending|in_progress|completed",
  "completion_percentage": 75
}
```

## 📊 Dashboard Endpoints

### Karyakarta Dashboard
```
GET /api/dashboard/karyakarta
Headers: Authorization: Bearer {token}
Returns: {
  "assigned_voters": 500,
  "visited_voters": 300,
  "voted_voters": 150,
  "coverage_percentage": 60,
  "total_surveys": 250,
  "pending_tasks": 5,
  "today_surveys": 10,
  "today_visits": 15
}
```

### Admin Dashboard
```
GET /api/dashboard/admin
Headers: Authorization: Bearer {token}
Returns: {
  "total_voters": 10000,
  "assigned_voters": 8000,
  "visited_voters": 5000,
  "voted_voters": 3000,
  "total_karyakartas": 20,
  "total_surveys": 4500,
  "karyakarta_performance": [...]
}
```

### Super Admin Dashboard
```
GET /api/dashboard/super-admin
Headers: Authorization: Bearer {token}
Returns: {
  "total_voters": 50000,
  "visited_voters": 30000,
  "voted_voters": 20000,
  "visit_percentage": 60,
  "turnout_percentage": 40,
  "total_surveys": 25000,
  "total_admins": 5,
  "total_karyakartas": 100,
  "booth_performance": [...],
  "favor_score_distribution": [...]
}
```

## 🔍 All Endpoints Available

- Health: GET /api/health
- API Docs: GET /api/docs
- OpenAPI Schema: GET /api/openapi.json

## 🔑 Login Credentials

**Super Admin:**
- Username: `superadmin`
- Password: `admin123`

**Test Admin (if created):**
- Username: `rajesh_admin`
- Password: `SecurePass123!`

**Test Karyakarta (if created):**
- Username: `amit_karyakarta`
- Password: `SecureKary123!`

## 📱 Frontend API Integration

All API calls should:
1. Include `Authorization: Bearer {token}` header
2. Use base URL from environment: `process.env.EXPO_PUBLIC_BACKEND_URL + '/api'`
3. Handle 401 (token expired) by redirecting to login
4. Handle 403 (insufficient permissions) with error message
5. Show loading states during API calls
6. Display user-friendly error messages

## 🚀 Testing with curl

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"admin123"}' | jq -r '.access_token')

# Get voters
curl -X GET "http://localhost:8001/api/voters/?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Create voter
curl -X POST http://localhost:8001/api/voters/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rahul",
    "surname": "Sharma",
    "gender": "male",
    "age": 35,
    "area": "Pune West",
    "booth_number": "101",
    "phone": "+91-9876543210"
  }'

# Get dashboard
curl -X GET http://localhost:8001/api/dashboard/super-admin \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Complete Feature List

✅ **Implemented:**
- User management (3 roles)
- JWT authentication
- Voter CRUD operations
- Advanced voter filtering
- Voter assignment
- Bulk operations
- Visit tracking
- Vote marking
- Survey templates
- Survey submission
- Task management
- Role-based dashboards
- Statistics & analytics

🚀 **Ready to Use:**
- All 40+ API endpoints
- Complete backend infrastructure
- Performance-optimized queries
- Role-based access control
- Comprehensive error handling
