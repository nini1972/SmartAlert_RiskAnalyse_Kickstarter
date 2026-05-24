import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables BEFORE importing
os.environ['MONGO_URL'] = 'mongodb://test:27017'
os.environ['DB_NAME'] = 'test_db'
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

# Import after setting environment
from config.settings import Settings

def test_settings_loads_correctly():
    '''Test that settings loads required fields from environment'''
    settings = Settings()
    
    assert settings.MONGO_URL == 'mongodb://test:27017'
    assert settings.DB_NAME == 'test_db'
    assert settings.OPENAI_API_KEY == 'test-openai-key'
    assert settings.PROJECT_NAME == 'Kickstarter Investment Tracker'
    
    print('[PASS] Settings test passed!')

def test_settings_has_required_attributes():
    '''Test that settings has all required attributes'''
    settings = Settings()
    
    assert hasattr(settings, 'MONGO_URL')
    assert hasattr(settings, 'DB_NAME')
    assert hasattr(settings, 'OPENAI_API_KEY')
    assert hasattr(settings, 'PROJECT_NAME')
    assert hasattr(settings, 'API_V1_STR')
    assert hasattr(settings, 'BACKEND_CORS_ORIGINS')
    assert hasattr(settings, 'LOG_LEVEL')
    
    # Test the cors_origins_list property
    assert isinstance(settings.cors_origins_list, list)
    assert len(settings.cors_origins_list) > 0
    
    print('[PASS] Settings attributes test passed!')

if __name__ == '__main__':
    test_settings_loads_correctly()
    test_settings_has_required_attributes()
    print('[PASS] All settings tests passed!')
