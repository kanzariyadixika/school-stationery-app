import os
from app import create_app, db
from app.models import User

app = create_app('default')

# 🔥 Automatically create tables on startup
with app.app_context():
    db.create_all()

    # Create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created")

@app.shell_context_processor
def make_shell_context():
    from app.models import Student
    return {'db': db, 'User': User, 'Student': Student}


    print("Run file is executing")

if __name__ == "__main__":
    print("App is starting...")
    app.run(debug=True)

