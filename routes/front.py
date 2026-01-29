from flask import render_template, request
from app import app
from model.product import getAllProductList, getProductByCategory
from model.category import getAllCategoryList

# Route for home page - list all products
@app.get('/')
def home():
    category_id = request.args.get('category_id', type=int)

    categories = getAllCategoryList()

    if category_id:  # if user clicked a category
        products = getProductByCategory(category_id)
    else:  # show all products
        products = getAllProductList()

    return render_template(
        'front/index.html',
        categories=categories,
        products=products,
        selected_category=category_id
    )
