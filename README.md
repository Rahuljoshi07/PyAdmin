<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/api-settings.png" alt="AdminPanel Logo"/>
</p>

<h1 align="center">🚀 AdminPanel</h1>

<p align="center">
  <strong>A Modern Full-Stack REST API with Dashboard</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/SQLite-Database-orange?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/JWT-Authentication-red?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Version-2.0-brightgreen.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status"/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**AdminPanel** is a production-ready REST API backend built with Python and Flask, featuring a sleek dark-themed dashboard UI. Perfect for learning, prototyping, or as a foundation for your next project.

### Why AdminPanel?

✅ **Complete Solution** - Backend API + Frontend Dashboard  
✅ **Secure** - JWT Auth, API Keys, Rate Limiting  
✅ **Scalable** - Pagination, Search, Filtering, Sorting  
✅ **Well-Tested** - Comprehensive pytest test suite  
✅ **Well-Documented** - Clear API documentation & Postman collection  

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔧 Backend API
- 🔐 **JWT Authentication** with 24-hour tokens
- 🔑 **API Key Support** for service-to-service auth
- 👥 **Role-Based Access** (Admin/User)
- 📝 **Full CRUD** for Users & Products
- 📄 **Pagination** with customizable page size
- 🔍 **Search & Filter** across all fields
- ↕️ **Sorting** (asc/desc) on any field
- ⚡ **Rate Limiting** to prevent abuse
- 🌐 **CORS Enabled** for cross-origin requests
- 📊 **Health Check** endpoint for monitoring
- ✅ **Input Validation** on all endpoints
- 📜 **Request Logging** to file

</td>
<td width="50%">

### 🎨 Frontend Dashboard
- 🌙 **Dark Theme** - Modern, eye-friendly design
- 📱 **Responsive** - Works on all devices
- 📈 **Live Statistics** - Real-time dashboard stats
- 📦 **Product Management** - Full CRUD with filters
- 👤 **User Management** - Admin-only controls
- 🔑 **API Key Manager** - Generate & revoke keys
- 🔔 **Toast Notifications** - Action feedback
- 🔄 **Auto-refresh** - Keep data current

</td>
</tr>
</table>

---

## 📸 Screenshots

<details>
<summary>🖥️ Click to view screenshots</summary>

### Login Page
```
┌─────────────────────────────────────────┐
│              AdminPanel                  │
│           Backend Dashboard              │
│  ┌─────────────┬─────────────┐          │
│  │   Login     │  Register   │          │
│  └─────────────┴─────────────┘          │
│  ┌───────────────────────────┐          │
│  │ Username: admin           │          │
│  └───────────────────────────┘          │
│  ┌───────────────────────────┐          │
│  │ Password: ••••••          │          │
│  └───────────────────────────┘          │
│  ┌───────────────────────────┐          │
│  │         LOGIN →           │          │
│  └───────────────────────────┘          │
└─────────────────────────────────────────┘
```

### Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│ AdminPanel          Dashboard                    admin 👤   │
├──────────┬──────────────────────────────────────────────────┤
│ Dashboard│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│ Products │  │ 6      │ │ 15     │ │ 6      │ │ 15     │    │
│ Users    │  │ Users  │ │Products│ │ Active │ │Available│   │
│ API Keys │  └────────┘ └────────┘ └────────┘ └────────┘    │
│          │                                                  │
│          │  ┌─────────────────────────────────────────────┐│
│          │  │ API Health                                  ││
│          │  │ Status: ✓ healthy  Database: ✓ healthy     ││
│          │  │ Version: 2.0       Last Check: 1:24 am     ││
│          │  └─────────────────────────────────────────────┘│
│  Logout  │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

</details>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/adminpanel.git
cd adminpanel

# 2. Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed sample data (optional)
python seed.py

# 5. Run the application
python app.py
```

### 🎉 That's it!

Open **http://localhost:5000** in your browser.

**Default Login:**
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |

---

## 📖 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints Overview

<details>
<summary>🔐 Authentication</summary>

| Method | Endpoint | Description | Auth |
|:------:|----------|-------------|:----:|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login & get token | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| GET | `/auth/api-keys` | List API keys | ✅ |
| POST | `/auth/api-keys` | Create API key | ✅ |
| DELETE | `/auth/api-keys/:id` | Delete API key | ✅ |

</details>

<details>
<summary>👥 Users (Admin Only)</summary>

| Method | Endpoint | Description | Auth |
|:------:|----------|-------------|:----:|
| GET | `/users` | List all users | 🔒 Admin |
| GET | `/users/:id` | Get user by ID | 🔒 Admin |
| POST | `/users` | Create user | 🔒 Admin |
| PUT | `/users/:id` | Update user | 🔒 Admin |
| DELETE | `/users/:id` | Delete user | 🔒 Admin |

</details>

<details>
<summary>📦 Products</summary>

| Method | Endpoint | Description | Auth |
|:------:|----------|-------------|:----:|
| GET | `/products` | List products | ✅ |
| GET | `/products/:id` | Get product | ✅ |
| GET | `/products/categories` | List categories | ✅ |
| POST | `/products` | Create product | ✅ |
| POST | `/products/bulk` | Bulk create | 🔒 Admin |
| PUT | `/products/:id` | Update product | ✅ |
| DELETE | `/products/:id` | Delete product | ✅ |
| DELETE | `/products/bulk` | Bulk delete | 🔒 Admin |

</details>

<details>
<summary>❤️ Health & Stats</summary>

| Method | Endpoint | Description | Auth |
|:------:|----------|-------------|:----:|
| GET | `/` | API info | ❌ |
| GET | `/health` | Health check | ❌ |
| GET | `/stats` | Statistics | ✅ |

</details>

### Query Parameters

```bash
# Pagination
?page=1&per_page=10

# Search
?search=laptop

# Filter
?category=Electronics&min_price=100&max_price=500

# Sort
?sort_by=price&sort_order=asc

# Combined
?search=laptop&category=Electronics&sort_by=price&page=1&per_page=5
```

### Response Format

```json
// Success
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}

// Paginated
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 50,
    "has_next": true,
    "has_prev": false
  }
}

// Error
{
  "success": false,
  "error": "NotFound",
  "message": "Resource not found"
}
```

---

## 🔐 Authentication

### Option 1: JWT Token

```bash
# 1. Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response: { "data": { "token": "eyJhbG..." } }

# 2. Use token in requests
curl http://localhost:5000/api/users \
  -H "Authorization: Bearer eyJhbG..."
```

### Option 2: API Key

```bash
# 1. Create API key (requires JWT first)
curl -X POST http://localhost:5000/api/auth/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Service Key"}'

# 2. Use API key in requests
curl http://localhost:5000/api/products \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage report
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test
python -m pytest tests/test_auth.py::TestRegistration::test_register_success -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures & configuration
├── test_auth.py         # Authentication tests (15 tests)
├── test_health.py       # Health & utility tests (8 tests)
├── test_products.py     # Product CRUD tests (18 tests)
└── test_users.py        # User management tests (14 tests)
```

### Using Postman

Import `postman_collection.json` into Postman for ready-to-use API requests.

---

## 📁 Project Structure

```
adminpanel/
│
├── 📄 app.py                  # Main Flask application (1200+ lines)
├── ⚙️ config.py               # Configuration settings
├── 🌱 seed.py                 # Database seeder (sample data)
├── 📦 requirements.txt        # Python dependencies
├── 📬 postman_collection.json # Postman testing collection
├── 📖 README.md               # This file
├── 🚫 .gitignore              # Git ignore rules
│
├── 📂 static/                 # Frontend assets
│   ├── 🌐 index.html          # Main dashboard HTML
│   ├── 🎨 style.css           # Dark theme styles
│   └── ⚡ app.js              # Frontend JavaScript
│
├── 📂 tests/                  # Test suite
│   ├── conftest.py            # Test fixtures
│   ├── test_auth.py           # Auth tests
│   ├── test_health.py         # Health tests
│   ├── test_products.py       # Product tests
│   └── test_users.py          # User tests
│
└── 📂 generated/
    ├── 📋 api.log             # Request logs
    └── 🗄️ database.db         # SQLite database
```

---

## 🛠️ Technologies

<table>
<tr>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=python" width="48" height="48" alt="Python" />
<br><sub>Python 3.x</sub>
</td>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=flask" width="48" height="48" alt="Flask" />
<br><sub>Flask</sub>
</td>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=sqlite" width="48" height="48" alt="SQLite" />
<br><sub>SQLite</sub>
</td>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=html" width="48" height="48" alt="HTML5" />
<br><sub>HTML5</sub>
</td>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=css" width="48" height="48" alt="CSS3" />
<br><sub>CSS3</sub>
</td>
<td align="center" width="100">
<img src="https://skillicons.dev/icons?i=js" width="48" height="48" alt="JavaScript" />
<br><sub>JavaScript</sub>
</td>
</tr>
</table>

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | SQL ORM |
| Flask-CORS | 4.0.0 | Cross-origin support |
| Flask-Limiter | 3.5.0 | Rate limiting |
| PyJWT | 2.8.0 | JWT authentication |
| pytest | 7.4.3 | Testing framework |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | Auto-generated |
| `DATABASE_URL` | Database path | `sqlite:///database.db` |
| `DEBUG` | Debug mode | `True` |

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Default | 200/day, 50/hour |
| Registration | 5/hour |
| Login | 10/minute |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/adminpanel.git

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests before committing
python -m pytest tests/ -v
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ using Python & Flask
</p>

<p align="center">
  <a href="#-adminpanel">Back to top ⬆️</a>
</p>
