<p align="center">
  <img src="https://img.icons8.com/fluency/96/api-settings.png" alt="Logo"/>
</p>

<h1 align="center">� PyAdmin</h1>
<p align="center"><strong>Full-Stack REST API with Modern Dashboard</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-2.3.3-green?style=flat-square&logo=flask"/>
  <img src="https://img.shields.io/badge/SQLite-DB-orange?style=flat-square&logo=sqlite"/>
  <img src="https://img.shields.io/badge/JWT-Auth-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square"/>
</p>

---

## ✨ Features

| Backend | Frontend |
|---------|----------|
| 🔐 JWT Authentication | 🌙 Dark Theme Dashboard |
| 🔑 API Key Support | 📱 Responsive Design |
| 👥 Role-Based Access | 📈 Real-time Statistics |
| 📝 CRUD Operations | 📦 Product Management |
| 📄 Pagination & Search | 👤 User Management |
| ⚡ Rate Limiting | 🔑 API Key Manager |
| 🌐 CORS Enabled | 🔔 Toast Notifications |
| ✅ Input Validation | 🔄 Auto-refresh |

---

## 🚀 Quick Start

```bash
# Clone & setup
git clone https://github.com/Rahuljoshi07/PyAdmin.git
cd PyAdmin

# Install dependencies
pip install -r requirements.txt

# Seed sample data (optional)
python seed.py

# Run
python app.py
```

Open **http://localhost:5000** | Login: `admin` / `admin123`

---

## 📖 API Endpoints

### Authentication
| Method | Endpoint | Description |
|:------:|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user |
| POST | `/api/auth/api-keys` | Create API key |

### Products
| Method | Endpoint | Description |
|:------:|----------|-------------|
| GET | `/api/products` | List products (paginated) |
| GET | `/api/products/:id` | Get product |
| POST | `/api/products` | Create product |
| PUT | `/api/products/:id` | Update product |
| DELETE | `/api/products/:id` | Delete product |
| POST | `/api/products/bulk` | Bulk create (admin) |

### Users (Admin Only)
| Method | Endpoint | Description |
|:------:|----------|-------------|
| GET | `/api/users` | List users |
| POST | `/api/users` | Create user |
| PUT | `/api/users/:id` | Update user |
| DELETE | `/api/users/:id` | Delete user |

### Health
| Method | Endpoint | Description |
|:------:|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Statistics |

---

## 🔐 Authentication

```bash
# Get JWT Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use Token
curl http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"

# Or use API Key
curl http://localhost:5000/api/products \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 🔍 Query Parameters

```bash
# Pagination
?page=1&per_page=10

# Search & Filter
?search=laptop&category=Electronics&min_price=100

# Sort
?sort_by=price&sort_order=asc
```

---

## 📁 Project Structure

```
PyAdmin/
├── app.py                  # Flask application
├── config.py               # Configuration
├── seed.py                 # Database seeder
├── requirements.txt        # Dependencies
├── postman_collection.json # Postman collection
├── static/
│   ├── index.html          # Dashboard HTML
│   ├── style.css           # Dark theme CSS
│   └── app.js              # Frontend JS
└── tests/
    ├── test_auth.py        # Auth tests
    ├── test_products.py    # Product tests
    └── test_users.py       # User tests
```

---

## 🧪 Testing

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=app
```

---

## 🛠️ Tech Stack

| Package | Purpose |
|---------|---------|
| Flask 2.3.3 | Web framework |
| Flask-SQLAlchemy | SQL ORM |
| Flask-CORS | Cross-origin support |
| Flask-Limiter | Rate limiting |
| PyJWT | JWT authentication |
| pytest | Testing |

---

## 📋 Response Format

```json
// Success
{ "success": true, "data": {...} }

// Paginated
{ "success": true, "data": [...], "pagination": {...} }

// Error
{ "success": false, "error": "Type", "message": "Details" }
```

---

## ⚙️ Configuration

| Variable | Default |
|----------|---------|
| `SECRET_KEY` | Auto-generated |
| `DATABASE_URL` | `sqlite:///database.db` |

**Rate Limits:** 200/day, 50/hour (default)

---

## 📄 License

MIT License - feel free to use for any project.

---

<p align="center">Made with ❤️ using Python & Flask</p>
