from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# Make sure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print("UPLOAD_FOLDER =", app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Load admin routes
from routes.admin import *
from routes.admin.auth import *

# Secret key for session
app.secret_key = 'super-secret-key'

# Import your models here
from model.product import Product
from model.category import Category

# ---------------- FRONT PAGE ROUTES ----------------

@app.route('/front')
def front_home():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('front/home.html', products=products, categories=categories, category_name=None)

@app.route('/front/category/<int:category_id>')
def front_category(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    category = Category.query.get(category_id)
    category_name = category.name if category else "Unknown"
    return render_template('front/home.html', products=products, categories=categories, category_name=category_name)

# ---------------- ADMIN DASHBOARD ----------------

@app.route('/')
def home():
    # Keep the admin dashboard for '/'
    return render_template('admin/dashboard/index.html')


if __name__ == "__main__":
    app.run(debug=True)
