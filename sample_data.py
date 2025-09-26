
"""
Sample data untuk database apotek
Berisi obat-obatan dengan alternatifnya dan kategori
"""
from datetime import datetime, date, timedelta
from database import db
from main import app

def create_sample_data():
    """Buat data sample untuk testing"""
    with app.app_context():
        from models import Category, Medicine, MedicineBatch, User
        
        # Create categories
        categories_data = [
            {'name': 'Antidepresan', 'description': 'Obat untuk mengatasi depresi dan gangguan mood'},
            {'name': 'Obat Batuk', 'description': 'Obat untuk mengatasi batuk dan gangguan pernapasan'},
            {'name': 'Obat Maag', 'description': 'Obat untuk mengatasi gangguan lambung dan maag'},
            {'name': 'Obat Sakit Kepala', 'description': 'Obat untuk mengatasi sakit kepala dan migrain'},
            {'name': 'Vitamin & Suplemen', 'description': 'Vitamin dan suplemen untuk kesehatan'},
        ]
        
        for cat_data in categories_data:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        
        # Get category IDs
        antidepresan_cat = Category.query.filter_by(name='Antidepresan').first()
        batuk_cat = Category.query.filter_by(name='Obat Batuk').first()
        maag_cat = Category.query.filter_by(name='Obat Maag').first()
        sakit_kepala_cat = Category.query.filter_by(name='Obat Sakit Kepala').first()
        vitamin_cat = Category.query.filter_by(name='Vitamin & Suplemen').first()
        
        # Sample medicines data
        medicines_data = [
            # Antidepresan
            {
                'name': 'Depram',
                'generic_name': 'Sertraline',
                'category_id': antidepresan_cat.id,
                'manufacturer': 'Dexa Medica',
                'unit': 'Tablet',
                'capacity': '50mg',
                'minimum_stock': 20,
                'purchase_price': 15000,
                'selling_price': 18000,
                'description': 'Antidepresan golongan SSRI untuk mengatasi depresi',
                'storage_location': 'Rak A1'
            },
            {
                'name': 'Cipralex',
                'generic_name': 'Escitalopram',
                'category_id': antidepresan_cat.id,
                'manufacturer': 'Lundbeck',
                'unit': 'Tablet',
                'capacity': '10mg',
                'minimum_stock': 15,
                'purchase_price': 25000,
                'selling_price': 30000,
                'description': 'Antidepresan escitalopram untuk gangguan depresi dan kecemasan',
                'storage_location': 'Rak A1'
            },
            {
                'name': 'Escipra',
                'generic_name': 'Escitalopram',
                'category_id': antidepresan_cat.id,
                'manufacturer': 'Kalbe Farma',
                'unit': 'Tablet',
                'capacity': '10mg',
                'minimum_stock': 15,
                'purchase_price': 20000,
                'selling_price': 24000,
                'description': 'Alternatif Cipralex dengan kandungan escitalopram',
                'storage_location': 'Rak A1'
            },
            {
                'name': 'Escitalopram Oxalate',
                'generic_name': 'Escitalopram Oxalate',
                'category_id': antidepresan_cat.id,
                'manufacturer': 'Kimia Farma',
                'unit': 'Tablet',
                'capacity': '10mg',
                'minimum_stock': 10,
                'purchase_price': 18000,
                'selling_price': 22000,
                'description': 'Antidepresan generik escitalopram oxalate',
                'storage_location': 'Rak A1'
            },
            {
                'name': 'Talox',
                'generic_name': 'Escitalopram',
                'category_id': antidepresan_cat.id,
                'manufacturer': 'Novell Pharmaceutical',
                'unit': 'Tablet',
                'capacity': '10mg',
                'minimum_stock': 12,
                'purchase_price': 22000,
                'selling_price': 26000,
                'description': 'Antidepresan dengan kandungan escitalopram',
                'storage_location': 'Rak A1'
            },
            
            # Obat Batuk
            {
                'name': 'OBH Combi',
                'generic_name': 'Dextromethorphan HBr + Chlorpheniramine Maleate',
                'category_id': batuk_cat.id,
                'manufacturer': 'Indofarma',
                'unit': 'Botol',
                'capacity': '60ml',
                'minimum_stock': 25,
                'purchase_price': 8000,
                'selling_price': 12000,
                'description': 'Sirup obat batuk untuk batuk kering dan berdahak',
                'storage_location': 'Rak B1'
            },
            {
                'name': 'Bisolvon',
                'generic_name': 'Bromhexine HCl',
                'category_id': batuk_cat.id,
                'manufacturer': 'Boehringer Ingelheim',
                'unit': 'Tablet',
                'capacity': '8mg',
                'minimum_stock': 30,
                'purchase_price': 12000,
                'selling_price': 15000,
                'description': 'Obat pengencer dahak untuk batuk berdahak',
                'storage_location': 'Rak B1'
            },
            {
                'name': 'Woods Peppermint',
                'generic_name': 'Dextromethorphan + Chlorpheniramine',
                'category_id': batuk_cat.id,
                'manufacturer': 'Kalbe Farma',
                'unit': 'Botol',
                'capacity': '60ml',
                'minimum_stock': 20,
                'purchase_price': 10000,
                'selling_price': 14000,
                'description': 'Sirup obat batuk rasa peppermint',
                'storage_location': 'Rak B1'
            },
            {
                'name': 'Komix',
                'generic_name': 'Paracetamol + Phenylephrine + Chlorpheniramine',
                'category_id': batuk_cat.id,
                'manufacturer': 'Darya Varia',
                'unit': 'Sachet',
                'capacity': '5g',
                'minimum_stock': 50,
                'purchase_price': 2500,
                'selling_price': 3500,
                'description': 'Obat batuk pilek dalam bentuk sachet',
                'storage_location': 'Rak B1'
            },
            
            # Obat Maag
            {
                'name': 'Antasida DOEN',
                'generic_name': 'Aluminum Hydroxide + Magnesium Hydroxide',
                'category_id': maag_cat.id,
                'manufacturer': 'Kimia Farma',
                'unit': 'Tablet',
                'capacity': '500mg',
                'minimum_stock': 40,
                'purchase_price': 5000,
                'selling_price': 7500,
                'description': 'Antasida untuk menetralkan asam lambung',
                'storage_location': 'Rak C1'
            },
            {
                'name': 'Mylanta',
                'generic_name': 'Aluminum Hydroxide + Magnesium Hydroxide + Simethicone',
                'category_id': maag_cat.id,
                'manufacturer': 'Johnson & Johnson',
                'unit': 'Tablet',
                'capacity': '200mg',
                'minimum_stock': 30,
                'purchase_price': 8000,
                'selling_price': 12000,
                'description': 'Antasida dengan simethicone untuk mengatasi kembung',
                'storage_location': 'Rak C1'
            },
            {
                'name': 'Omeprazole',
                'generic_name': 'Omeprazole',
                'category_id': maag_cat.id,
                'manufacturer': 'Dexa Medica',
                'unit': 'Kapsul',
                'capacity': '20mg',
                'minimum_stock': 25,
                'purchase_price': 15000,
                'selling_price': 18000,
                'description': 'Proton pump inhibitor untuk mengurangi produksi asam lambung',
                'storage_location': 'Rak C1'
            },
            {
                'name': 'Lansoprazole',
                'generic_name': 'Lansoprazole',
                'category_id': maag_cat.id,
                'manufacturer': 'Kalbe Farma',
                'unit': 'Kapsul',
                'capacity': '30mg',
                'minimum_stock': 20,
                'purchase_price': 18000,
                'selling_price': 22000,
                'description': 'Alternatif omeprazole untuk mengatasi GERD',
                'storage_location': 'Rak C1'
            },
            
            # Obat Sakit Kepala
            {
                'name': 'Paramex',
                'generic_name': 'Paracetamol + Propyphenazone + Caffeine',
                'category_id': sakit_kepala_cat.id,
                'manufacturer': 'Bayer',
                'unit': 'Tablet',
                'capacity': '500mg',
                'minimum_stock': 50,
                'purchase_price': 3000,
                'selling_price': 4500,
                'description': 'Obat sakit kepala dan demam dengan kafein',
                'storage_location': 'Rak D1'
            },
            {
                'name': 'Bodrex',
                'generic_name': 'Paracetamol + Caffeine + Phenylephrine',
                'category_id': sakit_kepala_cat.id,
                'manufacturer': 'Tempo Scan Pacific',
                'unit': 'Tablet',
                'capacity': '500mg',
                'minimum_stock': 45,
                'purchase_price': 2800,
                'selling_price': 4000,
                'description': 'Alternatif Paramex untuk sakit kepala',
                'storage_location': 'Rak D1'
            },
            {
                'name': 'Panadol',
                'generic_name': 'Paracetamol',
                'category_id': sakit_kepala_cat.id,
                'manufacturer': 'GlaxoSmithKline',
                'unit': 'Tablet',
                'capacity': '500mg',
                'minimum_stock': 60,
                'purchase_price': 3500,
                'selling_price': 5000,
                'description': 'Paracetamol murni untuk demam dan sakit kepala',
                'storage_location': 'Rak D1'
            },
            {
                'name': 'Aspirin',
                'generic_name': 'Asam Asetilsalisilat',
                'category_id': sakit_kepala_cat.id,
                'manufacturer': 'Bayer',
                'unit': 'Tablet',
                'capacity': '500mg',
                'minimum_stock': 35,
                'purchase_price': 4000,
                'selling_price': 6000,
                'description': 'Anti-inflamasi untuk sakit kepala dan demam',
                'storage_location': 'Rak D1'
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'category_id': sakit_kepala_cat.id,
                'manufacturer': 'Kimia Farma',
                'unit': 'Tablet',
                'capacity': '400mg',
                'minimum_stock': 40,
                'purchase_price': 5000,
                'selling_price': 7500,
                'description': 'NSAID untuk nyeri dan inflamasi',
                'storage_location': 'Rak D1'
            },
        ]
        
        # Add medicines
        for med_data in medicines_data:
            existing = Medicine.query.filter_by(name=med_data['name']).first()
            if not existing:
                medicine = Medicine(**med_data)
                db.session.add(medicine)
                db.session.flush()  # Get the ID
                
                # Add sample batch for each medicine
                batch = MedicineBatch(
                    medicine_id=medicine.id,
                    batch_number=f"BATCH{medicine.id:03d}",
                    expiry_date=date.today() + timedelta(days=365),
                    quantity=100,
                    purchase_price=med_data['purchase_price'],
                    supplier=f"Supplier {med_data['manufacturer']}",
                    received_date=date.today()
                )
                db.session.add(batch)
        
        db.session.commit()
        print("Sample data berhasil ditambahkan!")

if __name__ == "__main__":
    create_sample_data()
