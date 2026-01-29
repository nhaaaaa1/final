from app import app, render_template
from routes.admin.utils import login_required

# Dashboard route, requires login
@app.route('/admin')
@login_required
def admin_dashboard():
    module = 'dashboard'
    return render_template('admin/dashboard/index.html', module=module)

# Optional: if you want a separate /admin/dashboard route
@app.get('/admin/dashboard')
@login_required
def dashboard():
    module = 'dashboard'
    return render_template('admin/dashboard/index.html', module=module)
