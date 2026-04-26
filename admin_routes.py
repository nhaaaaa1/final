from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Product, Category, Order, OrderItem
from app import db
from werkzeug.utils import secure_filename
import os
import re
import uuid
from datetime import datetime


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def register_admin_routes(app):
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password) and user.is_admin:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Welcome back, {user.full_name}! 💕', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials or not an admin!', 'danger')

        return render_template('admin/login.html')

    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_customers = User.query.filter_by(is_admin=False).count()
        total_categories = Category.query.count()
        total_revenue = db.session.query(db.func.sum(Order.grand_total)).filter_by(payment_status='paid').scalar() or 0
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        low_stock_products = Product.query.filter(Product.stock < 10, Product.stock > 0).limit(5).all()
        out_of_stock = Product.query.filter(Product.stock == 0).count()
        pending_orders = Order.query.filter_by(payment_status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()

        return render_template('admin/dashboard.html',
                               total_products=total_products,
                               total_orders=total_orders,
                               total_customers=total_customers,
                               total_categories=total_categories,
                               total_revenue=total_revenue,
                               recent_orders=recent_orders,
                               low_stock_products=low_stock_products,
                               out_of_stock=out_of_stock,
                               pending_orders=pending_orders,
                               completed_orders=completed_orders)

    # ==================== PRODUCT MANAGEMENT ====================

    @app.route('/admin/products')
    @login_required
    def admin_products():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template('admin/products.html', products=products)

    @app.route('/admin/product/create', methods=['GET', 'POST'])
    @login_required
    def admin_product_create():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        categories = Category.query.all()

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            short_description = request.form.get('short_description')
            price = float(request.form.get('price'))
            compare_price = request.form.get('compare_price')
            stock = int(request.form.get('stock'))
            sku = request.form.get('sku')
            category_id = request.form.get('category_id')
            is_featured = request.form.get('is_featured') == 'on'

            slug = slugify(name)
            existing = Product.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{uuid.uuid4().hex[:4]}"

            image_file = request.files.get('image')
            image_filename = None
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                product_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
                os.makedirs(product_folder, exist_ok=True)
                image_file.save(os.path.join(product_folder, filename))
                image_filename = filename

            product = Product(
                name=name,
                slug=slug,
                description=description,
                short_description=short_description,
                price=price,
                compare_price=float(compare_price) if compare_price else None,
                stock=stock,
                sku=sku,
                category_id=int(category_id) if category_id else None,
                is_featured=is_featured,
                image=image_filename
            )

            db.session.add(product)
            db.session.commit()

            flash(f'Product "{name}" created successfully! 💕', 'success')
            return redirect(url_for('admin_products'))

        return render_template('admin/product_form.html', categories=categories, product=None)

    @app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_product_edit(product_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        product = Product.query.get_or_404(product_id)
        categories = Category.query.all()

        if request.method == 'POST':
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.short_description = request.form.get('short_description')
            product.price = float(request.form.get('price'))
            product.compare_price = float(request.form.get('compare_price')) if request.form.get(
                'compare_price') else None
            product.stock = int(request.form.get('stock'))
            product.sku = request.form.get('sku')
            product.category_id = int(request.form.get('category_id')) if request.form.get('category_id') else None
            product.is_featured = request.form.get('is_featured') == 'on'

            new_slug = slugify(product.name)
            if new_slug != product.slug:
                existing = Product.query.filter_by(slug=new_slug).first()
                if not existing:
                    product.slug = new_slug

            image_file = request.files.get('image')
            if image_file and image_file.filename:
                if product.image:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', product.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(image_file.filename)
                product_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
                os.makedirs(product_folder, exist_ok=True)
                image_file.save(os.path.join(product_folder, filename))
                product.image = filename

            db.session.commit()
            flash(f'Product "{product.name}" updated successfully! 💕', 'success')
            return redirect(url_for('admin_products'))

        return render_template('admin/product_form.html', categories=categories, product=product)

    @app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
    @login_required
    def admin_product_delete(product_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        product = Product.query.get_or_404(product_id)

        if product.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', product.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(product)
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/admin/product/<int:product_id>/toggle-status', methods=['POST'])
    @login_required
    def admin_product_toggle_status(product_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        product = Product.query.get_or_404(product_id)
        product.is_active = not product.is_active
        db.session.commit()

        return jsonify({'success': True})

    # ==================== CATEGORY MANAGEMENT ====================

    @app.route('/admin/categories')
    @login_required
    def admin_categories():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        categories = Category.query.order_by(Category.created_at.desc()).all()
        return render_template('admin/categories.html', categories=categories)

    @app.route('/admin/category/create', methods=['POST'])
    @login_required
    def admin_category_create():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon', 'fas fa-heart')

        slug = slugify(name)
        existing = Category.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"

        category = Category(name=name, slug=slug, description=description, icon=icon)
        db.session.add(category)
        db.session.commit()

        flash(f'Category "{name}" created successfully! 💕', 'success')
        return redirect(url_for('admin_categories'))

    @app.route('/admin/category/<int:category_id>/edit', methods=['POST'])
    @login_required
    def admin_category_edit(category_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        category = Category.query.get_or_404(category_id)
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.icon = request.form.get('icon', 'fas fa-heart')

        db.session.commit()
        flash(f'Category "{category.name}" updated successfully! 💕', 'success')
        return redirect(url_for('admin_categories'))

    @app.route('/admin/category/<int:category_id>/delete', methods=['POST'])
    @login_required
    def admin_category_delete(category_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        category = Category.query.get_or_404(category_id)

        if category.products:
            return jsonify({'success': False, 'error': 'Cannot delete category with products!'})

        db.session.delete(category)
        db.session.commit()

        return jsonify({'success': True})

    # ==================== ORDER MANAGEMENT ====================

    @app.route('/admin/orders')
    @login_required
    def admin_orders():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        status_filter = request.args.get('status', 'all')
        query = Order.query.order_by(Order.created_at.desc())

        if status_filter != 'all':
            query = query.filter_by(status=status_filter)

        orders = query.all()
        return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

    @app.route('/admin/order/<int:order_id>')
    @login_required
    def admin_order_detail(order_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        order = Order.query.get_or_404(order_id)
        return render_template('admin/order_detail.html', order=order)

    @app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
    @login_required
    def admin_order_update_status(order_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        order = Order.query.get_or_404(order_id)
        status = request.form.get('status')
        payment_status = request.form.get('payment_status')

        if status:
            order.status = status
        if payment_status:
            order.payment_status = payment_status

        db.session.commit()
        flash(f'Order #{order.order_number} status updated!', 'success')
        return redirect(url_for('admin_order_detail', order_id=order_id))

    # ==================== USER MANAGEMENT ====================
    # ADD THIS MISSING SECTION

    @app.route('/admin/users')
    @login_required
    def admin_users():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/users.html', users=users)

    @app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
    @login_required
    def admin_user_toggle_status(user_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot deactivate yourself!'})

        user.is_active = not user.is_active
        db.session.commit()

        return jsonify({'success': True})

    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @login_required
    def admin_user_delete(user_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot delete yourself!'})

        db.session.delete(user)
        db.session.commit()

        return jsonify({'success': True})