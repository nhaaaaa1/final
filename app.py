from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile = db.Column(db.String(128))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(128))


# Load admin routes
from routes.admin import *

@app.route('/')
def home():
    # Render dashboard page as home if you want
    return render_template('admin/dashboard/index.html')

if __name__ == "__main__":
    app.run(debug=True)
