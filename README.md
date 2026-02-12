# REST API Backend Application v2.0

A full-featured RESTful API built with Python and Flask, including JWT authentication, API keys, pagination, search, filtering, rate limiting, and more.

## Features

- **JWT Authentication** - Secure token-based authentication
- **API Key Support** - Alternative authentication via API keys
- **User Roles** - Admin and user role-based access control
- **CRUD Operations** - Full Create, Read, Update, Delete for Users and Products
- **Pagination** - Paginated responses for list endpoints
- **Search & Filtering** - Search by text, filter by fields
- **Sorting** - Sort results by any field
- **Rate Limiting** - Protect API from abuse
- **CORS Enabled** - Cross-origin resource sharing
- **Request Logging** - All requests logged to file
- **Health Check** - Endpoint for monitoring
- **Input Validation** - Server-side validation for all inputs
- **Error Handling** - Consistent error responses with proper HTTP status codes

## Project Structure

```
rest-api-backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── seed.py                 # Database seeder script
├── requirements.txt        # Python dependencies
├── postman_collection.json # Postman collection for testing
├── README.md               # Documentation
├── .gitignore              # Git ignore file
├── api.log                 # Request logs (generated)
└── database.db             # SQLite database (generated)
```

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd rest-api-backend
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
python app.py
```

The server will start at `http://localhost:5000`

### 6. (Optional) Seed sample data
```bash
python seed.py
```

## Default Admin Credentials
- **Username:** admin
- **Password:** admin123

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user (auth required) |
| GET | `/api/auth/api-keys` | List API keys (auth required) |
| POST | `/api/auth/api-keys` | Create API key (auth required) |
| DELETE | `/api/auth/api-keys/<id>` | Delete API key (auth required) |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users (paginated, auth required) |
| GET | `/api/users/<id>` | Get user by ID (auth required) |
| POST | `/api/users` | Create new user (admin only) |
| PUT | `/api/users/<id>` | Update user (auth required) |
| DELETE | `/api/users/<id>` | Delete user (admin only) |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | Get all products (paginated, public) |
| GET | `/api/products/<id>` | Get product by ID (public) |
| GET | `/api/products/categories` | Get all categories (public) |
| POST | `/api/products` | Create new product (auth required) |
| POST | `/api/products/bulk` | Bulk create products (admin only) |
| PUT | `/api/products/<id>` | Update product (auth required) |
| DELETE | `/api/products/<id>` | Delete product (auth required) |

### Health & Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/health` | Health check |
| GET | `/api/stats` | API statistics (auth required) |

## Authentication

### Using JWT Token
```bash
# Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token in requests
curl http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using API Key
```bash
# Create API key (after login)
curl -X POST http://localhost:5000/api/auth/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My API Key"}'

# Use API key in requests
curl http://localhost:5000/api/users \
  -H "X-API-Key: YOUR_API_KEY"
```

## Pagination, Search & Filtering

### Pagination
```
GET /api/products?page=1&per_page=10
```

### Search
```
GET /api/products?search=laptop
GET /api/users?search=john
```

### Filtering
```
GET /api/products?category=Electronics
GET /api/products?min_price=50&max_price=200
GET /api/products?is_available=true&in_stock=true
GET /api/users?role=admin&is_active=true
```

### Sorting
```
GET /api/products?sort_by=price&sort_order=asc
GET /api/products?sort_by=created_at&sort_order=desc
```

### Combined Example
```
GET /api/products?search=laptop&category=Electronics&min_price=500&sort_by=price&sort_order=asc&page=1&per_page=5
```

## API Examples with Postman

### Register User
- **Method:** POST
- **URL:** `http://localhost:5000/api/auth/register`
- **Body:**
```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
}
```

### Login
- **Method:** POST
- **URL:** `http://localhost:5000/api/auth/login`
- **Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

### Create Product (Auth Required)
- **Method:** POST
- **URL:** `http://localhost:5000/api/products`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
    "name": "Gaming Laptop",
    "description": "High-performance gaming laptop",
    "price": 1499.99,
    "quantity": 10,
    "category": "Electronics"
}
```

### Bulk Create Products (Admin Only)
- **Method:** POST
- **URL:** `http://localhost:5000/api/products/bulk`
- **Headers:** `Authorization: Bearer <admin_token>`
- **Body:**
```json
[
    {"name": "Product 1", "price": 99.99, "category": "Category A"},
    {"name": "Product 2", "price": 149.99, "category": "Category B"}
]
```

## Response Format

### Success Response
```json
{
    "success": true,
    "message": "Operation successful",
    "data": { ... }
}
```

### Paginated Response
```json
{
    "success": true,
    "items": [...],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total_pages": 5,
        "total_items": 50,
        "has_next": true,
        "has_prev": false
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error Type",
    "message": "Error description"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate data) |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

## Rate Limits

- **Default:** 200 requests/day, 50 requests/hour
- **Registration:** 5 requests/hour
- **Login:** 10 requests/minute

## Technologies Used

- **Python 3.x** - Programming language
- **Flask** - Web framework
- **Flask-SQLAlchemy** - SQL ORM
- **Flask-CORS** - Cross-origin support
- **Flask-Limiter** - Rate limiting
- **PyJWT** - JWT authentication
- **SQLite** - Database
- **Git** - Version control

## Version Control (Git)

```bash
# Initialize repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Add features: JWT auth, pagination, filtering, rate limiting"

# Push to remote
git push origin main
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | JWT secret key | Random generated |
| DATABASE_URL | Database connection URL | SQLite local |

## License

This project is open source and available under the MIT License.
