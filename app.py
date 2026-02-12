"""
REST API Backend Application
Flask-based RESTful API with CRUD operations and SQL database integration
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize database
db = SQLAlchemy(app)


# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for the database"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Product(db.Model):
    """Product model for the database"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# ==================== INPUT VALIDATION ====================

def validate_user_data(data, is_update=False):
    """Validate user input data"""
    errors = []
    
    if not is_update:
        if not data.get('username'):
            errors.append('Username is required')
        if not data.get('email'):
            errors.append('Email is required')
    
    if 'username' in data and data['username']:
        if len(data['username']) < 3:
            errors.append('Username must be at least 3 characters')
        if len(data['username']) > 80:
            errors.append('Username must not exceed 80 characters')
    
    if 'email' in data and data['email']:
        if '@' not in data['email'] or '.' not in data['email']:
            errors.append('Invalid email format')
        if len(data['email']) > 120:
            errors.append('Email must not exceed 120 characters')
    
    return errors


def validate_product_data(data, is_update=False):
    """Validate product input data"""
    errors = []
    
    if not is_update:
        if not data.get('name'):
            errors.append('Product name is required')
        if 'price' not in data:
            errors.append('Price is required')
    
    if 'name' in data and data['name']:
        if len(data['name']) > 100:
            errors.append('Product name must not exceed 100 characters')
    
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append('Price must be a positive number')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number')
    
    if 'quantity' in data:
        try:
            quantity = int(data['quantity'])
            if quantity < 0:
                errors.append('Quantity must be a non-negative integer')
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid integer')
    
    return errors


# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'success': False,
        'error': 'Bad Request',
        'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(409)
def conflict(error):
    """Handle 409 Conflict errors"""
    return jsonify({
        'success': False,
        'error': 'Conflict',
        'message': str(error.description) if hasattr(error, 'description') else 'Resource conflict'
    }), 409


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ==================== API ROUTES ====================

@app.route('/')
def index():
    """API Home endpoint"""
    return jsonify({
        'success': True,
        'message': 'Welcome to the REST API',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users',
            'products': '/api/products'
        }
    })


# ==================== USER CRUD OPERATIONS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """GET all users"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'count': len(users),
            'data': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """GET a specific user by ID"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'User with ID {user_id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200


@app.route('/api/users', methods=['POST'])
def create_user():
    """CREATE a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    # Validate input
    errors = validate_user_data(data)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    # Check for duplicate username or email
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': 'Username already exists'
        }), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': 'Email already exists'
        }), 409
    
    # Create new user
    try:
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """UPDATE an existing user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'User with ID {user_id} not found'
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    # Validate input
    errors = validate_user_data(data, is_update=True)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    # Check for duplicate username or email (excluding current user)
    if 'username' in data:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Conflict',
                'message': 'Username already exists'
            }), 409
        user.username = data['username']
    
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Conflict',
                'message': 'Email already exists'
            }), 409
        user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'User with ID {user_id} not found'
        }), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


# ==================== PRODUCT CRUD OPERATIONS ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """GET all products"""
    try:
        products = Product.query.all()
        return jsonify({
            'success': True,
            'count': len(products),
            'data': [product.to_dict() for product in products]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """GET a specific product by ID"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'Product with ID {product_id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': product.to_dict()
    }), 200


@app.route('/api/products', methods=['POST'])
def create_product():
    """CREATE a new product"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    # Validate input
    errors = validate_product_data(data)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    # Create new product
    try:
        new_product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            quantity=int(data.get('quantity', 0))
        )
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': new_product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """UPDATE an existing product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'Product with ID {product_id} not found'
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    # Validate input
    errors = validate_product_data(data, is_update=True)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    # Update product fields
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'quantity' in data:
        product.quantity = int(data['quantity'])
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """DELETE a product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'Product with ID {product_id} not found'
        }), 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
