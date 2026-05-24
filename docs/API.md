# API Documentation

## Base URL
```
http://localhost:8000
```

All API endpoints are prefixed with `/api` unless otherwise noted.

## Authentication
*Note: Authentication is planned for future implementation. Currently, all endpoints are accessible without authentication.*

## Response Format
All successful responses return JSON with the following structure:
```json
{
  "status": "success",
  "data": {/* response data */},
  "timestamp": "2026-05-23T18:07:37Z"
}
```

Error responses follow this format:
```json
{
  "status": "error",
  "message": "Error description",
  "details": {/* optional error details */},
  "timestamp": "2026-05-23T18:07:37Z"
}
```

## Pagination
Endpoints that return lists support pagination using:
- `page`: Page number (starts at 1)
- `page_size`: Number of items per page (max 100)

Example: `GET /api/projects?page=2&page_size=50`

## Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthenticated (planned)
- `403`: Forbidden (planned)
- `404`: Not Found
- `422`: Unprocessable Entity (validation error)
- `429`: Too Many Requests (rate limiting - planned)
- `500`: Internal Server Error
- `503`: Service Unavailable

## Endpoints

### Projects

#### Get Projects
```
GET /api/projects
```

Retrieve a paginated list of projects with optional filtering.

**Query Parameters:**
- `category` (string, optional): Filter by project category
- `risk_level` (string, optional): Filter by risk level (low, medium, high)
- `page` (integer, optional, default=1): Page number
- `page_size` (integer, optional, default=50, max=100): Items per page

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "string",
      "name": "string",
      "creator": "string",
      "url": "string",
      "description": "string",
      "category": "string",
      "goal_amount": "number",
      "pledged_amount": "number",
      "backers_count": "integer",
      "deadline": "string (ISO 8601 datetime)",
      "launched_date": "string (ISO 8601 datetime)",
      "status": "string (live|successful|failed|cancelled)",
      "risk_level": "string (low|medium|high)",
      "ai_analysis": {
        "risk_level": "string",
        "sentiment_score": "number (0-1)",
        "success_probability": "number (0-1)",
        "key_factors": ["string"],
        "recommendations": ["string"],
        "funding_velocity": "number",
        "creator_credibility": "number (0-1)"
      },
      "created_at": "string (ISO 8601 datetime)",
      "updated_at": "string (ISO 8601 datetime)"
    }
  ],
  "pagination": {
    "page": "integer",
    "page_size": "integer",
    "total_pages": "integer",
    "total_items": "integer"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Get Project by ID
```
GET /api/projects/{project_id}
```

Retrieve a specific project by its ID.

**Path Parameters:**
- `project_id` (string, required): The project UUID

**Response:** Same project object as in the projects list response

#### Create Project
```
POST /api/projects
```

Create a new Kickstarter project.

**Request Body:**
```json
{
  "name": "string (required, 1-200 chars)",
  "creator": "string (required, 1-100 chars)",
  "url": "string (required, valid Kickstarter URL)",
  "description": "string (required, 10-2000 chars)",
  "category": "string (required, 1-50 chars)",
  "goal_amount": "number (required, > 0)",
  "pledged_amount": "number (optional, default=0, >= 0)",
  "backers_count": "integer (optional, default=0, >= 0)",
  "deadline": "string (required, ISO 8601 datetime)",
  "launched_date": "string (required, ISO 8601 datetime)",
  "status": "string (optional, default='live', pattern=live|successful|failed|cancelled)"
}
```

**Response:** Created project object

#### Update Project
```
PUT /api/projects/{project_id}
```

Update an existing project.

**Path Parameters:**
- `project_id` (string, required): The project UUID

**Request Body:** Same as Create Project (all fields optional except those marked required)

**Response:** Updated project object

#### Delete Project
```
DELETE /api/projects/{project_id}
```

Delete a project and all associated investments.

**Path Parameters:**
- `project_id` (string, required): The project UUID

**Response:**
```json
{
  "status": "success",
  "message": "Project deleted successfully",
  "timestamp": "string (ISO 8601 datetime)"
}
```

### Investments

#### Get Investments
```
GET /api/investments
```

Retrieve investments, optionally filtered by project ID.

**Query Parameters:**
- `project_id` (string, optional): Filter by project ID
- `page` (integer, optional, default=1): Page number
- `page_size` (integer, optional, default=50, max=100): Items per page

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "string",
      "project_id": "string",
      "amount": "number",
      "investment_date": "string (ISO 8601 datetime)",
      "expected_return": "number (optional)",
      "notes": "string (optional)",
      "reward_tier": "string (optional)",
      "created_at": "string (ISO 8601 datetime)"
    }
  ],
  "pagination": {
    "page": "integer",
    "page_size": "integer",
    "total_pages": "integer",
    "total_items": "integer"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Create Investment
```
POST /api/investments
```

Record a new investment.

**Request Body:**
```json
{
  "project_id": "string (required)",
  "amount": "number (required, > 0)",
  "investment_date": "string (required, ISO 8601 datetime)",
  "expected_return": "number (optional)",
  "notes": "string (optional)",
  "reward_tier": "string (optional)"
}
```

**Response:** Created investment object

### Analytics

#### Get Dashboard Statistics
```
GET /api/dashboard/stats
```

Get high-level portfolio statistics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_projects": "integer",
    "total_investments": "integer",
    "total_invested": "number",
    "risk_distribution": [
      {
        "risk_level": "string (low|medium|high)",
        "count": "integer"
      }
    ],
    "category_distribution": [
      {
        "category": "string",
        "count": "integer"
      }
    ],
    "success_rate": "number (percentage)",
    "avg_investment": "number"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Get Advanced Analytics
```
GET /api/api/analytics/advanced
```

Get comprehensive portfolio analytics with ROI predictions.

**Response:**
```json
{
  "status": "success",
  "data": {
    "roi_prediction": "number (percentage)",
    "funding_velocity": "number (percentage per day)",
    "market_sentiment": "number (0-1)",
    "diversification_score": "number (0-1)",
    "risk_adjusted_return": "number (percentage)",
    "recommended_actions": ["string"]
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Get Funding Trends
```
GET /api/analytics/funding-trends
```

Get funding trend data for charts and visualizations.

**Response:**
```json
{
  "status": "success",
  "data": {
    "trends": [
      {
        "name": "string (project name, truncated)",
        "velocity": "number (funding velocity percentage/day)",
        "success_probability": "number (0-100)",
        "pledged_percentage": "number (0-100)",
        "risk_level": "string (low|medium|high)",
        "category": "string"
      }
    ]
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

### Alerts

#### Get Smart Alerts
```
GET /api/alerts
```

Get intelligent alerts for promising projects based on user settings.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "string",
      "project_id": "string",
      "alert_type": "string (high_potential|funding_surge|deadline_approaching)",
      "message": "string",
      "priority": "string (low|medium|high)",
      "is_read": "boolean",
      "created_at": "string (ISO 8601 datetime)"
    }
  ],
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Get Alert Settings
```
GET /api/alerts/settings
```

Get current alert settings for the user.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "string",
    "user_id": "string (default: 'default_user')",
    "notification_frequency": "string (instant|daily|weekly)",
    "min_funding_velocity": "number",
    "preferred_categories": ["string"],
    "max_risk_level": "string (low|medium|high)",
    "min_success_probability": "number (0-1)",
    "browser_notifications": "boolean",
    "email_notifications": "boolean",
    "created_at": "string (ISO 8601 datetime)"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Update Alert Settings
```
POST /api/alerts/settings
```

Update user alert preferences.

**Request Body:** Same as Alert Settings response (all fields optional)

**Response:** Updated alert settings object

### Miscellaneous

#### Get AI Recommendations
```
GET /api/recommendations
```

Get AI-powered investment recommendations for portfolio optimization.

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": ["string"],
    "generated_at": "string (ISO 8601 datetime)"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

#### Root Endpoint
```
GET /
```

Get basic API information.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Kickstarter Investment Tracker API",
    "version": "1.0.0",
    "docs": "/docs"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

## Error Responses

### Validation Error (400/422)
```json
{
  "status": "error",
  "message": "Validation failed",
  "details": {
    "field_name": "Error message"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

### Not Found (404)
```json
{
  "status": "error",
  "message": "Resource not found",
  "details": {
    "resource": "projects",
    "id": "project-id-here"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

### Internal Server Error (500)
```json
{
  "status": "error",
  "message": "Internal server error",
  "details": null,
  "timestamp": "string (ISO 8601 datetime)"
}
```

## Rate Limiting (Planned)
When implemented, rate limiting will return:
```json
{
  "status": "error",
  "message": "Rate limit exceeded",
  "details": {
    "limit": "number",
    "remaining": "number",
    "reset": "timestamp (Unix epoch)"
  },
  "timestamp": "string (ISO 8601 datetime)"
}
```

## OpenAPI/Swagger Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Versioning
API versioning is planned for future implementation. Current API is considered version 1.0.0.

## Changelog
### v1.0.0 (Initial Release)
- Initial API implementation with all core endpoints
- Project and investment CRUD operations
- Analytics and dashboard endpoints
- Alert generation and management
- AI-powered recommendations