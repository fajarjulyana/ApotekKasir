"""
Database migration script to add reminder system functionality
"""
import os
from sqlalchemy import text
from database import db

def migrate_reminder_system():
    # Import Flask app
    from main import app
    
    with app.app_context():
        
        print("Starting reminder system migration...")
        
        try:
            # Add new columns to notifications table
            print("Adding new columns to notifications table...")
            
            # Check if columns exist before adding
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='notifications' AND column_name IN ('customer_id', 'medicine_id', 'priority')
            """))
            existing_notification_columns = [row[0] for row in result]
            
            notification_columns = [
                ("customer_id", "INTEGER"),
                ("medicine_id", "INTEGER"),
                ("priority", "VARCHAR(10) DEFAULT 'normal'")
            ]
            
            for col_name, col_type in notification_columns:
                if col_name not in existing_notification_columns:
                    db.session.execute(text(f"ALTER TABLE notifications ADD COLUMN {col_name} {col_type}"))
                    print(f"Added column: notifications.{col_name}")
                else:
                    print(f"Column notifications.{col_name} already exists, skipping...")
            
            # Add foreign key constraints
            if 'customer_id' not in existing_notification_columns:
                db.session.execute(text("""
                    ALTER TABLE notifications 
                    ADD CONSTRAINT fk_notifications_customer_id 
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                """))
                print("Added foreign key constraint: notifications.customer_id")
                
            if 'medicine_id' not in existing_notification_columns:
                db.session.execute(text("""
                    ALTER TABLE notifications 
                    ADD CONSTRAINT fk_notifications_medicine_id 
                    FOREIGN KEY (medicine_id) REFERENCES medicines (id)
                """))
                print("Added foreign key constraint: notifications.medicine_id")
            
            # Create customer_waitlist table
            print("Creating customer_waitlist table...")
            
            # Check if table exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='customer_waitlist'
            """))
            
            if not result.fetchone():
                db.session.execute(text("""
                    CREATE TABLE customer_waitlist (
                        id SERIAL PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        medicine_id INTEGER NOT NULL,
                        quantity_needed INTEGER NOT NULL,
                        notes TEXT,
                        is_notified BOOLEAN DEFAULT FALSE,
                        notification_method VARCHAR(20) DEFAULT 'whatsapp',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notified_at TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers (id),
                        FOREIGN KEY (medicine_id) REFERENCES medicines (id),
                        UNIQUE (customer_id, medicine_id)
                    )
                """))
                print("Created customer_waitlist table")
            else:
                print("customer_waitlist table already exists, skipping...")
            
            db.session.commit()
            print("Reminder system migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise e

if __name__ == '__main__':
    migrate_reminder_system()