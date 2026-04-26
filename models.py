from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# This will be set from app.py
db = None


class User(UserMixin):
    pass


class Category:
    pass


class Product:
    pass


class Order:
    pass


class OrderItem:
    pass


def init_models(database):
    global db, User, Category, Product, Order, OrderItem

    db = database

    class User(UserMixin, db.Model):
        __tablename__ = 'user'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        full_name = db.Column(db.String(100))
        phone = db.Column(db.String(20), nullable=True)  # Made nullable
        avatar = db.Column(db.String(200), nullable=True)
        password_hash = db.Column(db.String(200), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)
        is_active = db.Column(db.Boolean, default=True)
        last_login = db.Column(db.DateTime, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class Category(db.Model):
        __tablename__ = 'category'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)
        slug = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(200), nullable=True)
        icon = db.Column(db.String(50), default='fas fa-heart')
        image = db.Column(db.String(200), nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        products = db.relationship('Product', backref='category', lazy=True)

    class Product(db.Model):
        __tablename__ = 'product'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        slug = db.Column(db.String(100), unique=True, nullable=False)
        description = db.Column(db.Text, nullable=False)
        short_description = db.Column(db.String(200), nullable=True)
        price = db.Column(db.Float, nullable=False)
        compare_price = db.Column(db.Float, nullable=True)
        cost_per_item = db.Column(db.Float, nullable=True)
        stock = db.Column(db.Integer, default=0)
        sku = db.Column(db.String(50), unique=True, nullable=True)
        image = db.Column(db.String(200), nullable=True)
        gallery_images = db.Column(db.Text, nullable=True)
        category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
        is_featured = db.Column(db.Boolean, default=False)
        is_active = db.Column(db.Boolean, default=True)
        weight = db.Column(db.Float, nullable=True)
        dimensions = db.Column(db.String(100), nullable=True)
        tags = db.Column(db.String(200), nullable=True)
        seo_title = db.Column(db.String(100), nullable=True)
        seo_description = db.Column(db.String(200), nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        @property
        def image_url(self):
            if self.image:
                return f'/static/uploads/products/{self.image}'
            return 'https://via.placeholder.com/500x500?text=Pink+Store'

        @property
        def discount_percent(self):
            if self.compare_price and self.compare_price > self.price:
                return int(((self.compare_price - self.price) / self.compare_price) * 100)
            return 0

    class Order(db.Model):
        __tablename__ = 'order'
        id = db.Column(db.Integer, primary_key=True)
        order_number = db.Column(db.String(50), unique=True, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
        customer_name = db.Column(db.String(100), nullable=False)
        customer_email = db.Column(db.String(120), nullable=False)
        customer_phone = db.Column(db.String(20), nullable=False)
        customer_address = db.Column(db.Text, nullable=False)
        shipping_address = db.Column(db.Text, nullable=True)
        total_amount = db.Column(db.Float, nullable=False)
        shipping_cost = db.Column(db.Float, default=0)
        tax_amount = db.Column(db.Float, default=0)
        discount_amount = db.Column(db.Float, default=0)
        grand_total = db.Column(db.Float, nullable=False)
        status = db.Column(db.String(20), default='pending')
        payment_method = db.Column(db.String(50), default='KHQR')
        payment_status = db.Column(db.String(20), default='pending')
        transaction_id = db.Column(db.String(100), nullable=True)
        notes = db.Column(db.Text, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    class OrderItem(db.Model):
        __tablename__ = 'order_item'
        id = db.Column(db.Integer, primary_key=True)
        order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
        product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
        product_name = db.Column(db.String(100), nullable=False)
        product_sku = db.Column(db.String(50), nullable=True)
        quantity = db.Column(db.Integer, nullable=False)
        price = db.Column(db.Float, nullable=False)
        total = db.Column(db.Float, nullable=False)

        @property
        def subtotal(self):
            return self.quantity * self.price

    # Assign to module variables
    globals()['User'] = User
    globals()['Category'] = Category
    globals()['Product'] = Product
    globals()['Order'] = Order
    globals()['OrderItem'] = OrderItem