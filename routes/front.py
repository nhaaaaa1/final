from flask import render_template, request, session, jsonify, url_for
from app import app
from model.product import getAllProductList, getProductByCategory
from model.category import getAllCategoryList
import json
from datetime import datetime


# Route for front home page
@app.route('/front')
def front_home():  # Make sure this function name matches what's in base.html
    category_id = request.args.get('category_id', type=int)

    categories = getAllCategoryList()

    if category_id:  # if user clicked a category
        products = getProductByCategory(category_id)
        # Get category name for display
        selected_category_name = next((cat.name for cat in categories if cat.id == category_id), None)
    else:  # show all products
        products = getAllProductList()
        selected_category_name = None

    return render_template(
        'front/home.html',
        categories=categories,
        products=products,
        selected_category=category_id,
        selected_category_name=selected_category_name
    )