"""
Database migration script to add new columns to Customer and Doctor models
"""
import os
from sqlalchemy import text
from database import db

def migrate_database():
    # Import Flask app
    from main import app
    
    with app.app_context():
        
        print("Starting database migration...")
        
        try:
            # Add new columns to customers table
            print("Adding new columns to customers table...")
            
            # Check if columns exist before adding
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='customers' AND column_name IN ('age', 'gender', 'birth_date', 'email', 'emergency_contact_name', 'emergency_contact_phone', 'medical_notes')
            """))
            existing_customer_columns = [row[0] for row in result]
            
            customer_columns = [
                ("age", "INTEGER"),
                ("gender", "VARCHAR(10)"),
                ("birth_date", "DATE"),
                ("email", "VARCHAR(120)"),
                ("emergency_contact_name", "VARCHAR(200)"),
                ("emergency_contact_phone", "VARCHAR(20)"),
                ("medical_notes", "TEXT")
            ]
            
            for col_name, col_type in customer_columns:
                if col_name not in existing_customer_columns:
                    db.session.execute(text(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}"))
                    print(f"Added column: customers.{col_name}")
                else:
                    print(f"Column customers.{col_name} already exists, skipping...")
            
            # Add new columns to doctors table
            print("Adding new columns to doctors table...")
            
            # Check if columns exist before adding
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='doctors' AND column_name IN ('nik', 'age', 'gender', 'birth_date', 'email', 'practice_address', 'license_expiry_date')
            """))
            existing_doctor_columns = [row[0] for row in result]
            
            doctor_columns = [
                ("nik", "VARCHAR(16) UNIQUE NOT NULL DEFAULT ''"),
                ("age", "INTEGER"),
                ("gender", "VARCHAR(10)"),
                ("birth_date", "DATE"),
                ("email", "VARCHAR(120)"),
                ("practice_address", "TEXT"),
                ("license_expiry_date", "DATE")
            ]
            
            for col_name, col_type in doctor_columns:
                if col_name not in existing_doctor_columns:
                    # For NIK column, we need to handle the NOT NULL constraint carefully
                    if col_name == 'nik':
                        # First add the column as nullable
                        db.session.execute(text(f"ALTER TABLE doctors ADD COLUMN {col_name} VARCHAR(16)"))
                        # Set default values for existing records
                        db.session.execute(text(f"UPDATE doctors SET {col_name} = 'NIK' || id::text WHERE {col_name} IS NULL"))
                        # Then add the constraint
                        db.session.execute(text(f"ALTER TABLE doctors ALTER COLUMN {col_name} SET NOT NULL"))
                        db.session.execute(text(f"ALTER TABLE doctors ADD CONSTRAINT doctors_{col_name}_unique UNIQUE ({col_name})"))
                        print(f"Added column: doctors.{col_name} with constraints")
                    else:
                        db.session.execute(text(f"ALTER TABLE doctors ADD COLUMN {col_name} {col_type}"))
                        print(f"Added column: doctors.{col_name}")
                else:
                    print(f"Column doctors.{col_name} already exists, skipping...")
            
            db.session.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise e

if __name__ == '__main__':
    migrate_database()