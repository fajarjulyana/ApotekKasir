"""
Script migrasi database untuk menambahkan kolom baru di tabel medicines
"""
from sqlalchemy import text
from database import db
from main import app

def migrate_database():
    """Migrasi database untuk menambahkan kolom baru"""
    import os

    # Ensure upload directories exist
    os.makedirs('static/product', exist_ok=True)
    os.makedirs('static/logo', exist_ok=True)  
    os.makedirs('static/images', exist_ok=True)
    print("Upload directories created/verified")

    with app.app_context():
        try:
            # Check if barcode_id column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='barcode_id'
            """))

            if not result.fetchone():
                print("Adding barcode_id column...")
                db.session.execute(text("""
                    ALTER TABLE medicines 
                    ADD COLUMN barcode_id VARCHAR(50) UNIQUE;
                """))

                # Create index for barcode_id
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_medicines_barcode_id 
                    ON medicines(barcode_id);
                """))

            # Check and add capacity_numeric column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='capacity_numeric'
            """))

            if not result.fetchone():
                print("Adding capacity_numeric column...")
                db.session.execute(text("""
                    ALTER TABLE medicines 
                    ADD COLUMN capacity_numeric FLOAT;
                """))

            # Check and add capacity_unit column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='capacity_unit'
            """))

            if not result.fetchone():
                print("Adding capacity_unit column...")
                db.session.execute(text("""
                    ALTER TABLE medicines 
                    ADD COLUMN capacity_unit VARCHAR(10);
                """))

            # Check and add logo_url column to pharmacy_profile
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='pharmacy_profile' AND column_name='logo_url'
            """))

            if not result.fetchone():
                print("Adding logo_url column to pharmacy_profile...")
                db.session.execute(text("""
                    ALTER TABLE pharmacy_profile 
                    ADD COLUMN logo_url VARCHAR(500);
                """))

            # Check and add image_url column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='medicines' AND column_name='image_url'
            """))

            if not result.fetchone():
                print("Adding image_url column...")
                db.session.execute(text("""
                    ALTER TABLE medicines 
                    ADD COLUMN image_url VARCHAR(500);
                """))

            # Add cash_amount and change_amount columns to sales table
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sales' AND column_name='cash_amount'
            """))

            if not result.fetchone():
                print("Adding cash_amount column to sales table...")
                db.session.execute(text("""
                    ALTER TABLE sales 
                    ADD COLUMN cash_amount NUMERIC(10, 2);
                """))

            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sales' AND column_name='change_amount'
            """))

            if not result.fetchone():
                print("Adding change_amount column to sales table...")
                db.session.execute(text("""
                    ALTER TABLE sales 
                    ADD COLUMN change_amount NUMERIC(10, 2);
                """))

            # Add new customer and doctor fields to sales table
            new_columns = [
                ('customer_nik', 'VARCHAR(16)'),
                ('customer_whatsapp', 'VARCHAR(20)'),
                ('doctor_name', 'VARCHAR(200)'),
                ('doctor_phone', 'VARCHAR(20)'),
                ('doctor_whatsapp', 'VARCHAR(20)'),
                ('prescription_number', 'VARCHAR(100)'),
                ('is_prescription', 'BOOLEAN DEFAULT FALSE')
            ]

            for column_name, column_type in new_columns:
                result = db.session.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='sales' AND column_name='{column_name}'
                """))

                if not result.fetchone():
                    print(f"Adding {column_name} column to sales table...")
                    db.session.execute(text(f"""
                        ALTER TABLE sales 
                        ADD COLUMN {column_name} {column_type};
                    """))

            # Create customers table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    nik VARCHAR(16) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    whatsapp VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Create doctors table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    str_number VARCHAR(50) UNIQUE NOT NULL,
                    specialization VARCHAR(200),
                    phone VARCHAR(20),
                    whatsapp VARCHAR(20),
                    hospital_clinic VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Create indexes
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
                CREATE INDEX IF NOT EXISTS idx_customers_nik ON customers(nik);
                CREATE INDEX IF NOT EXISTS idx_doctors_name ON doctors(name);
                CREATE INDEX IF NOT EXISTS idx_sales_customer_nik ON sales(customer_nik);
            """))

            db.session.commit()

            # Generate barcode_id for existing medicines
            from models import Medicine
            medicines_without_barcode = Medicine.query.filter(
                (Medicine.barcode_id == None) | (Medicine.barcode_id == '')
            ).all()

            if medicines_without_barcode:
                print(f"Generating barcode_id for {len(medicines_without_barcode)} existing medicines...")

                for medicine in medicines_without_barcode:
                    if not medicine.barcode_id:
                        medicine.barcode_id = Medicine.generate_barcode_id()

                    # Parse capacity if exists
                    if medicine.capacity and not medicine.capacity_numeric:
                        medicine.parse_capacity()

                db.session.commit()
                print("Migration completed successfully!")
            else:
                print("All medicines already have barcode_id")

        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_database()