from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Item
from app import db
from datetime import datetime
from app.decorators import admin_required

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/')
@admin_required
def list_stock():
    items = Item.query.all()
    return render_template('stock/list.html', items=items)

@stock_bp.route('/add', methods=['POST'])
@admin_required
def add_item():
    name = request.form.get('name')
    price = request.form.get('price')
    stock = request.form.get('stock')
    sku = request.form.get('sku')
    
    item = Item(name=name, price=float(price), stock_quantity=int(stock), sku=sku)
    db.session.add(item)
    db.session.commit()
    flash('Item added successfully')
    return redirect(url_for('stock.list_stock'))

@stock_bp.route('/update/<int:id>', methods=['POST'])
@admin_required
def update_item(id):
    item = Item.query.get_or_404(id)
    item.name = request.form.get('name')
    item.price = float(request.form.get('price'))
    item.stock_quantity = int(request.form.get('stock'))
    db.session.commit()
    flash('Item updated successfully')
    return redirect(url_for('stock.list_stock'))

@stock_bp.route('/delete/<int:id>')
@admin_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('stock.list_stock'))
