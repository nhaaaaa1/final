from flask import render_template, request, jsonify, session, redirect, url_for, flash
from models import Product, Category, Order, OrderItem
from app import db
import uuid
from datetime import datetime


def generate_khqr(amount, order_number):
    khqr_data = {
        'amount': str(amount),
        'order_id': order_number,
        'merchant_name': 'Pink Store',
        'merchant_id': 'PK123456789',
        'merchant_city': 'Phnom Penh',
        'currency': 'USD'
    }
    return khqr_data


def register_routes(app):
    @app.route('/')
    def index():
        categories = Category.query.filter_by(is_active=True).all()
        featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
        new_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
        cart_count = sum(item['quantity'] for item in session.get('cart', []))

        return render_template('index.html',
                               categories=categories,
                               featured_products=featured_products,
                               new_products=new_products,
                               cart_count=cart_count)

    @app.route('/shop')
    def shop():
        categories = Category.query.filter_by(is_active=True).all()
        category_id = request.args.get('category', type=int)

        if category_id:
            products = Product.query.filter_by(category_id=category_id, is_active=True).all()
            selected_category = Category.query.get(category_id)
        else:
            products = Product.query.filter_by(is_active=True).all()
            selected_category = None

        cart_count = sum(item['quantity'] for item in session.get('cart', []))

        return render_template('shop.html',
                               categories=categories,
                               products=products,
                               selected_category=selected_category,
                               cart_count=cart_count)

    # Add this missing endpoint - category_products
    @app.route('/category/<string:slug>')
    def category_products(slug):
        category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
        categories = Category.query.filter_by(is_active=True).all()
        products = Product.query.filter_by(category_id=category.id, is_active=True).all()
        cart_count = sum(item['quantity'] for item in session.get('cart', []))

        return render_template('shop.html',
                               categories=categories,
                               products=products,
                               selected_category=category,
                               cart_count=cart_count)

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        related_products = Product.query.filter_by(category_id=product.category_id, is_active=True).limit(4).all()
        categories = Category.query.filter_by(is_active=True).all()
        cart_count = sum(item['quantity'] for item in session.get('cart', []))

        return render_template('product_detail.html',
                               product=product,
                               related_products=related_products,
                               categories=categories,
                               cart_count=cart_count)

    @app.route('/add-to-cart', methods=['POST'])
    def add_to_cart():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        if product.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400

        cart = session.get('cart', [])

        for item in cart:
            if item['id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            cart.append({
                'id': product_id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'image': product.image
            })

        session['cart'] = cart
        session.modified = True

        cart_count = sum(item['quantity'] for item in cart)
        return jsonify({'success': True, 'cart_count': cart_count})

    @app.route('/cart')
    def view_cart():
        cart = session.get('cart', [])
        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        shipping = 0 if subtotal > 50 else 5
        tax = subtotal * 0.1
        grand_total = subtotal + shipping + tax
        cart_count = sum(item['quantity'] for item in cart)
        categories = Category.query.filter_by(is_active=True).all()

        return render_template('cart.html',
                               cart=cart,
                               subtotal=subtotal,
                               shipping=shipping,
                               tax=tax,
                               grand_total=grand_total,
                               cart_count=cart_count,
                               categories=categories)

    @app.route('/update-cart', methods=['POST'])
    def update_cart():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        cart = session.get('cart', [])

        for item in cart:
            if item['id'] == product_id:
                if quantity <= 0:
                    cart.remove(item)
                else:
                    item['quantity'] = quantity
                break

        session['cart'] = cart
        session.modified = True

        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        shipping = 0 if subtotal > 50 else 5
        tax = subtotal * 0.1
        grand_total = subtotal + shipping + tax
        cart_count = sum(item['quantity'] for item in cart)

        return jsonify({
            'success': True,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'grand_total': grand_total,
            'cart_count': cart_count
        })

    @app.route('/remove-from-cart', methods=['POST'])
    def remove_from_cart():
        data = request.get_json()
        product_id = data.get('product_id')

        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != product_id]

        session['cart'] = cart
        session.modified = True

        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        shipping = 0 if subtotal > 50 else 5
        tax = subtotal * 0.1
        grand_total = subtotal + shipping + tax
        cart_count = sum(item['quantity'] for item in cart)

        return jsonify({
            'success': True,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'grand_total': grand_total,
            'cart_count': cart_count
        })

    @app.route('/checkout')
    def checkout():
        cart = session.get('cart', [])
        if not cart:
            flash('Your cart is empty! 💕', 'warning')
            return redirect(url_for('index'))

        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        shipping = 0 if subtotal > 50 else 5
        tax = subtotal * 0.1
        grand_total = subtotal + shipping + tax
        cart_count = sum(item['quantity'] for item in cart)
        categories = Category.query.filter_by(is_active=True).all()

        return render_template('checkout.html',
                               cart=cart,
                               subtotal=subtotal,
                               shipping=shipping,
                               tax=tax,
                               grand_total=grand_total,
                               cart_count=cart_count,
                               categories=categories)

    @app.route('/place-order', methods=['POST'])
    def place_order():
        cart = session.get('cart', [])
        if not cart:
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('index'))

        customer_name = request.form.get('name')
        customer_email = request.form.get('email')
        customer_phone = request.form.get('phone')
        customer_address = request.form.get('address')

        if not all([customer_name, customer_email, customer_phone, customer_address]):
            flash('Please fill in all required fields! 💕', 'danger')
            return redirect(url_for('checkout'))

        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        shipping = 0 if subtotal > 50 else 5
        tax = subtotal * 0.1
        grand_total = subtotal + shipping + tax

        order_number = f"PK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

        order = Order(
            order_number=order_number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_amount=subtotal,
            shipping_cost=shipping,
            tax_amount=tax,
            grand_total=grand_total,
            payment_method='KHQR',
            payment_status='pending',
            status='pending'
        )

        db.session.add(order)
        db.session.flush()

        for item in cart:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['id'],
                product_name=item['name'],
                quantity=item['quantity'],
                price=item['price'],
                total=item['price'] * item['quantity']
            )
            db.session.add(order_item)

            product = Product.query.get(item['id'])
            if product:
                product.stock -= item['quantity']

        db.session.commit()

        khqr_data = generate_khqr(grand_total, order_number)
        session.pop('cart', None)

        return render_template('order_confirmation.html',
                               order=order,
                               khqr_data=khqr_data,
                               grand_total=grand_total)

    @app.route('/confirm-payment/<order_number>', methods=['POST'])
    def confirm_payment(order_number):
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        order.payment_status = 'paid'
        order.status = 'processing'
        order.transaction_id = f'TXN-{uuid.uuid4().hex[:10].upper()}'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Payment confirmed! 💕'})

    @app.route('/order-success/<order_number>')
    def order_success(order_number):
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        categories = Category.query.filter_by(is_active=True).all()
        return render_template('order_success.html', order=order, categories=categories)

    @app.route('/api/cart-count')
    def cart_count_api():
        cart_count = sum(item['quantity'] for item in session.get('cart', []))
        return jsonify({'cart_count': cart_count})