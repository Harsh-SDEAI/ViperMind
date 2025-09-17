# ViperMind API Documentation

This document provides comprehensive information about the ViperMind API endpoints, authentication, and usage patterns.

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication

ViperMind uses JWT (JSON Web Token) based authentication.

### Login Process

1. **Register a new user** (if needed):
   ```http
   POST /auth/register
   Content-Type: application/json

   {
     "email": "user@example.com",
     "username": "username",
     "password": "secure_password"
   }
   ```

2. **Login to get access token**:
   ```http
   POST /auth/login
   Content-Type: application/x-www-form-urlencoded

   username=your_username&password=your_password
   ```

   Response:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "token_type": "bearer",
     "expires_in": 28800
   }
   ```

3. **Use token in subsequent requests**:
   ```http
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```

## API Endpoints

### Authentication & User Management

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "current_level": "beginner",
  "created_at": "2023-12-01T10:00:00Z"
}
```

#### Login
```http
POST /auth/login
```

**Request Body (form-data):**
```
username=your_username
password=your_password
```

#### Get User Profile
```http
GET /auth/profile
Authorization: Bearer {token}
```

#### Update User Profile
```http
PUT /auth/profile
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "current_level": "intermediate"
}
```

### Curriculum Management

#### Get Curriculum Structure
```http
GET /curriculum/structure
```

**Response:**
```json
{
  "levels": [
    {
      "id": "uuid",
      "name": "Beginner",
      "code": "B",
      "description": "Introduction to Python programming",
      "order": 1,
      "sections": [
        {
          "id": "uuid",
          "name": "Python Basics",
          "code": "B1",
          "description": "Fundamental concepts",
          "order": 1,
          "topics": [
            {
              "id": "uuid",
              "name": "Introduction to Python",
              "order": 1
            }
          ]
        }
      ]
    }
  ]
}
```

#### Get Curriculum with Progress
```http
GET /curriculum/progress
Authorization: Bearer {token}
```

**Response:**
```json
{
  "levels": [
    {
      "id": "uuid",
      "name": "Beginner",
      "code": "B",
      "is_unlocked": true,
      "completion_percentage": 75.5,
      "sections": [
        {
          "id": "uuid",
          "name": "Python Basics",
          "code": "B1",
          "is_unlocked": true,
          "completion_percentage": 100.0,
          "topics": [
            {
              "id": "uuid",
              "name": "Introduction to Python",
              "order": 1,
              "is_unlocked": true,
              "is_completed": true,
              "progress_percentage": 85.0
            }
          ]
        }
      ]
    }
  ]
}
```

#### Get Level Details
```http
GET /curriculum/levels/{level_id}
```

#### Get Section Details
```http
GET /curriculum/sections/{section_id}
```

#### Get Topic Details
```http
GET /curriculum/topics/{topic_id}
```

### Lesson Content

#### Get AI-Generated Lesson
```http
GET /lessons/{topic_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "lesson_content": {
    "title": "Introduction to Python",
    "why_it_matters": "Python is essential because...",
    "key_ideas": [
      "Python is interpreted",
      "Indentation matters",
      "Dynamic typing"
    ],
    "examples": [
      {
        "title": "Hello World",
        "code": "print('Hello, World!')",
        "explanation": "This displays text to the console"
      }
    ],
    "pitfalls": [
      "Forgetting proper indentation",
      "Mixing tabs and spaces"
    ],
    "recap": "Python is a powerful, beginner-friendly language..."
  },
  "personalized": true,
  "ai_generated": true
}
```

#### Get Personalized Explanation
```http
POST /lessons/explain
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "concept": "variables",
  "context": "I'm confused about variable assignment"
}
```

**Response:**
```json
{
  "success": true,
  "explanation": {
    "concept": "variables",
    "explanation": "Variables in Python are like labeled boxes...",
    "examples": ["x = 5", "name = 'Alice'"],
    "related_concepts": ["data types", "assignment operators"]
  },
  "personalized": true
}
```

### Assessment System

#### Generate Quiz
```http
POST /assessments/generate-quiz/{topic_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "assessment": {
    "id": "uuid",
    "type": "quiz",
    "target_id": "topic_uuid",
    "questions": [
      {
        "id": "uuid",
        "text": "What is Python?",
        "options": [
          "A programming language",
          "A type of snake",
          "A web browser",
          "An operating system"
        ],
        "difficulty": "easy",
        "code_snippet": null
      }
    ],
    "time_limit": 600,
    "ai_generated": true
  }
}
```

#### Generate Section Test
```http
POST /assessments/generate-test/{section_id}
Authorization: Bearer {token}
```

#### Generate Level Final
```http
POST /assessments/generate-final/{level_id}
Authorization: Bearer {token}
```

#### Submit Assessment
```http
POST /assessments/submit
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "assessment_id": "uuid",
  "answers": {
    "question_uuid_1": 0,
    "question_uuid_2": 2,
    "question_uuid_3": 1
  },
  "time_taken": 450
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "score": 75.0,
    "passed": true,
    "correct_answers": 3,
    "total_questions": 4,
    "time_taken": 450,
    "feedback": "Good job! You passed the quiz.",
    "detailed_results": [
      {
        "question_id": "uuid",
        "correct": true,
        "explanation": "Correct! Python is indeed a programming language."
      }
    ],
    "next_steps": "You can now proceed to the next topic."
  }
}
```

#### Get Assessment History
```http
GET /assessments/history
Authorization: Bearer {token}
```

#### Get Retake Eligibility
```http
GET /assessments/retake-eligibility/{assessment_type}/{target_id}
Authorization: Bearer {token}
```

### Progress Tracking

#### Get User Progress Dashboard
```http
GET /progress/dashboard
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "dashboard": {
    "overall_progress": {
      "total_topics": 30,
      "completed_topics": 12,
      "progress_percentage": 40.0,
      "current_level": "beginner",
      "next_unlock": "Intermediate Level"
    },
    "level_progress": [
      {
        "level_name": "Beginner",
        "completion_percentage": 80.0,
        "topics_completed": 8,
        "topics_total": 10,
        "can_advance": true
      }
    ],
    "recent_activity": [
      {
        "type": "quiz_completed",
        "topic": "Variables",
        "score": 85.0,
        "timestamp": "2023-12-01T10:30:00Z"
      }
    ],
    "recommendations": [
      "Practice more with loops",
      "Review function definitions"
    ],
    "achievements": [
      {
        "title": "First Quiz Completed",
        "description": "Completed your first quiz",
        "earned_at": "2023-12-01T09:15:00Z"
      }
    ]
  }
}
```

#### Get Detailed Progress
```http
GET /progress/detailed
Authorization: Bearer {token}
```

#### Update Progress
```http
POST /progress/update
Authorization: Bearer {token}
```

### Remedial Content

#### Get Remedial Plan
```http
GET /remedial/plan/{assessment_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "remedial_plan": {
    "assessment_id": "uuid",
    "weak_areas": ["loops", "conditionals"],
    "remedial_cards": [
      {
        "topic": "loops",
        "explanation": "Loops allow you to repeat code...",
        "examples": ["for i in range(5): print(i)"],
        "practice_exercises": [
          {
            "question": "Write a loop that prints numbers 1 to 10",
            "solution": "for i in range(1, 11): print(i)"
          }
        ]
      }
    ],
    "estimated_time": 30,
    "completion_required": true
  }
}
```

#### Complete Remedial Activity
```http
POST /remedial/complete
Authorization: Bearer {token}
```

### Personalization

#### Get Learning Preferences
```http
GET /personalization/preferences
Authorization: Bearer {token}
```

#### Update Learning Preferences
```http
PUT /personalization/preferences
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "learning_style": "visual",
  "difficulty_preference": "moderate",
  "interests": ["web_development", "data_science"],
  "pace": "self_paced"
}
```

#### Get Personalized Hints
```http
POST /personalization/hint
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "question_id": "uuid",
  "user_answer": 1,
  "context": "struggling with loops"
}
```

### Monitoring & Health

#### System Status (Public)
```http
GET /monitoring/status
```

**Response:**
```json
{
  "service": "ViperMind API",
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z",
  "version": "1.0.0"
}
```

#### Detailed Health Check
```http
GET /monitoring/health
Authorization: Bearer {token}
```

#### System Metrics
```http
GET /monitoring/metrics
Authorization: Bearer {token}
```

#### Active Alerts
```http
GET /monitoring/alerts
Authorization: Bearer {token}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "type": "validation_error",
    "code": "INVALID_INPUT",
    "message": "Please check your input and try again.",
    "details": "Email format is invalid",
    "request_id": "uuid",
    "timestamp": "2023-12-01T10:00:00Z",
    "recovery_suggestions": [
      "Check your input format",
      "Try again with valid data"
    ],
    "fallback_available": false
  }
}
```

### Error Types

- `validation_error`: Input validation failed
- `authentication_error`: Authentication required
- `authorization_error`: Insufficient permissions
- `not_found_error`: Resource not found
- `rate_limit_error`: Too many requests
- `ai_service_error`: AI service unavailable
- `database_error`: Database operation failed
- `internal_error`: Unexpected server error

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error
- `503`: Service Unavailable

## Rate Limiting

API endpoints are rate limited to ensure fair usage:

- **Default**: 60 requests per minute per user
- **Authentication**: 10 requests per minute per IP
- **AI Generation**: 20 requests per minute per user

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701432000
```

## Pagination

List endpoints support pagination:

```http
GET /assessments/history?page=1&limit=20
```

**Response:**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

```http
GET /progress/detailed?level=beginner&sort=completion_date&order=desc
```

## Webhooks

ViperMind supports webhooks for real-time notifications:

### Webhook Events

- `assessment.completed`: User completes an assessment
- `level.unlocked`: User unlocks a new level
- `achievement.earned`: User earns an achievement
- `remedial.assigned`: Remedial content assigned

### Webhook Payload

```json
{
  "event": "assessment.completed",
  "timestamp": "2023-12-01T10:00:00Z",
  "user_id": "uuid",
  "data": {
    "assessment_id": "uuid",
    "score": 85.0,
    "passed": true
  }
}
```

## SDK and Libraries

### Python SDK

```python
from vipermind_sdk import ViperMindClient

client = ViperMindClient(
    api_url="https://your-domain.com/api/v1",
    api_key="your_api_key"
)

# Get curriculum
curriculum = client.curriculum.get_structure()

# Generate assessment
quiz = client.assessments.generate_quiz(topic_id="uuid")
```

### JavaScript SDK

```javascript
import { ViperMindClient } from 'vipermind-js-sdk';

const client = new ViperMindClient({
  apiUrl: 'https://your-domain.com/api/v1',
  apiKey: 'your_api_key'
});

// Get user progress
const progress = await client.progress.getDashboard();
```

## Testing

### Postman Collection

Import the Postman collection from `docs/api/ViperMind.postman_collection.json` for easy API testing.

### Test Environment

Use the test environment for development:
- Base URL: `http://localhost:8000/api/v1`
- Test user credentials available in development setup

## Support

For API support:
- Documentation: https://docs.vipermind.com/api
- GitHub Issues: https://github.com/your-org/vipermind/issues
- Email: api-support@vipermind.com