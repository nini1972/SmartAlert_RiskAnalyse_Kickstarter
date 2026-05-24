# Backend Documentation

## Structure

The backend has been refactored into a modular structure for better maintainability and scalability:

```
backend/
├── config/                 # Configuration management
│   └── settings.py         # Application settings using pydantic-settings
├── models/                 # Data models and schemas
│   ├── __init__.py
│   └── kickstarter.py      # Pydantic models for projects, investments, etc.
├── services/               # Business logic services
│   ├── __init__.py
│   ├── ai_analysis.py      # AI-powered project analysis service
│   ├── alerts.py           # Alert generation service
│   └── analytics.py        # Portfolio analytics service
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── projects.py         # Project-related endpoints
│   ├── investments.py      # Investment-related endpoints
│   ├── analytics.py        # Analytics and dashboard endpoints
│   └── alerts.py           # Alert and notification endpoints
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── datenormalizer.py   # Date/time utility functions
├── external_integrations/  # External service integrations
│   ├── __init__.py
│   └── kickstarter.py      # Kickstarter scraping functionality
├── server.py               # Main application entry point
├── requirements.txt        # Python dependencies
└── test_refactor.py        # Test script for verifying the refactor
```

## Key Improvements

1. **Separation of Concerns**: Each module has a single responsibility
2. **Configuration Management**: Centralized settings with environment variable support
3. **Service Layer**: Business logic separated from route handlers
4. **Model Layer**: Clear data models with validation
5. **Routing**: Organized API endpoints by resource
6. **Utilities**: Shared helper functions in a dedicated module
7. **External Integrations**: Isolated third-party service integrations

## Getting Started

1. Copy `.env.example` to `.env` and fill in the required values:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

To verify the refactored structure:
```bash
python test_refactor.py
```