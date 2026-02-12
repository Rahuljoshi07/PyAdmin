"""
Tests for Authentication endpoints
"""
import pytest


class TestRegistration:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['username'] == 'newuser'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'email' in data['message'].lower()
    
    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': '123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_register_duplicate_username(self, client):
        """Test registration with existing username"""
        # First registration
        client.post('/api/auth/register', json={
            'username': 'existinguser',
            'email': 'first@example.com',
            'password': 'password123'
        })
        
        # Second registration with same username
        response = client.post('/api/auth/register', json={
            'username': 'existinguser',
            'email': 'second@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False


class TestLogin:
    """Test user login"""
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Register first
        client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Login with wrong password
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/auth/login', json={
            'username': 'someuser'
        })
        
        assert response.status_code == 400


class TestCurrentUser:
    """Test get current user endpoint"""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user with valid token"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get('/api/auth/me', 
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401


class TestApiKeys:
    """Test API key management"""
    
    def test_create_api_key(self, client, auth_headers):
        """Test creating an API key"""
        response = client.post('/api/auth/api-keys',
            json={'name': 'Test Key'},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'key' in data['data']
    
    def test_list_api_keys(self, client, auth_headers):
        """Test listing API keys"""
        # Create a key first
        client.post('/api/auth/api-keys',
            json={'name': 'Test Key'},
            headers=auth_headers
        )
        
        response = client.get('/api/auth/api-keys', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1
    
    def test_delete_api_key(self, client, auth_headers):
        """Test deleting an API key"""
        # Create a key first
        create_response = client.post('/api/auth/api-keys',
            json={'name': 'Test Key'},
            headers=auth_headers
        )
        key_id = create_response.get_json()['data']['id']
        
        # Delete the key
        response = client.delete(f'/api/auth/api-keys/{key_id}', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
