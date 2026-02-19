from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Class, Student
from app import db
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

# --- Class Management ---
@admin_bp.route('/classes')
@admin_required
def list_classes():
    classes = Class.query.order_by(Class.order).all()
    return render_template('admin/classes.html', classes=classes)

@admin_bp.route('/classes/add', methods=['POST'])
@admin_required
def add_class():
    name = request.form.get('name')
    order = request.form.get('order')
    
    if name:
        new_class = Class(name=name, order=int(order) if order else 0)
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully')
    return redirect(url_for('admin.list_classes'))

@admin_bp.route('/classes/edit/<int:id>', methods=['POST'])
@admin_required
def edit_class(id):
    c = Class.query.get_or_404(id)
    name = request.form.get('name')
    order = request.form.get('order')
    
    if name:
        c.name = name
        c.order = int(order) if order else 0
        db.session.commit()
        flash('Class updated successfully', 'success')
    return redirect(url_for('admin.list_classes'))

@admin_bp.route('/classes/delete/<int:id>')
@admin_required
def delete_class(id):
    c = Class.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Class deleted')
    return redirect(url_for('admin.list_classes'))
