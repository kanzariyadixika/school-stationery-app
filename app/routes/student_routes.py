from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Student, Transaction, Bill, BillItem
from app import db
from datetime import datetime
from app.decorators import student_required

student_panel_bp = Blueprint('student_panel', __name__)

@student_panel_bp.route('/dashboard')
@student_required
def dashboard():
    student = current_user
    recent_transactions = Transaction.query.filter_by(student_id=student.id).order_by(Transaction.date.desc()).limit(5).all()
    
    # Financial summary
    total_purchase = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.student_id == student.id, Transaction.type == 'PURCHASE').scalar() or 0
    total_paid = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.student_id == student.id, Transaction.type == 'PAYMENT').scalar() or 0
    
    return render_template('student/dashboard.html', 
                           student=student, 
                           recent_transactions=recent_transactions,
                           total_purchase=total_purchase,
                           total_paid=total_paid)

@student_panel_bp.route('/account')
@student_required
def account():
    student = current_user
    total_purchase = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.student_id == student.id, Transaction.type == 'PURCHASE').scalar() or 0
    total_paid = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.student_id == student.id, Transaction.type == 'PAYMENT').scalar() or 0
    
    return render_template('student/account.html', 
                           student=student,
                           total_purchase=total_purchase,
                           total_paid=total_paid)

@student_panel_bp.route('/transactions')
@student_required
def transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(student_id=current_user.id).order_by(Transaction.date.desc()).paginate(page=page, per_page=10)
    return render_template('student/transactions.html', transactions=transactions)

@student_panel_bp.route('/bills')
@student_required
def bills():
    page = request.args.get('page', 1, type=int)
    bills = Bill.query.filter_by(student_id=current_user.id).order_by(Bill.date.desc()).paginate(page=page, per_page=10)
    return render_template('student/bills.html', bills=bills)

@student_panel_bp.route('/bill/<int:id>')
@student_required
def view_bill(id):
    bill = Bill.query.get_or_404(id)
    if bill.student_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student_panel.bills'))
    return render_template('student/view_bill.html', bill=bill)

@student_panel_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.parent_phone = request.form.get('parent_phone')
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        if new_password:
            if current_user.check_password(old_password):
                current_user.set_password(new_password)
                flash('Profile and password updated successfully.', 'success')
            else:
                flash('Old password incorrect.', 'danger')
                return redirect(url_for('student_panel.profile'))
        else:
            flash('Profile updated successfully.', 'success')
            
        db.session.commit()
        return redirect(url_for('student_panel.profile'))
        
    return render_template('student/profile.html', student=current_user)

@student_panel_bp.route('/due_status')
@student_required
def due_status():
    return render_template('student/due_status.html', student=current_user)


@student_panel_bp.route('/logout')
@student_required
def logout():
    logout_user()       # Flask-Login logout
    session.clear()     # Clears any session variables
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))  # Use the correct endpoint
