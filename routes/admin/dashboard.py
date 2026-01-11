from app import app, render_template
@app.get('/admin/dashboard')
def dashboard():
    module ='dashboard'
    return render_template('admin/dashboard/index.html', module=module)


def admin():
    return None