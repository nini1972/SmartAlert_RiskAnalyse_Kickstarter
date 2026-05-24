import sys
import os

def test_imports():
    try:
        from config.settings import settings
        print('[OK] Config settings imported successfully')
        from models.kickstarter import KickstarterProject, Investment
        print('[OK] Models imported successfully')
        from services.ai_analysis import AIAnalysisService
        from services.alerts import AlertService
        from services.analytics import AnalyticsService
        print('[OK] Services imported successfully')
        from routes import projects, investments, analytics, alerts
        print('[OK] Routes imported successfully')
        from server import app
        print('[OK] Main server imported successfully')
        return True
    except Exception as e:
        print(f'[FAIL] Import failed: {e}')
        return False

def test_settings():
    try:
        from config.settings import settings
        assert hasattr(settings, 'PROJECT_NAME')
        assert hasattr(settings, 'MONGO_URL')
        assert hasattr(settings, 'OPENAI_API_KEY')
        print('[OK] Settings validation passed')
        return True
    except Exception as e:
        print(f'[FAIL] Settings validation failed: {e}')
        return False

def test_models():
    try:
        from models.kickstarter import KickstarterProject, Investment
        from datetime import datetime
        project = KickstarterProject(
            name='Test Project',
            creator='Test Creator',
            url='https://www.kickstarter.com/projects/test/project',
            description='A test project for validation',
            category='Technology',
            goal_amount=10000.0,
            deadline=datetime(2026, 12, 31),
            launched_date=datetime(2026, 1, 1),
            status='live'
        )
        assert project.name == 'Test Project'
        assert project.category == 'Technology'
        print('[OK] KickstarterModel instantiation passed')
        investment = Investment(
            project_id=project.id,
            amount=500.0,
            investment_date=datetime(2026, 6, 1)
        )
        assert investment.amount == 500.0
        assert investment.project_id == project.id
        print('[OK] Investment model instantiation passed')
        return True
    except Exception as e:
        print(f'[FAIL] Model test failed: {e}')
        return False

if __name__ == '__main__':
    print('Testing refactored backend structure...')
    print('=' * 50)
    tests = [test_imports, test_settings, test_models]
    passed = 0
    total = len(tests)
    for test in tests:
        if test():
            passed += 1
        print()
    print('=' * 50)
    print(f'Results: {passed}/{total} tests passed')
    if passed == total:
        print('[PASS] All tests passed! Backend refactoring successful.')
        sys.exit(0)
    else:
        print('[FAIL] Some tests failed. Please check the implementation.')
        sys.exit(1)
