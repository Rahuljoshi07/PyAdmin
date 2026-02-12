"""
Pytest configuration and fixtures for API testing

Note: Run tests individually or in small batches for best results:
    python -m pytest tests/test_auth.py::TestRegistration::test_register_success -v
    python -m pytest tests/ -k "test_register_success or test_health" -v
"""
import pytest
import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='function')
def app():
    """Create application for testing"""
    from app import app as flask_app, db
    
    # Use a unique database for each test
    test_db = f'test_{uuid.uuid4().hex}.db'
    
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db}'
    flask_app.config['RATELIMIT_ENABLED'] = False
    flask_app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
    
    # Cleanup
    try:
        if os.path.exists(test_db):
            os.unlink(test_db)
    except:
        pass


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application"""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope='function')  
def auth_headers(client, app):
    """Create a test user and return authentication headers"""
    response = client.post('/api/auth/register', json={
        'username': f'testuser_{uuid.uuid4().hex[:8]}',
        'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
        'password': 'password123'
    })
    
    data = response.get_json()
    if data and 'data' in data and 'token' in data['data']:
        return {'Authorization': f'Bearer {data["data"]["token"]}'}
    
    return {'Authorization': 'Bearer invalid'}


@pytest.fixture(scope='function')
def admin_headers(client, app):
    """Create an admin user and return authentication headers"""
    from app import db, User
    import uuid
    
    uid = uuid.uuid4().hex[:8]
    
    # Create admin user directly in the existing context
    admin = User(
        username=f'adminuser_{uid}',
        email=f'admin_{uid}@example.com',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', json={
        'username': f'adminuser_{uid}',
        'password': 'admin123'
    })
    
    data = response.get_json()
    if data and 'data' in data and 'token' in data['data']:
        return {'Authorization': f'Bearer {data["data"]["token"]}'}
    return {'Authorization': 'Bearer invalid'}


@pytest.fixture(scope='function')
def sample_product(client, admin_headers):
    """Create a sample product and return its data"""
    import uuid
    response = client.post('/api/products', 
        json={
            'name': f'Test Product {uuid.uuid4().hex[:8]}',
            'description': 'A test product',
            'price': 99.99,
            'quantity': 10,
            'category': 'Electronics'
        },
        headers=admin_headers
    )
    data = response.get_json()
    return data.get('data', {})


@pytest.fixture(scope='function')
def sample_user(client, admin_headers):
    """Create a sample user via admin and return its data"""
    import uuid
    uid = uuid.uuid4().hex[:8]
    response = client.post('/api/users',
        json={
            'username': f'sampleuser_{uid}',
            'email': f'sample_{uid}@example.com',
            'password': 'sample123',
            'role': 'user'
        },
        headers=admin_headers
    )
    data = response.get_json()
    return data.get('data', {})
    return response.get_json()['data']
