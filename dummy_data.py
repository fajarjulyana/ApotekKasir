"""
Script untuk membuat data dummy untuk pengujian sistem
Termasuk user berdasarkan role dan data obat untuk testing
"""
import os
from datetime import datetime, timedelta, date
from database import db

def create_dummy_data():
    # Import Flask app
    from main import app
    
    with app.app_context():
        from models import (User, Category, Medicine, MedicineBatch, Customer, Doctor, 
                           Notification, CustomerWaitlist, PharmacyProfile)
        
        print("Creating dummy data for testing...")
        
        try:
            # Create pharmacy profile if not exists
            if not PharmacyProfile.query.first():
                pharmacy_profile = PharmacyProfile(
                    name='Apotek Sehat Sentosa',
                    address='Jl. Kesehatan No. 123, Jakarta Pusat, DKI Jakarta 10430',
                    phone='(021) 3456789',
                    email='info@apoteksehatsentosa.com',
                    license_number='APT-001-2024',
                    pharmacist_name='Dra. Sarah Kusuma, Apt.'
                )
                db.session.add(pharmacy_profile)
                print("✅ Created pharmacy profile")
            
            # Create test users with different roles
            test_users = [
                {
                    'username': 'admin',
                    'email': 'admin@apotek.com',
                    'password': 'admin123',
                    'full_name': 'Administrator Sistem',
                    'role': 'admin'
                },
                {
                    'username': 'dr.sarah',
                    'email': 'sarah@apotek.com', 
                    'password': 'pharmacist123',
                    'full_name': 'Dra. Sarah Kusuma, Apt.',
                    'role': 'pharmacist'
                },
                {
                    'username': 'budi.restoker',
                    'email': 'budi@apotek.com',
                    'password': 'restoker123', 
                    'full_name': 'Budi Santoso',
                    'role': 'restoker'
                },
                {
                    'username': 'siti.pharmacist',
                    'email': 'siti@apotek.com',
                    'password': 'pharmacist456',
                    'full_name': 'Siti Rahayu, S.Farm.',
                    'role': 'pharmacist'
                }
            ]
            
            for user_data in test_users:
                if not User.query.filter_by(username=user_data['username']).first():
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        full_name=user_data['full_name'],
                        role=user_data['role'],
                        active=True
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
                else:
                    print(f"⏭️  User {user_data['username']} already exists")
            
            # Create test customers
            test_customers = [
                {
                    'name': 'Ibu Sari Dewi',
                    'nik': '3174012345678901',
                    'age': 45,
                    'gender': 'Wanita',
                    'birth_date': date(1978, 5, 15),
                    'phone': '081234567890',
                    'whatsapp': '081234567890',
                    'email': 'sari.dewi@email.com',
                    'address': 'Jl. Melati No. 45, Jakarta Selatan',
                    'emergency_contact_name': 'Pak Andi (Suami)',
                    'emergency_contact_phone': '081234567891',
                    'medical_notes': 'Alergi penisilin, riwayat hipertensi'
                },
                {
                    'name': 'Bapak Joko Susilo',
                    'nik': '3174012345678902',
                    'age': 52,
                    'gender': 'Pria',
                    'birth_date': date(1971, 8, 20),
                    'phone': '081234567892',
                    'whatsapp': '081234567892',
                    'email': 'joko.susilo@email.com',
                    'address': 'Jl. Mawar No. 12, Jakarta Timur',
                    'emergency_contact_name': 'Ibu Rina (Istri)',
                    'emergency_contact_phone': '081234567893',
                    'medical_notes': 'Diabetes mellitus tipe 2, pantangan gula'
                },
                {
                    'name': 'Adik Maya Putri',
                    'nik': '3174012345678903',
                    'age': 12,
                    'gender': 'Wanita',
                    'birth_date': date(2011, 3, 10),
                    'phone': '081234567894',
                    'whatsapp': '081234567894',
                    'address': 'Jl. Anggrek No. 8, Jakarta Barat',
                    'emergency_contact_name': 'Ibu Linda (Ibu)',
                    'emergency_contact_phone': '081234567895',
                    'medical_notes': 'Asma ringan, alergi debu'
                }
            ]
            
            for customer_data in test_customers:
                if not Customer.query.filter_by(nik=customer_data['nik']).first():
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                    print(f"✅ Created customer: {customer_data['name']}")
                else:
                    print(f"⏭️  Customer with NIK {customer_data['nik']} already exists")
            
            # Create test doctors
            test_doctors = [
                {
                    'name': 'dr. Ahmad Fauzi, Sp.PD',
                    'nik': '3174013456789101',
                    'str_number': 'STR-12345-2023',
                    'age': 42,
                    'gender': 'Pria',
                    'birth_date': date(1981, 4, 12),
                    'specialization': 'Spesialis Penyakit Dalam',
                    'phone': '081345678901',
                    'whatsapp': '081345678901',
                    'email': 'ahmad.fauzi@rs-sehat.com',
                    'hospital_clinic': 'RS Sehat Jakarta',
                    'practice_address': 'Jl. Sudirman No. 100, Jakarta Pusat',
                    'license_expiry_date': date(2026, 12, 31)
                },
                {
                    'name': 'dr. Lisa Permata, Sp.A',
                    'nik': '3174013456789102', 
                    'str_number': 'STR-12346-2023',
                    'age': 36,
                    'gender': 'Wanita',
                    'birth_date': date(1987, 9, 25),
                    'specialization': 'Spesialis Anak',
                    'phone': '081345678902',
                    'whatsapp': '081345678902',
                    'email': 'lisa.permata@klinik-anak.com',
                    'hospital_clinic': 'Klinik Anak Sehat',
                    'practice_address': 'Jl. Gatot Subroto No. 45, Jakarta Selatan',
                    'license_expiry_date': date(2025, 6, 30)
                },
                {
                    'name': 'dr. Budi Hartono',
                    'nik': '3174013456789103',
                    'str_number': 'STR-12347-2023', 
                    'age': 38,
                    'gender': 'Pria',
                    'birth_date': date(1985, 11, 8),
                    'specialization': 'Dokter Umum',
                    'phone': '081345678903',
                    'whatsapp': '081345678903',
                    'email': 'budi.hartono@puskesmas.go.id',
                    'hospital_clinic': 'Puskesmas Menteng',
                    'practice_address': 'Jl. Menteng Raya No. 15, Jakarta Pusat',
                    'license_expiry_date': date(2025, 12, 31)
                }
            ]
            
            for doctor_data in test_doctors:
                if not Doctor.query.filter_by(nik=doctor_data['nik']).first():
                    doctor = Doctor(**doctor_data)
                    db.session.add(doctor)
                    print(f"✅ Created doctor: {doctor_data['name']}")
                else:
                    print(f"⏭️  Doctor with NIK {doctor_data['nik']} already exists")
            
            # Create test medicines with batches
            test_medicines = [
                {
                    'name': 'Paracetamol 500mg',
                    'generic_name': 'Paracetamol',
                    'category_name': 'Obat Bebas',
                    'manufacturer': 'Kimia Farma',
                    'unit': 'tablet',
                    'capacity': '500mg',
                    'minimum_stock': 50,
                    'purchase_price': 150.0,
                    'selling_price': 300.0,
                    'description': 'Obat pereda demam dan nyeri',
                    'storage_location': 'Rak A-1',
                    'batches': [
                        {'batch_number': 'PCT001', 'quantity': 80, 'expiry_date': date(2025, 12, 31), 'supplier': 'PT Distributor Medis'},
                        {'batch_number': 'PCT002', 'quantity': 120, 'expiry_date': date(2026, 6, 30), 'supplier': 'PT Distributor Medis'}
                    ]
                },
                {
                    'name': 'Amoxicillin 500mg',
                    'generic_name': 'Amoxicillin',
                    'category_name': 'Obat Keras',
                    'manufacturer': 'Sanbe Farma',
                    'unit': 'kapsul',
                    'capacity': '500mg',
                    'minimum_stock': 30,
                    'purchase_price': 800.0,
                    'selling_price': 1500.0,
                    'description': 'Antibiotik untuk infeksi bakteri',
                    'storage_location': 'Rak B-2',
                    'batches': [
                        {'batch_number': 'AMX001', 'quantity': 15, 'expiry_date': date(2025, 8, 15), 'supplier': 'PT Pharma Distribusi'}
                    ]
                },
                {
                    'name': 'Vitamin C 1000mg',
                    'generic_name': 'Ascorbic Acid',
                    'category_name': 'Vitamin & Suplemen',
                    'manufacturer': 'Blackmores',
                    'unit': 'tablet',
                    'capacity': '1000mg',
                    'minimum_stock': 25,
                    'purchase_price': 2500.0,
                    'selling_price': 5000.0,
                    'description': 'Suplemen vitamin C untuk daya tahan tubuh',
                    'storage_location': 'Rak C-1',
                    'batches': [
                        {'batch_number': 'VIT001', 'quantity': 60, 'expiry_date': date(2026, 3, 31), 'supplier': 'PT Vitamin Sehat'}
                    ]
                },
                {
                    'name': 'Ibuprofen 400mg',
                    'generic_name': 'Ibuprofen',
                    'category_name': 'Obat Bebas Terbatas',
                    'manufacturer': 'Tempo Scan',
                    'unit': 'tablet',
                    'capacity': '400mg',
                    'minimum_stock': 40,
                    'purchase_price': 500.0,
                    'selling_price': 1000.0,
                    'description': 'Anti-inflamasi dan pereda nyeri',
                    'storage_location': 'Rak A-3',
                    'batches': [
                        {'batch_number': 'IBU001', 'quantity': 5, 'expiry_date': date(2025, 10, 15), 'supplier': 'PT Medical Supply'}
                    ]
                }
            ]
            
            for med_data in test_medicines:
                # Find or create category
                category = Category.query.filter_by(name=med_data['category_name']).first()
                if not category:
                    continue
                
                if not Medicine.query.filter_by(name=med_data['name']).first():
                    # Create medicine
                    medicine = Medicine(
                        name=med_data['name'],
                        generic_name=med_data['generic_name'],
                        category_id=category.id,
                        manufacturer=med_data['manufacturer'],
                        unit=med_data['unit'],
                        capacity=med_data['capacity'],
                        minimum_stock=med_data['minimum_stock'],
                        purchase_price=med_data['purchase_price'],
                        selling_price=med_data['selling_price'],
                        description=med_data['description'],
                        storage_location=med_data['storage_location']
                    )
                    db.session.add(medicine)
                    db.session.flush()  # To get the ID
                    
                    # Add batches
                    for batch_data in med_data['batches']:
                        batch = MedicineBatch(
                            medicine_id=medicine.id,
                            batch_number=batch_data['batch_number'],
                            quantity=batch_data['quantity'],
                            expiry_date=batch_data['expiry_date'],
                            purchase_price=med_data['purchase_price'],
                            supplier=batch_data['supplier']
                        )
                        db.session.add(batch)
                    
                    print(f"✅ Created medicine: {med_data['name']}")
                else:
                    print(f"⏭️  Medicine {med_data['name']} already exists")
            
            # Create test notifications
            admin_user = User.query.filter_by(role='admin').first()
            pharmacist_user = User.query.filter_by(role='pharmacist').first()
            
            if admin_user:
                test_notifications = [
                    {
                        'title': 'Stok Rendah: Amoxicillin 500mg',
                        'message': 'Obat Amoxicillin 500mg memiliki stok di bawah minimum (15 tersisa, minimum 30)',
                        'type': 'low_stock',
                        'user_id': admin_user.id,
                        'priority': 'high'
                    },
                    {
                        'title': 'Stok Rendah: Ibuprofen 400mg', 
                        'message': 'Obat Ibuprofen 400mg memiliki stok di bawah minimum (5 tersisa, minimum 40)',
                        'type': 'low_stock',
                        'user_id': admin_user.id,
                        'priority': 'high'
                    }
                ]
                
                for notif_data in test_notifications:
                    notification = Notification(**notif_data)
                    db.session.add(notification)
                
                print("✅ Created test notifications")
            
            # Create test waitlist entries
            customer1 = Customer.query.filter_by(name='Ibu Sari Dewi').first()
            customer2 = Customer.query.filter_by(name='Bapak Joko Susilo').first()
            amoxicillin = Medicine.query.filter_by(name='Amoxicillin 500mg').first()
            ibuprofen = Medicine.query.filter_by(name='Ibuprofen 400mg').first()
            
            if customer1 and amoxicillin:
                waitlist1 = CustomerWaitlist(
                    customer_id=customer1.id,
                    medicine_id=amoxicillin.id,
                    quantity_needed=20,
                    notes='Untuk pengobatan infeksi saluran kemih',
                    notification_method='whatsapp'
                )
                db.session.add(waitlist1)
                print("✅ Added customer to waitlist: Amoxicillin for Ibu Sari")
            
            if customer2 and ibuprofen:
                waitlist2 = CustomerWaitlist(
                    customer_id=customer2.id,
                    medicine_id=ibuprofen.id,
                    quantity_needed=10,
                    notes='Untuk nyeri sendi',
                    notification_method='whatsapp'
                )
                db.session.add(waitlist2)
                print("✅ Added customer to waitlist: Ibuprofen for Bapak Joko")
            
            db.session.commit()
            
            print("\\n🎉 Dummy data creation completed successfully!")
            print("\\n📋 Summary:")
            print(f"👥 Users: {User.query.count()} total")
            print(f"🏥 Customers: {Customer.query.count()} total")  
            print(f"👨‍⚕️ Doctors: {Doctor.query.count()} total")
            print(f"💊 Medicines: {Medicine.query.count()} total")
            print(f"📦 Medicine Batches: {MedicineBatch.query.count()} total")
            print(f"🔔 Notifications: {Notification.query.count()} total")
            print(f"⏳ Waitlist Entries: {CustomerWaitlist.query.count()} total")
            
            print("\\n🔑 Test Login Credentials:")
            for user_data in test_users:
                print(f"   {user_data['role'].title()}: {user_data['username']} / {user_data['password']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating dummy data: {e}")
            raise e

if __name__ == '__main__':
    create_dummy_data()