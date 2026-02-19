import sqlite3
import os
from app import create_app, db
from sqlalchemy import text

app = create_app('default')

def add_column_if_not_exists(cursor, table, col_name, col_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
        print(f"Added column {col_name} to {table}")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "no such table" in str(e).lower():
            # Already exists or table missing
            print(f"Skipping {col_name} (likely exists): {e}")
        else:
            print(f"Error adding {col_name}: {e}")

with app.app_context():
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    print(f"Target Database: {database_uri}")

    # Create new tables first (SQLAlchemy does this gracefully if not exists)
    try:
        db.create_all()
        print("Created new tables (Classes, AcademicYears) if they didn't exist.")
    except Exception as e:
        print(f"Table creation error: {e}")

    # Now handle column additions for existing tables manually
    # We need raw connection for ALTER TABLE if using SQLite
    
    if database_uri.startswith('sqlite'):
        db_path = database_uri.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            print("DB file not found, skipping migration.")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add columns to students table
            add_column_if_not_exists(cursor, 'students', 'class_id', 'INTEGER REFERENCES classes(id)')
            add_column_if_not_exists(cursor, 'students', 'academic_year_id', 'INTEGER REFERENCES academic_years(id)')
            
            conn.commit()
            conn.close()
            print("SQLite migration completed.")
            
    elif database_uri.startswith('mysql'):
        # For MySQL, we can use SQLAlchemy engine
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE students ADD COLUMN class_id INT"))
                conn.execute(text("ALTER TABLE students ADD FOREIGN KEY (class_id) REFERENCES classes(id)"))
                print("Added class_id to students (MySQL)")
            except Exception as e:
                print(f"MySQL error (class_id): {e}")
                
            try:
                conn.execute(text("ALTER TABLE students ADD COLUMN academic_year_id INT"))
                conn.execute(text("ALTER TABLE students ADD FOREIGN KEY (academic_year_id) REFERENCES academic_years(id)"))
                print("Added academic_year_id to students (MySQL)")
            except Exception as e:
                print(f"MySQL error (academic_year_id): {e}")

    print("Migration finished. Restart your app.")
