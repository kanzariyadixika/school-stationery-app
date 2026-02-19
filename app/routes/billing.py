from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app.models import Student, Item, Bill, BillItem, Transaction, Class
from app import db
from datetime import datetime
import json
from app.decorators import admin_required

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@admin_required
def pos():
    classes = Class.query.order_by(Class.order).all()
    items = Item.query.all() # Pass items to frontend for JS searching
    return render_template('billing/pos.html', classes=classes, items=items)

@billing_bp.route('/api/students/<int:class_id>')
@admin_required
def get_students_by_class(class_id):
    students = Student.query.filter_by(class_id=class_id).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'roll_no': s.roll_no,
        'balance': s.balance
    } for s in students])

@billing_bp.route('/create_bill', methods=['POST'])
@admin_required
def create_bill():
    data = request.get_json()
    student_id = data.get('student_id')
    cart_items = data.get('items') # List of {id, qty, price}
    
    if not student_id or not cart_items:
        return jsonify({'success': False, 'message': 'Invalid data'})
        
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'})
        
    # Calculate Total
    total_amount = 0
    bill = Bill(student_id=student_id, date=datetime.utcnow(), status='paid') # Assume paid via balance deduction? Or just generated?
    # Usually: Bill generated -> Total deducted from Balance.
    
    db.session.add(bill)
    db.session.flush() # get ID
    
    for item_data in cart_items:
        item = Item.query.get(item_data['id'])
        qty = int(item_data['quantity'])
        
        if item.stock_quantity < qty:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Not enough stock for {item.name}'})
            
        # Deduct Stock
        item.stock_quantity -= qty
        
        # Add Bill Item
        bill_item = BillItem(bill_id=bill.id, item_id=item.id, quantity=qty, price=item.price)
        db.session.add(bill_item)
        
        total_amount += (item.price * qty)
        
    bill.total_amount = total_amount
    
    # Update Student Balance (Debit)
    # Purchase reduces balance.
    student.balance -= total_amount
    
    # Create Transaction
    transaction = Transaction(
        student_id=student.id,
        type='PURCHASE',
        amount=total_amount,
        balance_after=student.balance,
        description=f'Bill #{bill.id}',
        related_bill_id=bill.id,
        date=datetime.utcnow()
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({'success': True, 'bill_id': bill.id})
    
@billing_bp.route('/invoice/<int:id>')
@admin_required
def invoice(id):
    bill = Bill.query.get_or_404(id)
    return render_template('billing/invoice.html', bill=bill)
