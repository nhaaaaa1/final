from flask import request, render_template
from app import app

@app.get('/admin/product')
def product():
    module = 'product'
    return render_template('admin/product/index.html', module=module)

@app.get('/admin/product/form')
def add_product():
    module = 'product'
    action = request.args.get('action', 'add')
    pro_id = request.args.get('pro_id', '0')
    status = 'add' if action == 'add' else 'edit'

    return render_template(
        'admin/product/form.html',
        module=module,
        status=status,
        pro_id=pro_id,
    )
