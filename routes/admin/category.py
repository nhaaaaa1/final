from flask import abort, request, render_template, redirect, url_for
from app import app, db
from model.category import Category, getAllCategoryList, getCategoryById


# ==========================
# CATEGORY LIST
# ==========================
@app.get('/admin/category')
def category():
    module = 'category'
    rows = getAllCategoryList()
    return render_template(
        'admin/category/index.html',
        module=module,
        categories=rows
    )


# ==========================
# CATEGORY FORM (ADD / EDIT)
# ==========================
@app.get('/admin/category/form')
def form_category():
    module = 'category'
    action = request.args.get('action', 'add')
    if action not in ('add', 'edit'):
        abort(404)

    category_id = request.args.get('category_id', type=int)
    status = 'add' if action == 'add' else 'edit'

    category = None
    if status == 'edit':
        if not category_id:
            abort(400)
        category = getCategoryById(category_id)
        if not category:
            abort(404)

    return render_template(
        'admin/category/form.html',
        module=module,
        status=status,
        category=category
    )


# ==========================
# ADD CATEGORY
# ==========================
@app.post('/admin/category/add')
def add_category():
    name = request.form.get('name')
    if not name:
        abort(400)

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('category'))


# ==========================
# EDIT CATEGORY
# ==========================
@app.post('/admin/category/edit')
def edit_category():
    category_id = request.form.get('category_id', type=int)
    category = Category.query.get_or_404(category_id)

    name = request.form.get('name')
    if not name:
        abort(400)
    category.name = name

    db.session.commit()
    return redirect(url_for('category'))


# ==========================
# CONFIRM DELETE
# ==========================
@app.get('/admin/category/confirm')
def confirm_category():
    module = 'category'
    category_id = request.args.get('category_id', type=int)
    category = Category.query.get(category_id)
    if not category:
        return 'No category found'

    return render_template(
        'admin/category/confirm.html',
        module=module,
        category=category
    )


# ==========================
# DELETE CATEGORY
# ==========================
@app.post('/admin/category/<int:category_id>/delete')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('category'))
