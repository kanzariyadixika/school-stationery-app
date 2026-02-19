from flask import Blueprint, render_template, redirect, url_for, session, request
from app import db
from flask_login import login_required
from app.models import Student, Bill, Item, Transaction
from sqlalchemy import func
from datetime import datetime, date
from app.decorators import admin_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@admin_required
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code in ['en', 'gu']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.dashboard'))

@main_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = Student.query.count()
    
    # Calculate Total Sales
    total_sales = db.session.query(func.sum(Bill.total_amount)).scalar() or 0.0
    
    # Calculate Today's Sales
    today = date.today()
    bills_today = Bill.query.filter(func.date(Bill.date) == today).all()
    today_sales = sum(b.total_amount for b in bills_today)
        
    # Total Due (Sum of negative balances)
    # Using func.sum on negative balances directly might return negative
    total_due_neg = db.session.query(func.sum(Student.balance))\
        .filter(Student.balance < 0).scalar() or 0.0
    total_due = abs(float(total_due_neg))
    
    # Low Stock Items
    low_stock_items = Item.query.filter(Item.stock_quantity <= Item.low_stock_threshold).all()
    
    return render_template('dashboard.html', 
                          total_students=total_students,
                          total_sales=total_sales,
                          today_sales=today_sales,
                          total_due=total_due,
                          low_stock_items=low_stock_items)
