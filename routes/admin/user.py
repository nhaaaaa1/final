from flask import abort, request, render_template, redirect, url_for
from werkzeug.security import generate_password_hash

from app import app, db
from model.user import User, getAllUserList, getUserById


# ==========================
# USER LIST
# ==========================
@app.get('/admin/user')
def user():
    module = 'user'
    rows = getAllUserList()
    return render_template(
        'admin/user/index.html',
        module=module,
        users=rows
    )


# ==========================
# USER FORM (ADD / EDIT)
# ==========================
@app.get('/admin/user/form')
def form_user():
    module = 'user'
    action = request.args.get('action', 'add')

    if action not in ('add', 'edit'):
        abort(404)

    user_id = request.args.get('user_id', type=int)
    status = 'add' if action == 'add' else 'edit'

    user = None
    if status == 'edit':
        if not user_id:
            abort(400)
        user = getUserById(user_id)
        if not user:
            abort(404)

    return render_template(
        'admin/user/form.html',
        module=module,
        status=status,
        user=user
    )


# ==========================
# ADD USER
# ==========================
@app.post('/admin/user/add')
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        abort(400)

    password_hash = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('user'))


# ==========================
# EDIT USER
# ==========================
@app.post('/admin/user/edit')
def edit_user():
    user_id = request.form.get('user_id', type=int)
    user = User.query.get_or_404(user_id)

    user.username = request.form.get('username')
    user.email = request.form.get('email')

    password = request.form.get('password')
    if password:  # update password only if provided
        user.password = generate_password_hash(password)

    db.session.commit()
    return redirect(url_for('user'))


# ==========================
# CONFIRM DELETE
# ==========================
@app.get('/admin/user/confirm')
def confirm_user():
    module = 'user'
    user_id = request.args.get('user_id', type=int)

    user = User.query.get(user_id)
    if not user:
        abort(404)

    return render_template(
        'admin/user/confirm.html',
        module=module,
        user=user
    )


# ==========================
# DELETE USER
# ==========================
@app.post('/admin/user/<int:user_id>/delete')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user'))
