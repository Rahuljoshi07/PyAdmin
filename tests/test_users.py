"""
Tests for User endpoints
"""
import pytest


class TestUserCreate:
    """Test user creation (admin only)"""
    
    def test_create_user_as_admin(self, client, admin_headers):
        """Test user creation by admin"""
        response = client.post('/api/users',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'role': 'user'
            },
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'newuser'
    
    def test_create_user_as_regular_user(self, client, auth_headers):
        """Test user creation by regular user (should fail)"""
        response = client.post('/api/users',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_create_user_duplicate_username(self, client, admin_headers):
        """Test creating user with existing username"""
        # Create first user
        client.post('/api/users',
            json={
                'username': 'duplicate',
                'email': 'first@example.com',
                'password': 'password123'
            },
            headers=admin_headers
        )
        
        # Try to create second with same username
        response = client.post('/api/users',
            json={
                'username': 'duplicate',
                'email': 'second@example.com',
                'password': 'password123'
            },
            headers=admin_headers
        )
        
        assert response.status_code == 409


class TestUserRead:
    """Test user retrieval"""
    
    def test_get_all_users_as_admin(self, client, admin_headers):
        """Test getting all users as admin"""
        response = client.get('/api/users', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'pagination' in data
    
    def test_get_all_users_as_regular_user(self, client, auth_headers):
        """Test getting all users as regular user (should fail)"""
        response = client.get('/api/users', headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_get_user_by_id_as_admin(self, client, admin_headers, sample_user):
        """Test getting a specific user as admin"""
        user_id = sample_user['id']
        response = client.get(f'/api/users/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == user_id
    
    def test_get_nonexistent_user(self, client, admin_headers):
        """Test getting a non-existent user"""
        response = client.get('/api/users/99999', headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_search_users(self, client, admin_headers, sample_user):
        """Test user search"""
        response = client.get('/api/users?search=sample', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestUserUpdate:
    """Test user updates"""
    
    def test_update_user_as_admin(self, client, admin_headers, sample_user):
        """Test updating user as admin"""
        user_id = sample_user['id']
        response = client.put(f'/api/users/{user_id}',
            json={'email': 'updated@example.com'},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['email'] == 'updated@example.com'
    
    def test_update_user_role(self, client, admin_headers, sample_user):
        """Test updating user role"""
        user_id = sample_user['id']
        response = client.put(f'/api/users/{user_id}',
            json={'role': 'admin'},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['role'] == 'admin'
    
    def test_update_user_as_regular_user(self, client, auth_headers, sample_user):
        """Test updating user as regular user (should fail)"""
        user_id = sample_user['id']
        response = client.put(f'/api/users/{user_id}',
            json={'email': 'hacked@example.com'},
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_update_nonexistent_user(self, client, admin_headers):
        """Test updating a non-existent user"""
        response = client.put('/api/users/99999',
            json={'email': 'test@example.com'},
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestUserDelete:
    """Test user deletion"""
    
    def test_delete_user_as_admin(self, client, admin_headers, sample_user):
        """Test deleting user as admin"""
        user_id = sample_user['id']
        response = client.delete(f'/api/users/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify deletion
        get_response = client.get(f'/api/users/{user_id}', headers=admin_headers)
        assert get_response.status_code == 404
    
    def test_delete_user_as_regular_user(self, client, auth_headers, sample_user):
        """Test deleting user as regular user (should fail)"""
        user_id = sample_user['id']
        response = client.delete(f'/api/users/{user_id}', headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_delete_nonexistent_user(self, client, admin_headers):
        """Test deleting a non-existent user"""
        response = client.delete('/api/users/99999', headers=admin_headers)
        
        assert response.status_code == 404


class TestUserToggleActive:
    """Test user activation/deactivation"""
    
    def test_toggle_user_active_status(self, client, admin_headers, sample_user):
        """Test toggling user active status"""
        user_id = sample_user['id']
        
        # Deactivate
        response = client.put(f'/api/users/{user_id}',
            json={'is_active': False},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['is_active'] is False
        
        # Reactivate
        response = client.put(f'/api/users/{user_id}',
            json={'is_active': True},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['is_active'] is True
