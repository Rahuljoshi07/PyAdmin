"""
Tests for Product endpoints
"""
import pytest


class TestProductCreate:
    """Test product creation"""
    
    def test_create_product_success(self, client, admin_headers):
        """Test successful product creation"""
        response = client.post('/api/products',
            json={
                'name': 'New Product',
                'description': 'A great product',
                'price': 49.99,
                'quantity': 100,
                'category': 'Electronics'
            },
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'New Product'
        assert data['data']['price'] == 49.99
    
    def test_create_product_missing_name(self, client, admin_headers):
        """Test product creation without name"""
        response = client.post('/api/products',
            json={
                'description': 'A product',
                'price': 49.99
            },
            headers=admin_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_product_negative_price(self, client, admin_headers):
        """Test product creation with negative price"""
        response = client.post('/api/products',
            json={
                'name': 'Bad Product',
                'price': -10.00
            },
            headers=admin_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_create_product_unauthorized(self, client):
        """Test product creation without auth"""
        response = client.post('/api/products',
            json={
                'name': 'New Product',
                'price': 49.99
            }
        )
        
        assert response.status_code == 401
    
    def test_create_product_regular_user(self, client, auth_headers):
        """Test product creation by regular user (should work)"""
        response = client.post('/api/products',
            json={
                'name': 'User Product',
                'description': 'Created by user',
                'price': 29.99,
                'quantity': 50
            },
            headers=auth_headers
        )
        
        # Regular users can create products
        assert response.status_code == 201


class TestProductRead:
    """Test product retrieval"""
    
    def test_get_all_products(self, client, admin_headers, sample_product):
        """Test getting all products"""
        response = client.get('/api/products', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'pagination' in data
    
    def test_get_product_by_id(self, client, admin_headers, sample_product):
        """Test getting a specific product"""
        product_id = sample_product['id']
        response = client.get(f'/api/products/{product_id}', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == product_id
    
    def test_get_nonexistent_product(self, client, admin_headers):
        """Test getting a non-existent product"""
        response = client.get('/api/products/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_search_products(self, client, admin_headers, sample_product):
        """Test product search"""
        response = client.get('/api/products?search=Test', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_filter_products_by_category(self, client, admin_headers, sample_product):
        """Test filtering products by category"""
        response = client.get('/api/products?category=Electronics', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_pagination(self, client, admin_headers):
        """Test product pagination"""
        # Create multiple products
        for i in range(15):
            client.post('/api/products',
                json={
                    'name': f'Product {i}',
                    'price': 10.00 + i
                },
                headers=admin_headers
            )
        
        # Get first page
        response = client.get('/api/products?page=1&per_page=5', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 5
        assert data['pagination']['page'] == 1
        assert data['pagination']['total_pages'] == 3
    
    def test_sorting(self, client, admin_headers):
        """Test product sorting"""
        # Create products
        client.post('/api/products', 
            json={'name': 'Apple', 'price': 10}, headers=admin_headers)
        client.post('/api/products', 
            json={'name': 'Banana', 'price': 20}, headers=admin_headers)
        
        # Get sorted by name
        response = client.get('/api/products?sort_by=name&sort_order=asc', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        products = data['data']
        if len(products) >= 2:
            assert products[0]['name'] <= products[1]['name']


class TestProductUpdate:
    """Test product updates"""
    
    def test_update_product_success(self, client, admin_headers, sample_product):
        """Test successful product update"""
        product_id = sample_product['id']
        response = client.put(f'/api/products/{product_id}',
            json={
                'name': 'Updated Product',
                'price': 199.99
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Product'
        assert data['data']['price'] == 199.99
    
    def test_update_nonexistent_product(self, client, admin_headers):
        """Test updating a non-existent product"""
        response = client.put('/api/products/99999',
            json={'name': 'Updated'},
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    def test_update_product_invalid_price(self, client, admin_headers, sample_product):
        """Test updating product with invalid price"""
        product_id = sample_product['id']
        response = client.put(f'/api/products/{product_id}',
            json={'price': -50},
            headers=admin_headers
        )
        
        assert response.status_code == 400


class TestProductDelete:
    """Test product deletion"""
    
    def test_delete_product_success(self, client, admin_headers, sample_product):
        """Test successful product deletion"""
        product_id = sample_product['id']
        response = client.delete(f'/api/products/{product_id}', 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify deletion
        get_response = client.get(f'/api/products/{product_id}', 
            headers=admin_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_product(self, client, admin_headers):
        """Test deleting a non-existent product"""
        response = client.delete('/api/products/99999', headers=admin_headers)
        
        assert response.status_code == 404


class TestBulkOperations:
    """Test bulk product operations"""
    
    def test_bulk_create_products(self, client, admin_headers):
        """Test creating multiple products at once"""
        response = client.post('/api/products/bulk',
            json={
                'products': [
                    {'name': 'Bulk Product 1', 'price': 10.00},
                    {'name': 'Bulk Product 2', 'price': 20.00},
                    {'name': 'Bulk Product 3', 'price': 30.00}
                ]
            },
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['created'] == 3
    
    def test_bulk_delete_products(self, client, admin_headers):
        """Test deleting multiple products at once"""
        # Create products first
        ids = []
        for i in range(3):
            resp = client.post('/api/products',
                json={'name': f'Delete Me {i}', 'price': 10},
                headers=admin_headers
            )
            ids.append(resp.get_json()['data']['id'])
        
        # Bulk delete
        response = client.delete('/api/products/bulk',
            json={'ids': ids},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
