import os
import uuid




from flask import abort, request, render_template, redirect,url_for
from sqlalchemy import text
from werkzeug.utils import secure_filename

from app import app, db
from model.category import getAllCategoryList
from model.product import getProductById, getAllProductList, add_watermark
from model.product import Product



@app.get('/admin/product')
def product():
    module = 'product'
    rows = getAllProductList()
    return render_template(
        'admin/product/index.html',
        module=module,
        products=rows
    )


@app.get('/admin/product/form')
def form_product():
    module = 'product'
    action = request.args.get('action', 'add')

    if action not in ('add', 'edit'):
        abort(404)

    pro_id = request.args.get('pro_id', type=int)
    status = 'add' if action == 'add' else 'edit'

    product = None
    if status == 'edit':
        if not pro_id:
            abort(400)
        product = getProductById(pro_id)
        if not product:
            abort(404)

    return render_template(
        'admin/product/form.html',
        module=module,
        status=status,
        pro_id=pro_id,
        product=product,
        category=getAllCategoryList()
    )

@app.post('/admin/product/add')
def add_product():
    name = request.form.get('name')
    category = request.form.get('category')
    cost = request.form.get('cost', type=float)
    price = request.form.get('price', type=float)
    description = request.form.get('description')
    image_file = request.files.get('image')

    product = Product(
        name=name,
        category_id=category,
        cost=cost,
        price=price,
        description=description
    )
    db.session.add(product)
    db.session.commit()  # get product.id

    if image_file and image_file.filename:
        ext = image_file.filename.rsplit('.', 1)[1].lower()
        image_name = f"product_{product.id}.{ext}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        image_file.save(image_path)         # Save original image
        add_watermark(image_path, "@Panha")  # Add watermark
        product.image = image_name
        db.session.commit()

    return redirect(url_for('product'))

# EDIT PRODUCT
@app.post('/admin/product/edit')
def edit_product():
    product_id = request.form.get('product_id', type=int)
    product = Product.query.get_or_404(product_id)

    product.name = request.form.get('name')
    product.category_id = request.form.get('category')
    product.cost = request.form.get('cost', type=float)
    product.price = request.form.get('price', type=float)
    product.description = request.form.get('description')

    image_file = request.files.get('image')
    if image_file and image_file.filename:
        ext = image_file.filename.rsplit('.', 1)[1].lower()
        image_name = f"product_{product.id}.{ext}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        image_file.save(image_path)
        add_watermark(image_path, "@Panha")
        product.image = image_name

    db.session.commit()
    return redirect(url_for('product'))


@app.get('/admin/product/confirm')
def confirm_product():
    module = 'product'
    pro_id = int(request.args.get('pro_id'))
    product = Product.query.get(pro_id)
    if not product:
        return 'no product found'
    return render_template('admin/product/confirm.html',
            module=module,
            product=product
    )
from flask import request, redirect, url_for

@app.post('/admin/product/<int:pro_id>/delete')
def delete_product(pro_id):
    product = Product.query.get_or_404(pro_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('product'))  # reload list page





