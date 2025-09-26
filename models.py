from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    """Model untuk user/pengguna sistem"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='kasir')  # admin, kasir
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class PharmacyProfile(db.Model):
    """Model untuk profil apotek"""
    __tablename__ = 'pharmacy_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    pharmacist_name = db.Column(db.String(120), nullable=False)
    logo_url = db.Column(db.String(500))  # URL atau path logo apotek
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(db.Model):
    """Model untuk kategori obat"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    medicines = db.relationship('Medicine', backref='category_ref', lazy=True)

class Medicine(db.Model):
    """Model untuk obat"""
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Auto-generated or manual barcode
    name = db.Column(db.String(200), nullable=False, index=True)
    generic_name = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    manufacturer = db.Column(db.String(200))
    unit = db.Column(db.String(50), nullable=False)  # tablet, kapsul, ml, dll
    capacity = db.Column(db.String(50), index=True)  # 500mg, 100ml, dll
    capacity_numeric = db.Column(db.Float)  # Nilai numerik untuk pencarian
    capacity_unit = db.Column(db.String(10))  # mg, ml, gram, dll
    minimum_stock = db.Column(db.Integer, default=10)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    barcode = db.Column(db.String(50), unique=True)  # Legacy field for backward compatibility
    description = db.Column(db.Text)
    storage_location = db.Column(db.String(100))
    image_url = db.Column(db.String(500))  # URL atau path gambar kemasan
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    batches = db.relationship('MedicineBatch', backref='medicine_ref', lazy=True, cascade='all, delete-orphan')
    sale_items = db.relationship('SaleItem', backref='medicine_ref', lazy=True)
    
    @property
    def total_quantity(self):
        """Total stok dari semua batch yang belum kadaluwarsa"""
        today = datetime.now().date()
        return sum(batch.quantity for batch in self.batches 
                  if batch.expiry_date > today and batch.quantity > 0)
    
    @property
    def is_low_stock(self):
        """Cek apakah stok rendah"""
        return self.total_quantity <= self.minimum_stock
    
    def expiring_batches(self, days_ahead=14):
        """Batch yang akan kadaluwarsa dalam waktu tertentu"""
        cutoff_date = datetime.now().date() + timedelta(days=days_ahead)
        return [batch for batch in self.batches 
                if batch.expiry_date <= cutoff_date and batch.quantity > 0]
    
    @staticmethod
    def generate_barcode_id():
        """Generate unique barcode ID"""
        import random
        import string
        while True:
            # Format: APT + 6 digit random numbers + year
            random_part = ''.join(random.choices(string.digits, k=6))
            year = datetime.now().strftime('%y')
            barcode_id = f"APT{random_part}{year}"
            
            # Check if already exists
            if not Medicine.query.filter_by(barcode_id=barcode_id).first():
                return barcode_id
    
    def parse_capacity(self):
        """Parse capacity string to numeric value and unit"""
        if not self.capacity:
            return
            
        import re
        # Extract numeric value and unit from capacity string
        match = re.match(r'(\d+(?:\.\d+)?)\s*(\w+)', self.capacity.lower())
        if match:
            self.capacity_numeric = float(match.group(1))
            self.capacity_unit = match.group(2)
    
    def __init__(self, **kwargs):
        # Auto-generate barcode_id if not provided
        if 'barcode_id' not in kwargs or not kwargs['barcode_id']:
            kwargs['barcode_id'] = self.generate_barcode_id()
        
        super(Medicine, self).__init__(**kwargs)
        
        # Parse capacity after initialization
        if self.capacity:
            self.parse_capacity()

class MedicineBatch(db.Model):
    """Model untuk batch obat dengan tanggal kadaluwarsa"""
    __tablename__ = 'medicine_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    supplier = db.Column(db.String(200))
    received_date = db.Column(db.Date, default=datetime.now().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_expired(self):
        return self.expiry_date < datetime.now().date()
    
    @property
    def days_to_expiry(self):
        return (self.expiry_date - datetime.now().date()).days

class Sale(db.Model):
    """Model untuk transaksi penjualan"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200))
    customer_nik = db.Column(db.String(16), index=True)  # NIK pembeli (16 digit)
    customer_phone = db.Column(db.String(20))
    customer_whatsapp = db.Column(db.String(20))  # Nomor WA pembeli
    doctor_name = db.Column(db.String(200))  # Nama dokter untuk resep
    doctor_phone = db.Column(db.String(20))  # Nomor telepon dokter
    doctor_whatsapp = db.Column(db.String(20))  # Nomor WA dokter
    prescription_number = db.Column(db.String(100))  # Nomor resep dokter
    is_prescription = db.Column(db.Boolean, default=False)  # Apakah transaksi berdasarkan resep
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), default='cash')  # cash, credit_card, debit_card, digital_wallet
    cash_amount = db.Column(db.Numeric(10, 2))  # Jumlah uang cash yang dibayarkan
    change_amount = db.Column(db.Numeric(10, 2))  # Kembalian
    notes = db.Column(db.Text)
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sale_items = db.relationship('SaleItem', backref='sale_ref', lazy=True, cascade='all, delete-orphan')
    cashier = db.relationship('User', backref='sales', lazy=True)

class SaleItem(db.Model):
    """Model untuk item dalam transaksi penjualan"""
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('medicine_batches.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    batch = db.relationship('MedicineBatch', backref='sale_items', lazy=True)

class Customer(db.Model):
    """Model untuk data pelanggan"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    nik = db.Column(db.String(16), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Doctor(db.Model):
    """Model untuk data dokter"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    str_number = db.Column(db.String(50), unique=True, nullable=False)  # Nomor STR dokter
    specialization = db.Column(db.String(200))  # Spesialisasi dokter
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    hospital_clinic = db.Column(db.String(200))  # Rumah sakit/klinik tempat praktik
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    """Model untuk notifikasi sistem"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # expiry, low_stock, restock
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

# Utility functions
def get_expiring_medicines(days_ahead=14):
    """Dapatkan obat yang akan kadaluwarsa dalam waktu tertentu"""
    cutoff_date = datetime.now().date() + timedelta(days=days_ahead)
    
    expiring_batches = MedicineBatch.query.filter(
        MedicineBatch.expiry_date <= cutoff_date,
        MedicineBatch.quantity > 0
    ).all()
    
    medicines = {}
    for batch in expiring_batches:
        if batch.medicine_id not in medicines:
            medicines[batch.medicine_id] = {
                'medicine': batch.medicine_ref,
                'batches': [],
                'total_quantity': 0
            }
        medicines[batch.medicine_id]['batches'].append(batch)
        medicines[batch.medicine_id]['total_quantity'] += batch.quantity
    
    return list(medicines.values())

def get_low_stock_medicines():
    """Dapatkan obat dengan stok rendah"""
    medicines = Medicine.query.filter(Medicine.active == True).all()
    low_stock = []
    
    for medicine in medicines:
        if medicine.is_low_stock:
            low_stock.append(medicine)
    
    return low_stock

def get_top_selling_medicines(days=30, limit=10):
    """Dapatkan obat terlaris dalam periode tertentu"""
    from sqlalchemy import func
    
    start_date = datetime.now() - timedelta(days=days)
    
    top_selling = db.session.query(
        Medicine.id,
        Medicine.name,
        func.sum(SaleItem.quantity).label('total_sold'),
        func.sum(SaleItem.total_price).label('total_revenue')
    ).join(
        SaleItem, Medicine.id == SaleItem.medicine_id
    ).join(
        Sale, SaleItem.sale_id == Sale.id
    ).filter(
        Sale.created_at >= start_date
    ).group_by(
        Medicine.id, Medicine.name
    ).order_by(
        func.sum(SaleItem.quantity).desc()
    ).limit(limit).all()
    
    return top_selling

def get_alternative_medicines(medicine_id):
    """Dapatkan rekomendasi obat alternatif berdasarkan kategori dan kapasitas"""
    medicine = Medicine.query.get(medicine_id)
    if not medicine:
        return []
    
    # Prioritas 1: Kategori sama, kapasitas sama
    exact_alternatives = Medicine.query.filter(
        Medicine.id != medicine_id,
        Medicine.category_id == medicine.category_id,
        Medicine.capacity == medicine.capacity,
        Medicine.active == True,
        Medicine.total_quantity > 0
    ).all()
    
    if exact_alternatives:
        return exact_alternatives
    
    # Prioritas 2: Kategori sama, kapasitas numerik mirip (±20%)
    if medicine.capacity_numeric:
        tolerance = medicine.capacity_numeric * 0.2
        min_capacity = medicine.capacity_numeric - tolerance
        max_capacity = medicine.capacity_numeric + tolerance
        
        similar_alternatives = Medicine.query.filter(
            Medicine.id != medicine_id,
            Medicine.category_id == medicine.category_id,
            Medicine.capacity_numeric.between(min_capacity, max_capacity),
            Medicine.capacity_unit == medicine.capacity_unit,
            Medicine.active == True,
            Medicine.total_quantity > 0
        ).all()
        
        if similar_alternatives:
            return similar_alternatives
    
    # Prioritas 3: Kategori sama, generic name sama
    if medicine.generic_name:
        generic_alternatives = Medicine.query.filter(
            Medicine.id != medicine_id,
            Medicine.generic_name.ilike(f'%{medicine.generic_name}%'),
            Medicine.active == True,
            Medicine.total_quantity > 0
        ).all()
        
        if generic_alternatives:
            return generic_alternatives
    
    # Prioritas 4: Kategori sama saja
    category_alternatives = Medicine.query.filter(
        Medicine.id != medicine_id,
        Medicine.category_id == medicine.category_id,
        Medicine.active == True,
        Medicine.total_quantity > 0
    ).limit(10).all()
    
    return category_alternatives

def search_alternative_medicines(query, category_id=None):
    """Pencarian obat alternatif berdasarkan query dan kategori"""
    from sqlalchemy import or_
    
    base_query = Medicine.query.filter(
        Medicine.active == True,
        Medicine.total_quantity > 0
    )
    
    if category_id:
        base_query = base_query.filter(Medicine.category_id == category_id)
    
    if query:
        search_conditions = [
            Medicine.name.ilike(f'%{query}%'),
            Medicine.generic_name.ilike(f'%{query}%'),
            Medicine.manufacturer.ilike(f'%{query}%'),
            Medicine.capacity.ilike(f'%{query}%')
        ]
        base_query = base_query.filter(or_(*search_conditions))
    
    return base_query.order_by(Medicine.name).limit(20).all()

def get_out_of_stock_medicines():
    """Dapatkan obat yang habis stok"""
    medicines = Medicine.query.filter(Medicine.active == True).all()
    out_of_stock = []
    
    for medicine in medicines:
        if medicine.total_quantity == 0:
            out_of_stock.append(medicine)
    
    return out_of_stock

def search_medicines_advanced(query, search_type='all'):
    """Pencarian obat canggih berdasarkan berbagai kriteria"""
    from sqlalchemy import or_, and_
    
    base_query = Medicine.query.filter(Medicine.active == True)
    
    if not query:
        return base_query.limit(20).all()
    
    query = query.strip()
    
    if search_type == 'barcode_id':
        # Pencarian berdasarkan barcode ID
        return base_query.filter(Medicine.barcode_id.ilike(f'%{query}%')).all()
    
    elif search_type == 'barcode':
        # Pencarian berdasarkan barcode legacy
        return base_query.filter(Medicine.barcode.ilike(f'%{query}%')).all()
    
    elif search_type == 'capacity':
        # Pencarian berdasarkan kapasitas
        try:
            import re
            # Extract numeric value from query
            match = re.match(r'(\d+(?:\.\d+)?)', query)
            if match:
                numeric_value = float(match.group(1))
                return base_query.filter(Medicine.capacity_numeric == numeric_value).all()
            else:
                return base_query.filter(Medicine.capacity.ilike(f'%{query}%')).all()
        except:
            return base_query.filter(Medicine.capacity.ilike(f'%{query}%')).all()
    
    else:
        # Pencarian umum (nama, barcode_id, barcode, capacity)
        search_conditions = [
            Medicine.name.ilike(f'%{query}%'),
            Medicine.generic_name.ilike(f'%{query}%'),
            Medicine.barcode_id.ilike(f'%{query}%'),
            Medicine.barcode.ilike(f'%{query}%'),
            Medicine.capacity.ilike(f'%{query}%'),
            Medicine.manufacturer.ilike(f'%{query}%')
        ]
        
        return base_query.filter(or_(*search_conditions)).limit(20).all()

def search_customers(query):
    """Pencarian pelanggan berdasarkan nama atau NIK"""
    from sqlalchemy import or_
    
    if not query:
        return []
    
    query = query.strip()
    
    search_conditions = [
        Customer.name.ilike(f'%{query}%'),
        Customer.nik.ilike(f'%{query}%')
    ]
    
    return Customer.query.filter(or_(*search_conditions)).order_by(Customer.name).limit(10).all()

def search_doctors(query):
    """Pencarian dokter berdasarkan nama atau nomor STR"""
    from sqlalchemy import or_
    
    if not query:
        return []
    
    query = query.strip()
    
    search_conditions = [
        Doctor.name.ilike(f'%{query}%'),
        Doctor.str_number.ilike(f'%{query}%'),
        Doctor.specialization.ilike(f'%{query}%')
    ]
    
    return Doctor.query.filter(or_(*search_conditions)).order_by(Doctor.name).limit(10).all()