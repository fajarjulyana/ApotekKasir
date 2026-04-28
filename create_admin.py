"""
Script untuk membuat user admin default
"""
import os
from database import db

def create_admin_user():
    # Import Flask app
    from main import app
    
    with app.app_context():
        # Import models within app context
        from models import User, Category
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user sudah ada!")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@apotek.com',
            full_name='Administrator',
            role='admin',
            active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        
        # Create default categories if they don't exist
        default_categories = [
            {'name': 'Obat Bebas', 'description': 'Obat yang dapat dibeli tanpa resep dokter'},
            {'name': 'Obat Bebas Terbatas', 'description': 'Obat yang dapat dibeli tanpa resep dengan pengawasan apoteker'},
            {'name': 'Obat Keras', 'description': 'Obat yang memerlukan resep dokter'},
            {'name': 'Vitamin & Suplemen', 'description': 'Vitamin dan suplemen kesehatan'},
            {'name': 'Alat Kesehatan', 'description': 'Alat-alat kesehatan dan medis'}
        ]
        
        for cat_data in default_categories:
            if not Category.query.filter_by(name=cat_data['name']).first():
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
        
        try:
            db.session.commit()
            print("Admin user dan kategori default berhasil dibuat!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    create_admin_user()