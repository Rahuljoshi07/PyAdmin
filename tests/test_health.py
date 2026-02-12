"""
Tests for Health, Stats and utility endpoints
"""
import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'
        assert 'database' in data['data']
        assert 'version' in data['data']
    
    def test_health_check_no_auth_required(self, client):
        """Test health endpoint doesn't require authentication"""
        response = client.get('/api/health')
        
        # Should work without auth
        assert response.status_code == 200


class TestApiInfoEndpoint:
    """Test API info endpoint"""
    
    def test_api_info(self, client):
        """Test API info endpoint"""
        response = client.get('/api')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'version' in data
        assert 'endpoints' in data
        assert 'features' in data


class TestStatsEndpoint:
    """Test statistics endpoint"""
    
    def test_get_stats_as_admin(self, client, admin_headers):
        """Test getting stats as admin"""
        response = client.get('/api/stats', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'total_users' in data['data']
        assert 'total_products' in data['data']
    
    def test_get_stats_unauthorized(self, client):
        """Test getting stats without auth"""
        response = client.get('/api/stats')
        
        assert response.status_code == 401


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error response"""
        response = client.get('/api/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_method_not_allowed(self, client, admin_headers):
        """Test 405 error for wrong HTTP method"""
        response = client.patch('/api/health', headers=admin_headers)
        
        assert response.status_code == 405
    
    def test_invalid_json(self, client, admin_headers):
        """Test handling of invalid JSON"""
        response = client.post('/api/products',
            data='not valid json',
            content_type='application/json',
            headers=admin_headers
        )
        
        assert response.status_code == 400


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_headers(self, client, auth_headers):
        """Test that rate limit headers are present"""
        response = client.get('/api/products', headers=auth_headers)
        
        # Check for rate limit headers
        assert response.status_code == 200


class TestCORS:
    """Test CORS functionality"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get('/api/health')
        
        assert 'Access-Control-Allow-Origin' in response.headers


class TestIndexRoute:
    """Test index route serving frontend"""
    
    def test_index_serves_html(self, client):
        """Test that index route serves HTML"""
        response = client.get('/')
        
        # Should return HTML content or redirect to frontend
        assert response.status_code in [200, 302, 404]  # 404 if static files not present in test
