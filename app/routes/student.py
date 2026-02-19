from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Student, Transaction, Bill, Class
from datetime import datetime
from app.decorators import admin_required

student_bp = Blueprint('student', __name__, url_prefix='/students')


# ======================================================
# 📌 Student List
# ======================================================
@student_bp.route('/')
@admin_required
def list_students():
    """
    Show all students with class filtering
    """
    class_id = request.args.get('class_id')
    query = Student.query.order_by(Student.name)
    
    if class_id and class_id != 'all':
        query = query.filter_by(class_id=int(class_id))
        
    students = query.all()
    classes = Class.query.order_by(Class.order).all()
    
    return render_template('students/list.html', 
                         students=students, 
                         classes=classes,
                         selected_class=class_id)


# ======================================================
# 📌 Add Student
# ======================================================
@student_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_student():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        roll_no = request.form.get('roll_no')
        parent_phone = request.form.get('parent_phone')
        language = request.form.get('language', 'en')

        # ✅ SAFE class_id handling (NO CRASH EVER)
        class_id_raw = request.form.get('class_id')
        try:
            class_id = int(class_id_raw) if class_id_raw else None
        except ValueError:
            class_id = None

        # validation
        if not name:
            flash('Student name is required', 'danger')
            return redirect(request.url)

        student = Student(
            name=name,
            class_id=class_id,
            roll_no=roll_no,
            parent_phone=parent_phone,
            language=language,
            balance=0
        )
        
        # Set password
        password = request.form.get('password')
        if password:
            student.set_password(password)

        db.session.add(student)
        db.session.commit()

        flash('Student added successfully', 'success')
        return redirect(url_for('student.list_students'))

    classes = Class.query.order_by(Class.order).all()
    return render_template('students/form.html', classes=classes)


# ======================================================
# 📌 View Student Profile
# ======================================================
@student_bp.route('/<int:id>')
@admin_required
def view_student(id):

    student = Student.query.get_or_404(id)

    transactions = Transaction.query \
        .filter_by(student_id=id) \
        .order_by(Transaction.date.desc()) \
        .all()

    bills = Bill.query \
        .filter_by(student_id=id) \
        .order_by(Bill.date.desc()) \
        .all()

    return render_template(
        'students/view.html',
        student=student,
        transactions=transactions,
        bills=bills
    )


# ======================================================
# 📌 Add Payment
# ======================================================
@student_bp.route('/<int:id>/payment', methods=['POST'])
@admin_required
def add_payment(id):

    student = Student.query.get_or_404(id)

    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount', 'danger')
        return redirect(url_for('student.view_student', id=id))

    if amount <= 0:
        flash('Amount must be greater than 0', 'danger')
        return redirect(url_for('student.view_student', id=id))

    description = request.form.get('description', 'Payment Received')

    # Payment increases balance
    new_balance = student.balance + amount

    transaction = Transaction(
        student_id=id,
        type='PAYMENT',
        amount=amount,
        balance_after=new_balance,
        description=description,
        date=datetime.utcnow()
    )

    student.balance = new_balance

    db.session.add(transaction)
    db.session.commit()

    flash('Payment recorded successfully', 'success')
    return redirect(url_for('student.view_student', id=id))


# ======================================================
# 📌 Edit Student
# ======================================================
@student_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == 'POST':

        student.name = request.form.get('name', '').strip()
        student.roll_no = request.form.get('roll_no')
        student.parent_phone = request.form.get('parent_phone')
        student.language = request.form.get('language', 'en')

        # ✅ SAFE class handling again
        class_id_raw = request.form.get('class_id')
        try:
            student.class_id = int(class_id_raw) if class_id_raw else None
        except ValueError:
            student.class_id = None

        # Optional password update
        password = request.form.get('password')
        if password:
            student.set_password(password)

        db.session.commit()

        flash('Student updated successfully', 'success')
        return redirect(url_for('student.list_students'))

    classes = Class.query.order_by(Class.order).all()

    return render_template(
        'students/form.html',
        student=student,
        classes=classes
    )


# ======================================================
# 📌 Delete Student (Optional but useful)
# ======================================================
@student_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    flash('Student deleted successfully', 'success')
    return redirect(url_for('student.list_students'))
