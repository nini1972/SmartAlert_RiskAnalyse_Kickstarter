# System Architecture

## Overview

SmartAlert Risk Analysis Kickstarter is a full-stack application designed to help users track and analyze Kickstarter projects for investment purposes. The application consists of three main components:

1. **Frontend**: React.js application providing the user interface
2. **Backend**: FastAPI application providing RESTful API services
3. **Database**: MongoDB for persistent storage
4. **External Services**: 
   - OpenAI API for project analysis
   - Kickstarter (via web scraping) for project data

## Architecture Diagram

```
+-------------------+       +-------------------+       +------------------+
|   Frontend (React)| <---> |   Backend (FastAPI)| <---> |   Database (MongoDB)|
+-------------------+       +-------------------+       +------------------+
         ^                         ^                         ^
         |                         |                         |
+--------+--------+   +------------+------------+   +--------+--------+
|                 |   |                           |   |                 |
|  OpenAI API     |   |  Kickstarter (Scraping)   |   |  Redis (Cache)    |
|                 |   |                           |   |                 |
+-----------------+   +---------------------------+   +-------------------+
```

## Component Details

### Frontend

- **Framework**: React.js with Create React App
- **Styling**: TailwindCSS
- **State Management**: React Context API (AppContext)
- **Key Features**:
  - Dashboard showing portfolio statistics
  - Project browsing and filtering
  - Investment tracking
  - Alerts and notifications
  - Analytics and AI insights
  - Calendar view of project deadlines
- **Communication**: 
  - RESTful API calls to backend using axios
  - WebSocket (if implemented) for real-time updates
- **Build**: 
  - Yarn package manager
  - Production build optimized for static hosting

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Architecture**: Modular, layered architecture
- **Key Components**:
  - **API Layer**: Route handlers organized by resource (projects, investments, analytics, alerts)
  - **Service Layer**: Business logic services (AI analysis, alerts, analytics)
  - **Model Layer**: Pydantic models for data validation and serialization
  - **Configuration Layer**: Centralized settings management using pydantic-settings
  - **Utility Layer**: Helper functions (date normalization, etc.)
  - **External Integrations**: Kickstarter scraping service
- **Key Features**:
  - RESTful API with automatic OpenAPI documentation
  - Asynchronous database operations using Motor (MongoDB async driver)
  - AI-powered project analysis using OpenAI GPT-4
  - Intelligent alert system based on user-defined criteria
  - Portfolio analytics and ROI predictions
  - Rate limiting and input validation
  - Structured logging
- **Dependencies**:
  - FastAPI, Uvicorn for ASGI server
  - Motor for MongoDB async operations
  - Pydantic for data validation
  - OpenAI for AI analysis
  - Aiohttp, BeautifulSoup4 for web scraping
  - Python-dotenv for environment management

### Database

- **Technology**: MongoDB (NoSQL document database)
- **Collections**:
  - `projects`: Stores Kickstarter project data
  - `investments`: Stores user investment records
  - `alert_settings`: Stores user alert preferences
  - `project_alerts`: Stores generated alerts for users
- **Indexes**:
  - Projects: indexed by category, risk_level, status
  - Investments: indexed by project_id, investment_date
- **Connection**: 
  - Async connection using Motor
  - Connection pooling for performance

### External Services

1. **OpenAI API**:
   - Used for qualitative project analysis
   - Generates risk levels, success probabilities, and investment recommendations
   - Cached per project to minimize API calls

2. **Kickstarter Scraping**:
   - Custom scraping service with 3-layer fallback strategy:
     1. Structured data (JSON-LD, embedded state)
     2. Browser automation (Playwright) for client-rendered content
     3. HTML parsing (BeautifulSoup) as fallback
   - Features:
     - Request timeout handling
     - Exponential backoff retry mechanism
     - Detailed logging
     - Disk-based caching to reduce API calls
     - Pydantic validation of scraped data

3. **Redis** (optional/planned):
   - Caching layer for frequent API responses
   - Session storage (if implementing authentication)
   - Rate limiting implementation

## Data Flow

### Project Creation Flow
1. User submits project details via frontend form
2. Frontend sends POST request to `/api/projects/` endpoint
3. Backend validates input using Pydantic models
4. Backend creates KickstarterProject model instance
5. Backend sends project to AI analysis service
6. AI analysis service calls OpenAI API for project insights
7. Backend stores project with AI analysis results in MongoDB
8. Backend returns created project to frontend
9. Frontend updates project list display

### Investment Tracking Flow
1. User records investment in frontend
2. Frontend sends POST request to `/api/investments/` endpoint
3. Backend validates investment and verifies project exists
4. Backend creates Investment model instance
5. Backend stores investment in MongoDB
6. Backend triggers portfolio analytics recalculation (asynchronous)
7. Frontend updates investment list and dashboard statistics

### Alert Generation Flow
1. Periodic task (or on project update) triggers alert evaluation
2. Backend retrieves active projects from MongoDB
3. For each project, backend:
   - Calculates funding velocity
   - Checks against user alert settings
   - Generates alerts for funding surges, high potential projects, and approaching deadlines
4. Alerts are stored in MongoDB and returned to frontend
5. Frontend displays alerts in the Alerts tab
6. High-priority triggers may trigger browser notifications

### Analytics Calculation Flow
1. User requests analytics dashboard or periodically
2. Backend retrieves projects and investments from MongoDB
3. Analytics service calculates:
   - Portfolio ROI prediction
   - Average funding velocity
   - Market sentiment (average success probability)
   - Diversification score
   - Risk-adjusted return
   - Recommended actions based on thresholds
4. Results cached briefly and returned to frontend
5. Frontend displays analytics in Charts and Analytics tabs

## Security Considerations

1. **Input Validation**: All API inputs validated via Pydantic models
2. **CORS**: Configured to restrict origins in production
3. **Environment Secrets**: No secrets in code; all via environment variables
4. **Rate Limiting**: Planned for API endpoints (not yet implemented)
5. **Security Headers**: Implemented via nginx configuration
6. **Dependency Scanning**: Regular updates of dependencies
7. **Error Handling**: Graceful error responses without leaking sensitive data

## Scalability Considerations

1. **Database**: MongoDB sharding for horizontal scaling
2. **Backend**: Stateless FastAPI instances behind load balancer
3. **Caching**: Redis layer planned for API response caching
4. **Frontend**: Static assets served via CDN (nginx or cloud provider)
5. **Async Operations**: Non-blocking I/O for database and external API calls
6. **Worker Processes**: Planned for heavy computations (AI analysis, analytics)

## Deployment Architecture

### Development
- Single container per service (frontend, backend) using docker-compose
- Live code reloading via volume mounts
- Debug tools enabled
- Local MongoDB instance

### Production
- Multi-container orchestration (Docker Compose or Kubernetes)
- Separate frontend and backend services
- External managed database (MongoDB Atlas or similar)
- Redis caching layer
- SSL termination at ingress/nginx
- Monitoring and logging integration
- CI/CD pipeline for automated deployments

## Technology Stack

### Frontend
- React 18
- Tailwind CSS 3
- Axios (HTTP client)
- React Hot Toast (notifications)
- Context API (state management)

### Backend
- FastAPI 0.110+
- Python 3.11
- Motor 3.3+ (MongoDB async driver)
- Pydantic 2.6+ (data validation)
- OpenAI 1.0+ (AI API)
- Aiohttp 3.8+ (async HTTP client)
- BeautifulSoup4 4.12+ (HTML parsing)
- LXML 4.9+ (XML/HTML parsing)
- Python-dotenv 1.0+ (environment variables)

### Infrastructure
- Docker (containerization)
- Nginx (reverse proxy and static file server)
- MongoDB (NoSQL database)
- Redis (planned caching layer)
```

## Future Enhancements

1. **User Authentication**: Implement JWT-based authentication for multi-user support
2. **Real-time Updates**: WebSocket connections for live data updates
3. **Advanced Analytics**: Machine learning models for trend prediction
4. **Mobile Application**: React Native companion app
5. **Extended Integrations**: Additional crowdfunding platforms (Indiegogo, GoFundMe)
6. **Performance Optimization**: GraphQL API for efficient data fetching
7. **Accessibility**: WCAG 2.1 compliance improvements
8. **Internationalization**: Multi-language support