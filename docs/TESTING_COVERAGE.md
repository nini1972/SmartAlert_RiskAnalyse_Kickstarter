# Testing Coverage Improvement Plan

## Current State
- Backend: Limited tests (only scraper tests in `tests/test_kickstarter_scraper.py`)
- Frontend: No tests implemented (Create React App provides testing setup but no tests written)
- Overall test coverage is low

## Goals
1. Increase backend test coverage to >80% for critical modules
2. Implement frontend unit and integration tests
3. Set up automated testing in CI/CD pipeline
4. Add test coverage reporting

## Backend Testing Strategy

### Units to Test
1. **Configuration**: `backend/config/settings.py`
2. **Models**: `backend/models/kickstarter.py`
3. **Services**:
   - `backend/services/ai_analysis.py`
   - `backend/services/alerts.py`
   - `backend/services/analytics.py`
4. **Utilities**: `backend/utils/datenormalizer.py`
5. **Routes**: Test API endpoints with test client
6. **External Integrations**: `backend/external_integrations/kickstarter.py` (already partially tested)

### Test Types
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test interactions between components (e.g., service + model)
- **API Tests**: Test endpoints using FastAPI's TestClient
- **Mocking**: Use unittest.mock to patch external dependencies (OpenAI, MongoDB)

### Test Organization
```
backend/tests/
├── unit/
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_services/
│   │   ├── test_ai_analysis.py
│   │   ├── test_alerts.py
│   │   └── test_analytics.py
│   ├── test_utils/
│   │   └── test_datenormalizer.py
│   └── test_external_integrations/
│       └── test_kickstarter.py
├── integration/
│   ├── test_api_projects.py
│   ├── test_api_investments.py
│   └── test_api_analytics.py
└── conftest.py          # Shared fixtures
```

### Key Improvements
1. **Test Database**: Use test MongoDB instance or mongomock for isolation
2. **Fixtures**: Create reusable fixtures for common test data
3. **Mock External Services**: Mock OpenAI API and network calls
4. **Test Coverage**: Use pytest-cov to measure and enforce coverage thresholds
5. **Continuous Integration**: Integrate tests into GitHub Actions

## Frontend Testing Strategy

### Testing Setup
- Use Jest and React Testing Library (already configured by Create React App)
- Add cypress for end-to-end testing (optional)

### Components to Test
1. **Components**: All components in `frontend/src/components/`
2. **Context**: `frontend/src/context/AppContext.js`
3. **Custom Hooks** (if any)
4. **Utility Functions** (if any)

### Test Types
- **Unit Tests**: Test component rendering, props, state changes
- **Integration Tests**: Test component interactions
- **Snapshot Tests**: For UI regression testing
- **User Interaction Tests**: Simulate clicks, form submissions, etc.

### Test Organization
```
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── features/
│   │   ├── layout/
│   │   └── ui/
│   ├── context/
│   └── utils/
└── ... (existing files)
```

### Key Improvements
1. **Test Rendering**: Ensure components render correctly with various props
2. **Test Interactions**: Test form submissions, button clicks, modal openings
3. **Test Data Fetching**: Mock API calls and test data display
4. **Test Context**: Test state management and actions
5. **Accessibility Tests**: Use jest-axe for basic accessibility checks
6. **Performance Tests**: Monitor render times for critical components

## Implementation Steps

### Phase 1: Backend Tests (Week 1)
1. Set up testing infrastructure (fixtures, test database)
2. Write tests for configuration and models
3. Write tests for utility functions
4. Write tests for each service (AI analysis, alerts, analytics)
5. Write tests for external integrations (enhance existing)
6. Write API endpoint tests using TestClient
7. Configure pytest-cov and set coverage thresholds

### Phase 2: Frontend Tests (Week 2)
1. Review and enhance existing test setup (if needed)
2. Write tests for presentational components
3. Write tests for container components
4. Write tests for context and custom hooks
5. Add end-to-end tests for critical user flows (using Cypress or similar)
6. Configure test coverage reporting

### Phase 3: Automation and Reporting (Week 3)
1. Integrate tests into GitHub Actions workflow
2. Add test coverage badges to README
3. Set up automated test reporting
4. Implement test caching for faster CI runs
5. Add test performance monitoring

## Tools and Dependencies

### Backend
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `pytest-mock`: Mocking utilities
- `mongomock`: Mock MongoDB for testing (or use test database)
- `factory-boy` or `model-bakery`: Test data factories
- `httpx`: For async HTTP client testing (if needed)

### Frontend
- `@testing-library/react`: React Testing Library
- `@testing-library/jest-dom`: Custom jest matchers
- `@testing-library/user-event`: User interaction simulation
- `cypress`: End-to-end testing (optional)
- `jest-axe`: Accessibility testing

## Acceptance Criteria
1. Backend test coverage >80% for critical modules (config, models, services)
2. Frontend test coverage >70% for components and context
3. All tests pass in CI/CD pipeline
4. Test coverage reports generated and visible
5. Critical user flows covered by end-to-end tests
6. No regression in existing functionality

## Files to Create/Modify
```
backend/tests/unit/test_config.py
backend/tests/unit/test_models.py
backend/tests/unit/test_services/test_ai_analysis.py
backend/tests/unit/test_services/test_alerts.py
backend/tests/unit/test_services/test_analytics.py
backend/tests/unit/test_utils/test_datenormalizer.py
backend/tests/unit/test_external_integrations/test_kickstarter.py
backend/tests/conftest.py
backend/tests/integration/test_api_projects.py
backend/tests/integration/test_api_investments.py
backend/tests/integration/test_api_analytics.py

frontend/src/__tests__/components/features/*.test.js
frontend/src/__tests__/components/layout/*.test.js
frontend/src/__tests__/components/ui/*.test.js
frontend/src/__tests__/context/AppContext.test.js
```

## Immediate Next Steps
1. Create the backend test directory structure
2. Write the first test for configuration loading
3. Enhance the existing scraper tests with better coverage
4. Set up pytest configuration with coverage reporting
5. Create a shared conftest.py with fixtures for test database and mock services