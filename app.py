"""
REST API Backend Application
Flask-based RESTful API with CRUD operations, authentication, and SQL database integration
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from functools import wraps
import os
import logging
import jwt
import hashlib
import secrets

# Initialize Flask app
app = Flask(__name__)

# ==================== CONFIGURATION ====================

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['JWT_EXPIRATION_HOURS'] = 24

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for API routes

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ==================== LOGGING SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== REQUEST LOGGING MIDDLEWARE ====================

@app.before_request
def log_request_info():
    """Log incoming request details"""
    logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")


@app.after_request
def log_response_info(response):
    """Log response details"""
    logger.info(f"Response: {response.status_code}")
    return response


# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for the database"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if password matches"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self, include_email=True):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        return data


class Product(db.Model):
    """Product model for the database"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), index=True)
    is_available = db.Column(db.Boolean, default=True)
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
            'category': self.category,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ApiKey(db.Model):
    """API Key model for authentication"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('api_keys', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key[:8] + '...',  # Only show first 8 chars
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


# ==================== AUTHENTICATION ====================

def generate_token(user_id, role='user'):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Check for API key
        api_key = request.headers.get('X-API-Key')
        
        if not token and not api_key:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Token or API key is required'
            }), 401
        
        try:
            if token:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.get(data['user_id'])
                if not current_user or not current_user.is_active:
                    raise Exception('User not found or inactive')
                g.current_user = current_user
            elif api_key:
                key_record = ApiKey.query.filter_by(key=api_key, is_active=True).first()
                if not key_record:
                    raise Exception('Invalid API key')
                if key_record.expires_at and key_record.expires_at < datetime.utcnow():
                    raise Exception('API key expired')
                g.current_user = key_record.user
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Token has expired'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': str(e)
            }), 401
        
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Admin access required'
            }), 403
        return f(*args, **kwargs)
    return decorated


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
    
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            errors.append('Password must be at least 6 characters')
    
    if 'role' in data and data['role'] not in ['user', 'admin']:
        errors.append('Role must be "user" or "admin"')
    
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
    
    if 'category' in data and data['category']:
        if len(data['category']) > 50:
            errors.append('Category must not exceed 50 characters')
    
    return errors


# ==================== PAGINATION HELPER ====================

def paginate(query, page=1, per_page=10, max_per_page=100):
    """Paginate a SQLAlchemy query"""
    per_page = min(per_page, max_per_page)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': [item.to_dict() for item in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }


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


@app.errorhandler(429)
def ratelimit_handler(error):
    """Handle rate limit exceeded"""
    return jsonify({
        'success': False,
        'error': 'Too Many Requests',
        'message': 'Rate limit exceeded. Please try again later.'
    }), 429


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    db.session.rollback()
    logger.error(f"Internal Server Error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ==================== HEALTH & INFO ROUTES ====================

@app.route('/')
def index():
    """API Home endpoint"""
    return jsonify({
        'success': True,
        'message': 'Welcome to the REST API',
        'version': '2.0',
        'features': [
            'JWT Authentication',
            'API Key Support',
            'Pagination',
            'Search & Filtering',
            'Rate Limiting',
            'CORS Enabled'
        ],
        'endpoints': {
            'auth': '/api/auth',
            'users': '/api/users',
            'products': '/api/products',
            'health': '/api/health'
        }
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'version': '2.0'
    })


@app.route('/api/stats')
@token_required
def get_stats():
    """Get API statistics (authenticated)"""
    return jsonify({
        'success': True,
        'data': {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_products': Product.query.count(),
            'available_products': Product.query.filter_by(is_available=True).count(),
            'total_api_keys': ApiKey.query.filter_by(is_active=True).count()
        }
    })


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    errors = validate_user_data(data)
    if not data.get('password'):
        errors.append('Password is required')
    
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
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
    
    try:
        new_user = User(
            username=data['username'],
            email=data['email'],
            role='user'
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        
        token = generate_token(new_user.id, new_user.role)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': new_user.to_dict(),
                'token': token
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login and get JWT token"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'Username and password required'
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Invalid username or password'
        }), 401
    
    if not user.is_active:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Account is deactivated'
        }), 403
    
    token = generate_token(user.id, user.role)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': user.to_dict(),
            'token': token,
            'expires_in': app.config['JWT_EXPIRATION_HOURS'] * 3600
        }
    })


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user"""
    return jsonify({
        'success': True,
        'data': g.current_user.to_dict()
    })


@app.route('/api/auth/api-keys', methods=['GET'])
@token_required
def list_api_keys():
    """List user's API keys"""
    keys = ApiKey.query.filter_by(user_id=g.current_user.id).all()
    return jsonify({
        'success': True,
        'data': [key.to_dict() for key in keys]
    })


@app.route('/api/auth/api-keys', methods=['POST'])
@token_required
def create_api_key():
    """Create new API key"""
    data = request.get_json() or {}
    
    name = data.get('name', 'API Key')
    expires_days = data.get('expires_days', 30)
    
    key = secrets.token_hex(32)
    api_key = ApiKey(
        key=key,
        name=name,
        user_id=g.current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'API key created. Store it securely - it won\'t be shown again.',
        'data': {
            'key': key,  # Show full key only on creation
            'name': name,
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None
        }
    }), 201


@app.route('/api/auth/api-keys/<int:key_id>', methods=['DELETE'])
@token_required
def delete_api_key(key_id):
    """Delete an API key"""
    api_key = ApiKey.query.filter_by(id=key_id, user_id=g.current_user.id).first()
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'API key not found'
        }), 404
    
    db.session.delete(api_key)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'API key deleted successfully'
    })


# ==================== USER CRUD OPERATIONS ====================

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    """GET all users with pagination, search, and filtering"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Search parameter
        search = request.args.get('search', '')
        
        # Filter parameters
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = User.query
        
        # Apply search
        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == (is_active.lower() == 'true'))
        
        # Apply sorting
        if hasattr(User, sort_by):
            order_column = getattr(User, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        result = paginate(query, page, per_page)
        
        return jsonify({
            'success': True,
            **result
        }), 200
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
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
@admin_required
def create_user():
    """CREATE a new user (admin only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    errors = validate_user_data(data)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
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
    
    try:
        new_user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'user')
        )
        if data.get('password'):
            new_user.set_password(data['password'])
        
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
@token_required
def update_user(user_id):
    """UPDATE an existing user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'User with ID {user_id} not found'
        }), 404
    
    # Only admin or user themselves can update
    if g.current_user.role != 'admin' and g.current_user.id != user_id:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You can only update your own profile'
        }), 403
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    errors = validate_user_data(data, is_update=True)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    # Check for duplicate username or email
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
    
    if 'password' in data:
        user.set_password(data['password'])
    
    # Only admin can change role and is_active status
    if g.current_user.role == 'admin':
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
    
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
@admin_required
def delete_user(user_id):
    """DELETE a user (admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': f'User with ID {user_id} not found'
        }), 404
    
    if user.id == g.current_user.id:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Cannot delete your own account'
        }), 403
    
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
    """GET all products with pagination, search, filtering, and sorting"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Search parameter
        search = request.args.get('search', '')
        
        # Filter parameters
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        is_available = request.args.get('is_available')
        in_stock = request.args.get('in_stock')
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Product.query
        
        # Apply search
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        # Apply filters
        if category:
            query = query.filter(Product.category == category)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if is_available is not None:
            query = query.filter(Product.is_available == (is_available.lower() == 'true'))
        if in_stock is not None:
            if in_stock.lower() == 'true':
                query = query.filter(Product.quantity > 0)
            else:
                query = query.filter(Product.quantity == 0)
        
        # Apply sorting
        if hasattr(Product, sort_by):
            order_column = getattr(Product, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        result = paginate(query, page, per_page)
        
        return jsonify({
            'success': True,
            **result
        }), 200
    except Exception as e:
        logger.error(f"Get products error: {e}")
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': str(e)
        }), 500


@app.route('/api/products/categories', methods=['GET'])
def get_categories():
    """GET all unique product categories"""
    try:
        categories = db.session.query(Product.category).distinct().filter(
            Product.category.isnot(None)
        ).all()
        return jsonify({
            'success': True,
            'data': [cat[0] for cat in categories if cat[0]]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
@token_required
def create_product():
    """CREATE a new product"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'No input data provided'
        }), 400
    
    errors = validate_product_data(data)
    if errors:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'messages': errors
        }), 400
    
    try:
        new_product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            quantity=int(data.get('quantity', 0)),
            category=data.get('category'),
            is_available=data.get('is_available', True)
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
@token_required
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
    if 'category' in data:
        product.category = data['category']
    if 'is_available' in data:
        product.is_available = data['is_available']
    
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
@token_required
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


@app.route('/api/products/bulk', methods=['POST'])
@admin_required
def bulk_create_products():
    """Bulk create products (admin only)"""
    data = request.get_json()
    
    if not data or not isinstance(data, list):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'Expected an array of products'
        }), 400
    
    created = []
    errors = []
    
    for idx, product_data in enumerate(data):
        validation_errors = validate_product_data(product_data)
        if validation_errors:
            errors.append({'index': idx, 'errors': validation_errors})
            continue
        
        try:
            product = Product(
                name=product_data['name'],
                description=product_data.get('description', ''),
                price=float(product_data['price']),
                quantity=int(product_data.get('quantity', 0)),
                category=product_data.get('category'),
                is_available=product_data.get('is_available', True)
            )
            db.session.add(product)
            created.append(product)
        except Exception as e:
            errors.append({'index': idx, 'errors': [str(e)]})
    
    if created:
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{len(created)} products created, {len(errors)} failed',
        'data': {
            'created': [p.to_dict() for p in created],
            'errors': errors
        }
    }), 201 if created else 400


# ==================== MAIN ====================

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")
        
        print("Database tables created successfully!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
