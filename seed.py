"""
Database Seeder Script
Populates the database with sample data for testing
"""

from app import app, db, User, Product
import random

# Sample data
USERNAMES = ['john_doe', 'jane_smith', 'bob_wilson', 'alice_brown', 'charlie_davis']
DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'example.com']

PRODUCTS = [
    {'name': 'Laptop Pro 15', 'description': 'High-performance laptop with 16GB RAM', 'price': 1299.99, 'category': 'Electronics', 'quantity': 25},
    {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse with long battery life', 'price': 29.99, 'category': 'Electronics', 'quantity': 100},
    {'name': 'Mechanical Keyboard', 'description': 'RGB mechanical keyboard with blue switches', 'price': 89.99, 'category': 'Electronics', 'quantity': 50},
    {'name': 'USB-C Hub', 'description': '7-in-1 USB-C hub with HDMI and SD card reader', 'price': 49.99, 'category': 'Electronics', 'quantity': 75},
    {'name': 'Webcam HD', 'description': '1080p HD webcam with built-in microphone', 'price': 69.99, 'category': 'Electronics', 'quantity': 40},
    {'name': 'Office Chair', 'description': 'Ergonomic office chair with lumbar support', 'price': 299.99, 'category': 'Furniture', 'quantity': 15},
    {'name': 'Standing Desk', 'description': 'Electric height-adjustable standing desk', 'price': 499.99, 'category': 'Furniture', 'quantity': 10},
    {'name': 'Monitor Stand', 'description': 'Dual monitor stand with cable management', 'price': 79.99, 'category': 'Furniture', 'quantity': 30},
    {'name': 'Desk Lamp LED', 'description': 'Adjustable LED desk lamp with USB charging port', 'price': 39.99, 'category': 'Furniture', 'quantity': 60},
    {'name': 'Python Programming Book', 'description': 'Comprehensive guide to Python programming', 'price': 45.99, 'category': 'Books', 'quantity': 100},
    {'name': 'Flask Web Development', 'description': 'Learn Flask framework from scratch', 'price': 39.99, 'category': 'Books', 'quantity': 80},
    {'name': 'REST API Design', 'description': 'Best practices for designing RESTful APIs', 'price': 34.99, 'category': 'Books', 'quantity': 55},
    {'name': 'Notebook Pack', 'description': 'Pack of 5 spiral notebooks', 'price': 12.99, 'category': 'Office Supplies', 'quantity': 200},
    {'name': 'Pen Set Premium', 'description': 'Set of 10 premium ballpoint pens', 'price': 9.99, 'category': 'Office Supplies', 'quantity': 150},
    {'name': 'Wireless Headphones', 'description': 'Noise-cancelling wireless headphones', 'price': 199.99, 'category': 'Electronics', 'quantity': 35},
]


def seed_users():
    """Seed sample users"""
    print("Seeding users...")
    
    for username in USERNAMES:
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                email=f"{username}@{random.choice(DOMAINS)}",
                role='user'
            )
            user.set_password('password123')
            db.session.add(user)
            print(f"  Created user: {username}")
    
    db.session.commit()
    print(f"Users seeded successfully! Total: {User.query.count()}")


def seed_products():
    """Seed sample products"""
    print("Seeding products...")
    
    for product_data in PRODUCTS:
        if not Product.query.filter_by(name=product_data['name']).first():
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                quantity=product_data['quantity'],
                category=product_data['category'],
                is_available=True
            )
            db.session.add(product)
            print(f"  Created product: {product_data['name']}")
    
    db.session.commit()
    print(f"Products seeded successfully! Total: {Product.query.count()}")


def seed_all():
    """Seed all sample data"""
    with app.app_context():
        print("\n" + "="*50)
        print("Starting database seeding...")
        print("="*50 + "\n")
        
        seed_users()
        print()
        seed_products()
        
        print("\n" + "="*50)
        print("Database seeding completed!")
        print("="*50)
        print(f"\nSummary:")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Products: {Product.query.count()}")
        print(f"  - Categories: {len(set(p.category for p in Product.query.all() if p.category))}")


if __name__ == '__main__':
    seed_all()
