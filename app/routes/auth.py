from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Student
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if session.get('user_type') == 'student':
            return redirect(url_for('student_panel.dashboard'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username') # Admin: username, Student: roll_no
        password = request.form.get('password')
        
        # 1. Check Admin Table
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_type'] = 'admin'
            login_user(user)
            return redirect(url_for('main.dashboard'))
            
        # 2. Check Student Table
        student = Student.query.filter_by(roll_no=username).first()
        if student and student.check_password(password):
            session['user_type'] = 'student'
            login_user(student)
            return redirect(url_for('student_panel.dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
