# REST API Backend Application

A RESTful API built with Python and Flask, featuring CRUD operations, SQL database integration, input validation, and error handling.

## Features

- **RESTful API Design** - Clean API endpoints following REST conventions
- **CRUD Operations** - Create, Read, Update, Delete for Users and Products
- **SQL Database** - SQLite database with SQLAlchemy ORM
- **Input Validation** - Server-side validation for all inputs
- **Error Handling** - Consistent error responses with proper HTTP status codes
- **JSON Responses** - All endpoints return JSON formatted data

## Project Structure

```
rest-api-backend/
├── app.py              # Main Flask application with routes
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore file
└── database.db         # SQLite database (created on first run)
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

## API Endpoints

### Base URL
```
http://localhost:5000
```

### Users API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/<id>` | Get user by ID |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/<id>` | Update user |
| DELETE | `/api/users/<id>` | Delete user |

### Products API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | Get all products |
| GET | `/api/products/<id>` | Get product by ID |
| POST | `/api/products` | Create new product |
| PUT | `/api/products/<id>` | Update product |
| DELETE | `/api/products/<id>` | Delete product |

## Testing with Postman

### Create User
- **Method:** POST
- **URL:** `http://localhost:5000/api/users`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "username": "john_doe",
    "email": "john@example.com"
}
```

### Get All Users
- **Method:** GET
- **URL:** `http://localhost:5000/api/users`

### Get User by ID
- **Method:** GET
- **URL:** `http://localhost:5000/api/users/1`

### Update User
- **Method:** PUT
- **URL:** `http://localhost:5000/api/users/1`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "username": "john_updated",
    "email": "john.updated@example.com"
}
```

### Delete User
- **Method:** DELETE
- **URL:** `http://localhost:5000/api/users/1`

### Create Product
- **Method:** POST
- **URL:** `http://localhost:5000/api/products`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "quantity": 10
}
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
| 404 | Not Found |
| 409 | Conflict (duplicate data) |
| 500 | Internal Server Error |

## Technologies Used

- **Python 3.x** - Programming language
- **Flask** - Web framework
- **Flask-SQLAlchemy** - SQL ORM
- **SQLite** - Database
- **Git** - Version control

## Version Control (Git)

```bash
# Initialize repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: REST API backend with Flask"

# Add remote (optional)
git remote add origin <repository-url>

# Push to remote
git push -u origin main
```

## License

This project is open source and available under the MIT License.
