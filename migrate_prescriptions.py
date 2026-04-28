"""
Database migration script to add prescription management functionality
"""
import os
from sqlalchemy import text
from database import db

def migrate_prescriptions():
    # Import Flask app
    from main import app
    
    with app.app_context():
        
        print("Starting prescription system migration...")
        
        try:
            # Create prescriptions table
            print("Creating prescriptions table...")
            
            # Check if table exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='prescriptions'
            """))
            
            if not result.fetchone():
                db.session.execute(text("""
                    CREATE TABLE prescriptions (
                        id SERIAL PRIMARY KEY,
                        prescription_number VARCHAR(50) UNIQUE NOT NULL,
                        customer_id INTEGER NOT NULL,
                        doctor_id INTEGER NOT NULL,
                        uploaded_by INTEGER NOT NULL,
                        image_filename VARCHAR(255) NOT NULL,
                        image_path VARCHAR(500) NOT NULL,
                        file_size INTEGER,
                        diagnosis TEXT,
                        notes TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        prescription_date DATE NOT NULL,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP,
                        processed_by INTEGER,
                        FOREIGN KEY (customer_id) REFERENCES customers (id),
                        FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                        FOREIGN KEY (uploaded_by) REFERENCES users (id),
                        FOREIGN KEY (processed_by) REFERENCES users (id)
                    )
                """))
                print("Created prescriptions table")
            else:
                print("prescriptions table already exists, skipping...")
            
            # Create prescription_items table
            print("Creating prescription_items table...")
            
            # Check if table exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='prescription_items'
            """))
            
            if not result.fetchone():
                db.session.execute(text("""
                    CREATE TABLE prescription_items (
                        id SERIAL PRIMARY KEY,
                        prescription_id INTEGER NOT NULL,
                        medicine_id INTEGER,
                        medicine_name VARCHAR(200) NOT NULL,
                        dosage VARCHAR(100),
                        quantity INTEGER NOT NULL,
                        instructions TEXT,
                        quantity_fulfilled INTEGER DEFAULT 0,
                        is_available BOOLEAN DEFAULT TRUE,
                        substitution_medicine_id INTEGER,
                        substitution_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
                        FOREIGN KEY (medicine_id) REFERENCES medicines (id),
                        FOREIGN KEY (substitution_medicine_id) REFERENCES medicines (id)
                    )
                """))
                print("Created prescription_items table")
            else:
                print("prescription_items table already exists, skipping...")
            
            db.session.commit()
            print("Prescription system migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise e

if __name__ == '__main__':
    migrate_prescriptions()