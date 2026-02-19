from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

from flask import session

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'student':
        return Student.query.get(int(user_id))
    elif user_type == 'admin':
        return User.query.get(int(user_id))
    return None

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False) # e.g., "7", "8", "9-A"
    order = db.Column(db.Integer, default=0) # For sorting and promotion logic (e.g., 7 -> 8)
    
    students = db.relationship('Student', backref='student_class', lazy='dynamic')

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Auth fields
    password_hash = db.Column(db.String(255))
    
    # New relationships
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    
    roll_no = db.Column(db.String(20))
    parent_phone = db.Column(db.String(20))
    
    # Financials
    balance = db.Column(db.Float, default=0.0) # Positive = Wallet, Negative = Due
    
    language = db.Column(db.String(5), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='student', lazy='dynamic')
    bills = db.relationship('Bill', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def total_due(self):
        return abs(self.balance) if self.balance < 0 else 0.0

    @property
    def wallet_amount(self):
        return self.balance if self.balance > 0 else 0.0

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    total_amount = db.Column(db.Float, default=0.0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='paid') # paid, due, partial
    items = db.relationship('BillItem', backref='bill', lazy='dynamic')

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Price at time of purchase
    
    item = db.relationship('Item')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    type = db.Column(db.String(20)) # PURCHASE, PAYMENT, DEPOSIT
    amount = db.Column(db.Float, nullable=False) # Amount of transaction
    balance_after = db.Column(db.Float) # Balance after transaction
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    related_bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=True)

