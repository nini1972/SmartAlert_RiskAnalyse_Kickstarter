# Developer Onboarding Guide

Welcome to the SmartAlert Risk Analysis Kickstarter project! This guide will help you get the development environment set up and familiarize you with the codebase.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v20+)
- **Yarn** (v1.22+)
- **Python** (3.11+)
- **Git**
- **Docker** and **Docker Compose** (optional, for containerized development)
- **MongoDB** (if not using Docker, install locally or use a cloud instance)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/SmartAlert_RiskAnalyse_Kickstarter.git
cd SmartAlert_RiskAnalyse_Kickstarter
```

### 2. Environment Setup

#### Option A: Using Docker Compose (Recommended for Consistency)
```bash
# Copy example environment files
cp .env.example .env
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env

# Edit the .env files to add your actual values (especially OPENAI_API_KEY and MongoDB connection)

# Start all services
docker-compose up --build
```
This will start:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379 (if included in your compose)

#### Option B: Manual Setup (For Direct Development)

##### Backend Setup
```bash
cd backend
# Copy environment file
cp .env.example .env
# Edit .env to add your MongoDB connection and OpenAI API key

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

##### Frontend Setup
```bash
cd frontend
# Copy environment file
cp .env.example .env
# Edit .env to set REACT_APP_BACKEND_URL=http://localhost:8000

# Install dependencies
yarn install

# Start the development server
yarn start
```
This will start the frontend at http://localhost:3000

### 3. Verify the Setup
- Open http://localhost:3000 in your browser to see the frontend
- Visit http://localhost:8000/docs to view the API documentation (Swagger UI)
- Check that the backend is running: http://localhost:8000/ should return a JSON message

## Project Structure

### Backend (`backend/`)
- `config/` - Configuration management (settings.py)
- `models/` - Pydantic data models
- `services/` - Business logic services (AI analysis, alerts, analytics)
- `routes/` - API route handlers
- `utils/` - Utility functions
- `external_integrations/` - Third-party integrations (Kickstarter scraping)
- `server.py` - Main application entry point

### Frontend (`frontend/`)
- `public/` - Static assets
- `src/`
  - `components/` - Reusable UI components (organized by features, layout, ui)
  - `context/` - React Context (AppContext for state management)
  - `App.js` - Main application component
  - `index.js` - Entry point

### Documentation (`docs/`)
- `ARCHITECTURE.md` - System architecture overview
- `API.md` - Detailed API endpoint documentation
- (This file) - Developer onboarding guide

## Development Workflow

### Making Changes
1. Create a new branch for your feature or bug fix
2. Make your changes
3. Write tests for your changes (if applicable)
4. Ensure existing tests still pass
5. Submit a pull request

### Running Tests
#### Backend Tests
```bash
cd backend
# Run the existing scraper tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/unit/test_settings.py

# Run all tests in a directory
python -m pytest tests/unit/
```

#### Frontend Tests
*(Frontend tests are not yet implemented but can be added with Jest/React Testing Library)*
```bash
cd frontend
yarn test
```

### Code Style
- **Backend**: Follows PEP 8 with some exceptions for line length (up to 100 characters)
- **Frontend**: Follows standard JavaScript/React conventions with ESLint and Prettier (via Create React App defaults)

#### Linting and Formatting
```bash
# Backend
cd backend
black .          # Code formatting
isort .          # Import sorting
flake8 .         # Linting
mypy .           # Type checking (if using mypy)

# Frontend
cd frontend
yarn lint        # If ESLint is configured
yarn format      # If Prettier is configured
```

## Common Tasks

### Adding a New API Endpoint
1. Create or update a model in `backend/models/` if needed
2. Add the endpoint to the appropriate file in `backend/routes/`
3. Implement any necessary business logic in `backend/services/`
4. Update the Pydantic models for request/response validation
5. Test the endpoint using the Swagger UI at http://localhost:8000/docs

### Adding a New Frontend Page
1. Create a new component in `frontend/src/components/features/`
2. Add the component to the import and switch statement in `frontend/src/App.js`
3. Add any necessary API calls in `frontend/src/context/AppContext.js`
4. Style the component using TailwindCSS classes
5. Add any necessary modal components to `frontend/src/components/ui/`

### Updating Dependencies
#### Backend
```bash
cd backend
# Update requirements.txt with new versions
pip install --upgrade -r requirements.txt
# Then regenerate requirements.txt if needed
pip freeze > requirements.txt
```

#### Frontend
```bash
cd frontend
yarn upgrade-interactive --latest
# Or update specific packages
yarn upgrade package-name
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'backend'"
- Ensure you are running commands from the project root or have the backend directory in your PYTHONPATH
- When running tests from within the backend directory, make sure to set the Python path correctly

#### Connection Refused Errors
- Verify that MongoDB is running (on port 27017 by default)
- Check your .env file for correct MONGO_URL and DB_NAME
- If using Docker, ensure the MongoDB container is healthy

#### Frontend Not Connecting to Backend
- Check that `REACT_APP_BACKEND_URL` in frontend/.env is set correctly
- Ensure the backend is running and accessible on the specified port
- Check browser console for CORS errors (should be handled by nginx proxy in Docker)

#### Docker Build Failures
- Ensure you have enough disk space and memory
- Check that you have copied all necessary files (especially .env files)
- Verify that the frontend build completes successfully (yarn build)

## Useful Commands

### Docker Commands
```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Stop and remove containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild a specific service
docker-compose build backend
```

### Database Commands (if using local MongoDB)
```bash
# Start MongoDB (if not using Docker)
mongod

# Connect to MongoDB shell
mongo

# Show databases
show dbs

# Use the kickstarter database
use kickstarter_db

# Show collections
show collections
```

## Getting Help

If you encounter issues:
1. Check the documentation in the `docs/` directory
2. Look for existing issues in the GitHub repository
3. Ask questions in the project's communication channels
4. For bugs, create a detailed issue with steps to reproduce

## Contributing

Please read our Contributing Guidelines (to be created) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Happy coding! 🚀