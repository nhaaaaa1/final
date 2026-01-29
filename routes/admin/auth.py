from flask import render_template, request, redirect, url_for, session
from app import app, db
from werkzeug.security import check_password_hash
from model.user import User
from routes.admin.utils import login_required


# Show login form
@app.route('/login', methods=['GET'])
def login():
    return render_template('admin/login.html')


# Process login
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # store user id in session
        session['user_id'] = user.id
        return redirect(url_for('admin_dashboard'))

    error = "Invalid username or password"
    return render_template('admin/login.html', error=error)


# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
