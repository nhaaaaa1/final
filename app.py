from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import uuid
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'pink-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Create upload folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'categories'), exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'
    login_manager.login_message_category = 'info'

    # Import and initialize models
    import models
    models.init_models(db)

    from models import User, Category, Product, Order, OrderItem

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and seed data
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@pinkstore.com',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin user created!")

        # Create categories if none exist
        if Category.query.count() == 0:
            categories = [
                Category(name='Drinks', slug='drinks', description='Refreshing beverages', icon='fas fa-coffee'),
                Category(name='Snacks', slug='snacks', description='Delicious snacks', icon='fas fa-cookie-bite'),
                Category(name='Desserts', slug='desserts', description='Sweet treats', icon='fas fa-cake-candles'),
                Category(name='Gifts', slug='gifts', description='Perfect presents', icon='fas fa-gift')
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            print("✅ Categories created!")

        # Create sample products if none exist
        if Product.query.count() == 0 and Category.query.count() > 0:
            products = [
                Product(
                    name='Pink Latte',
                    slug='pink-latte',
                    description='Delicious pink latte with strawberry flavor. A perfect treat for any time of the day!',
                    short_description='Sweet strawberry latte',
                    price=5.99,
                    compare_price=7.99,
                    stock=50,
                    sku='PK001',
                    category_id=1,
                    is_featured=True,
                    is_active=True
                ),
                Product(
                    name='Rose Macaron',
                    slug='rose-macaron',
                    description='French macaron with delicate rose flavor. Beautiful and delicious!',
                    short_description='French rose macaron',
                    price=3.99,
                    stock=100,
                    sku='PK002',
                    category_id=3,
                    is_featured=True,
                    is_active=True
                ),
                Product(
                    name='Strawberry Cake',
                    slug='strawberry-cake',
                    description='Fresh strawberry cake with creamy topping. Made with real strawberries!',
                    short_description='Strawberry cream cake',
                    price=15.99,
                    compare_price=19.99,
                    stock=30,
                    sku='PK003',
                    category_id=3,
                    is_featured=True,
                    is_active=True
                ),
                Product(
                    name='Iced Pink Drink',
                    slug='iced-pink-drink',
                    description='Refreshing iced pink beverage with strawberry and rose flavors.',
                    short_description='Iced strawberry rose drink',
                    price=4.99,
                    stock=75,
                    sku='PK004',
                    category_id=1,
                    is_active=True
                ),
                Product(
                    name='Chocolate Heart',
                    slug='chocolate-heart',
                    description='Premium chocolate shaped like a heart. Perfect gift!',
                    short_description='Heart-shaped chocolate',
                    price=8.99,
                    stock=60,
                    sku='PK005',
                    category_id=4,
                    is_featured=True,
                    is_active=True
                )
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()
            print("✅ Sample products created!")

        print("=" * 50)
        print("🚀 Application ready!")
        print("👤 Admin Login: admin / admin123")
        print("🔗 Frontend: http://localhost:5000")
        print("🔗 Admin Panel: http://localhost:5000/admin/login")
        print("=" * 50)

    # Import and register routes after app is created
    from routes import register_routes
    register_routes(app)

    from admin_routes import register_admin_routes
    register_admin_routes(app)

    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)