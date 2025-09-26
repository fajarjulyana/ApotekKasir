"""
Route handlers untuk aplikasi manajemen apotek
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO
import os
from werkzeug.utils import secure_filename

from database import db

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # Route untuk manajemen inventory
    @app.route('/inventory')
    @login_required
    def inventory():
        """Halaman manajemen inventory obat"""
        from models import Medicine, Category
        medicines = Medicine.query.filter_by(active=True).all()
        categories = Category.query.all()
        return render_template('inventory.html', medicines=medicines, categories=categories)

    @app.route('/inventory/add', methods=['GET', 'POST'])
    @login_required
    def add_medicine():
        """Tambah obat baru"""
        from models import Medicine, Category
        import os
        from werkzeug.utils import secure_filename
        
        if request.method == 'POST':
            try:
                # Handle image upload
                image_url = None
                if 'medicine_image' in request.files:
                    file = request.files['medicine_image']
                    if file and file.filename and file.filename != '':
                        # Create uploads directory if not exists
                        upload_folder = os.path.join(app.static_folder, 'product')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Secure filename
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid conflicts
                        import time
                        timestamp = str(int(time.time()))
                        name, ext = os.path.splitext(filename)
                        filename = f"medicine_{name}_{timestamp}{ext}"
                        
                        file_path = os.path.join(upload_folder, filename)
                        file.save(file_path)
                        image_url = f'/static/product/{filename}'
                
                medicine = Medicine(
                    name=request.form['name'],
                    generic_name=request.form.get('generic_name'),
                    category_id=request.form['category_id'],
                    manufacturer=request.form.get('manufacturer'),
                    unit=request.form['unit'],
                    capacity=request.form.get('capacity'),
                    minimum_stock=int(request.form['minimum_stock']),
                    purchase_price=float(request.form['purchase_price']),
                    selling_price=float(request.form['selling_price']),
                    barcode_id=request.form.get('barcode_id'),  # New barcode ID system
                    barcode=request.form.get('barcode'),        # Legacy barcode
                    description=request.form.get('description'),
                    storage_location=request.form.get('storage_location'),
                    image_url=image_url
                )
                db.session.add(medicine)
                db.session.commit()
                flash('Obat berhasil ditambahkan!', 'success')
                return redirect(url_for('inventory'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error menambahkan obat: {str(e)}', 'error')
        
        categories = Category.query.all()
        return render_template('add_medicine.html', categories=categories)

    @app.route('/inventory/batch/add/<int:medicine_id>', methods=['GET', 'POST'])
    @login_required
    def add_batch(medicine_id):
        """Tambah batch obat"""
        from models import Medicine, MedicineBatch
        medicine = Medicine.query.get_or_404(medicine_id)
        
        if request.method == 'POST':
            try:
                batch = MedicineBatch(
                    medicine_id=medicine_id,
                    batch_number=request.form['batch_number'],
                    expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date(),
                    quantity=int(request.form['quantity']),
                    purchase_price=float(request.form['purchase_price']),
                    supplier=request.form.get('supplier'),
                    received_date=datetime.strptime(request.form['received_date'], '%Y-%m-%d').date()
                )
                db.session.add(batch)
                db.session.commit()
                flash('Batch obat berhasil ditambahkan!', 'success')
                return redirect(url_for('inventory'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error menambahkan batch: {str(e)}', 'error')
        
        return render_template('add_batch.html', medicine=medicine)

    @app.route('/notifications')
    @login_required
    def notifications():
        """Halaman notifikasi"""
        from models import get_expiring_medicines, get_low_stock_medicines
        expiring_medicines = get_expiring_medicines()
        low_stock_medicines = get_low_stock_medicines()
        
        return render_template('notifications.html', 
                             expiring_medicines=expiring_medicines,
                             low_stock_medicines=low_stock_medicines)

    @app.route('/restock')
    @login_required
    def restock():
        """Halaman daftar restock"""
        from models import get_low_stock_medicines
        low_stock_medicines = get_low_stock_medicines()
        return render_template('restock.html', medicines=low_stock_medicines)

    @app.route('/sales')
    @login_required
    def sales():
        """Halaman transaksi penjualan"""
        return render_template('sales.html')

    @app.route('/reports')
    @login_required
    def reports():
        """Halaman laporan"""
        from models import get_top_selling_medicines, Sale
        # Top selling medicines in last 30 days
        top_selling = get_top_selling_medicines(days=30, limit=10)
        
        # Sales summary
        today = datetime.now().date()
        monthly_sales = Sale.query.filter(
            Sale.created_at >= datetime(today.year, today.month, 1)
        ).all()
        
        return render_template('reports.html', 
                             top_selling=top_selling,
                             monthly_sales=monthly_sales)

    @app.route('/export/inventory')
    @login_required
    def export_inventory():
        """Export inventory ke Excel"""
        from models import Medicine
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventory Report"
        
        # Headers
        headers = ['Nama Obat', 'Kategori', 'Stok', 'Stok Minimum', 'Harga Beli', 'Harga Jual', 'Status']
        ws.append(headers)
        
        # Data
        medicines = Medicine.query.filter_by(active=True).all()
        for medicine in medicines:
            status = 'Stok Rendah' if medicine.is_low_stock else 'Normal'
            ws.append([
                medicine.name,
                medicine.category_ref.name if medicine.category_ref else '',
                medicine.total_quantity,
                medicine.minimum_stock,
                float(medicine.purchase_price),
                float(medicine.selling_price),
                status
            ])
        
        # Save to memory
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=f'inventory_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    @app.route('/profile')
    @login_required
    def pharmacy_profile():
        """Halaman profil apotek"""
        from models import PharmacyProfile
        profile = PharmacyProfile.query.first()
        return render_template('pharmacy_profile.html', profile=profile)

    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_pharmacy_profile():
        """Edit profil apotek"""
        from models import PharmacyProfile
        if not current_user.is_admin():
            flash('Hanya admin yang dapat mengedit profil apotek!', 'error')
            return redirect(url_for('pharmacy_profile'))
        
        profile = PharmacyProfile.query.first()
        
        if request.method == 'POST':
            try:
                # Handle logo upload
                logo_url = None
                if 'pharmacy_logo' in request.files:
                    file = request.files['pharmacy_logo']
                    if file and file.filename and file.filename != '':
                        # Create uploads directory if not exists
                        upload_folder = os.path.join(app.static_folder, 'logo')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Secure filename
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid conflicts
                        import time
                        timestamp = str(int(time.time()))
                        name, ext = os.path.splitext(filename)
                        filename = f"pharmacy_logo_{timestamp}{ext}"
                        
                        file_path = os.path.join(upload_folder, filename)
                        file.save(file_path)
                        logo_url = f'/static/logo/{filename}'
                
                if profile:
                    profile.name = request.form['name']
                    profile.address = request.form['address']
                    profile.phone = request.form['phone']
                    profile.email = request.form['email']
                    profile.license_number = request.form['license_number']
                    profile.pharmacist_name = request.form['pharmacist_name']
                    if logo_url:
                        profile.logo_url = logo_url
                    profile.updated_at = datetime.utcnow()
                else:
                    profile = PharmacyProfile(
                        name=request.form['name'],
                        address=request.form['address'],
                        phone=request.form['phone'],
                        email=request.form['email'],
                        license_number=request.form['license_number'],
                        pharmacist_name=request.form['pharmacist_name'],
                        logo_url=logo_url
                    )
                    db.session.add(profile)
                
                db.session.commit()
                flash('Profil apotek berhasil diperbarui!', 'success')
                return redirect(url_for('pharmacy_profile'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error memperbarui profil: {str(e)}', 'error')
        
        return render_template('edit_pharmacy_profile.html', profile=profile)

    @app.route('/api/search/medicines')
    @login_required
    def api_search_medicines():
        """API untuk mencari obat dengan fitur advanced search"""
        from models import search_medicines_advanced
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        if len(query) < 1:
            return jsonify([])
        
        medicines = search_medicines_advanced(query, search_type)
        
        results = []
        for medicine in medicines:
            results.append({
                'id': medicine.id,
                'barcode_id': medicine.barcode_id,
                'name': medicine.name,
                'generic_name': medicine.generic_name,
                'capacity': medicine.capacity,
                'stock': medicine.total_quantity,
                'price': float(medicine.selling_price),
                'unit': medicine.unit,
                'storage_location': medicine.storage_location,
                'image_url': medicine.image_url,
                'category': medicine.category_ref.name if medicine.category_ref else None
            })
        
        return jsonify(results)

    @app.route('/api/medicine/<int:medicine_id>/alternatives')
    @login_required
    def api_medicine_alternatives(medicine_id):
        """API untuk mendapatkan alternatif obat"""
        from models import get_alternative_medicines
        alternatives = get_alternative_medicines(medicine_id)
        
        results = []
        for medicine in alternatives:
            results.append({
                'id': medicine.id,
                'barcode_id': medicine.barcode_id,
                'name': medicine.name,
                'generic_name': medicine.generic_name,
                'capacity': medicine.capacity,
                'price': float(medicine.selling_price),
                'stock': medicine.total_quantity,
                'unit': medicine.unit,
                'manufacturer': medicine.manufacturer,
                'storage_location': medicine.storage_location,
                'image_url': medicine.image_url,
                'category': medicine.category_ref.name if medicine.category_ref else None
            })
        
        return jsonify(results)

    @app.route('/api/alternatives/search')
    @login_required
    def api_search_alternatives():
        """API untuk mencari alternatif obat berdasarkan nama atau kategori"""
        from models import search_alternative_medicines
        query = request.args.get('q', '')
        category_id = request.args.get('category_id', type=int)
        
        alternatives = search_alternative_medicines(query, category_id)
        
        results = []
        for medicine in alternatives:
            results.append({
                'id': medicine.id,
                'barcode_id': medicine.barcode_id,
                'name': medicine.name,
                'generic_name': medicine.generic_name,
                'capacity': medicine.capacity,
                'price': float(medicine.selling_price),
                'stock': medicine.total_quantity,
                'unit': medicine.unit,
                'manufacturer': medicine.manufacturer,
                'storage_location': medicine.storage_location,
                'image_url': medicine.image_url,
                'category': medicine.category_ref.name if medicine.category_ref else None,
                'is_low_stock': medicine.is_low_stock
            })
        
        return jsonify(results)

    @app.route('/categories')
    @login_required
    def categories():
        """Halaman kelola kategori"""
        from models import Category
        categories = Category.query.order_by(Category.name).all()
        return render_template('categories.html', categories=categories)

    @app.route('/categories/add', methods=['POST'])
    @login_required
    def add_category():
        """Tambah kategori baru"""
        from models import Category
        if not current_user.is_admin():
            flash('Hanya admin yang dapat menambah kategori!', 'error')
            return redirect(url_for('categories'))
        
        try:
            category = Category(
                name=request.form['name'],
                description=request.form.get('description')
            )
            db.session.add(category)
            db.session.commit()
            flash('Kategori berhasil ditambahkan!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error menambahkan kategori: {str(e)}', 'error')
        
        return redirect(url_for('categories'))

    @app.route('/categories/<int:category_id>/edit', methods=['POST'])
    @login_required
    def edit_category(category_id):
        """Edit kategori"""
        from models import Category
        if not current_user.is_admin():
            flash('Hanya admin yang dapat mengedit kategori!', 'error')
            return redirect(url_for('categories'))
        
        category = Category.query.get_or_404(category_id)
        
        try:
            category.name = request.form['name']
            category.description = request.form.get('description')
            db.session.commit()
            flash('Kategori berhasil diperbarui!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error memperbarui kategori: {str(e)}', 'error')
        
        return redirect(url_for('categories'))

    @app.route('/categories/<int:category_id>/delete', methods=['POST'])
    @login_required
    def delete_category(category_id):
        """Hapus kategori"""
        from models import Category, Medicine
        if not current_user.is_admin():
            flash('Hanya admin yang dapat menghapus kategori!', 'error')
            return redirect(url_for('categories'))
        
        category = Category.query.get_or_404(category_id)
        
        # Check if category has medicines
        medicine_count = Medicine.query.filter_by(category_id=category_id).count()
        if medicine_count > 0:
            flash(f'Tidak dapat menghapus kategori yang masih memiliki {medicine_count} obat!', 'error')
            return redirect(url_for('categories'))
        
        try:
            db.session.delete(category)
            db.session.commit()
            flash('Kategori berhasil dihapus!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error menghapus kategori: {str(e)}', 'error')
        
        return redirect(url_for('categories'))

    @app.route('/api/medicine/<int:medicine_id>/barcode')
    @login_required
    def generate_barcode(medicine_id):
        """Generate barcode image untuk obat"""
        from models import Medicine
        import qrcode
        from io import BytesIO
        import base64
        
        medicine = Medicine.query.get_or_404(medicine_id)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(medicine.barcode_id)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'barcode_id': medicine.barcode_id,
            'image': f'data:image/png;base64,{img_str}'
        })

    @app.route('/static/product/<filename>')
    def serve_product_image(filename):
        """Serve product images with fallback"""
        import os
        from flask import send_from_directory, abort
        
        file_path = os.path.join(app.static_folder, 'product', filename)
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(app.static_folder, 'product'), filename)
        else:
            # Return placeholder if file doesn't exist
            return send_from_directory(os.path.join(app.static_folder, 'images'), 'no-image.png')
    
    @app.route('/static/logo/<filename>')
    def serve_logo_image(filename):
        """Serve logo images with fallback"""
        import os
        from flask import send_from_directory, abort
        
        file_path = os.path.join(app.static_folder, 'logo', filename)
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(app.static_folder, 'logo'), filename)
        else:
            # Return placeholder if file doesn't exist
            return send_from_directory(os.path.join(app.static_folder, 'images'), 'no-image.png')

    @app.route('/api/notifications/count')
    @login_required
    def get_notification_count():
        """Get count of notifications for navbar badge"""
        from models import get_expiring_medicines, get_low_stock_medicines
        
        expiring_count = len(get_expiring_medicines())
        low_stock_count = len(get_low_stock_medicines())
        total_notifications = expiring_count + low_stock_count
        
        return jsonify({
            'total': total_notifications,
            'expiring': expiring_count,
            'low_stock': low_stock_count
        })

    @app.route('/api/search/customers')
    @login_required
    def api_search_customers():
        """API untuk mencari pelanggan"""
        from models import search_customers, Customer
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify([])
        
        customers = search_customers(query)
        
        results = []
        for customer in customers:
            results.append({
                'id': customer.id,
                'name': customer.name,
                'nik': customer.nik,
                'phone': customer.phone,
                'whatsapp': customer.whatsapp
            })
        
        return jsonify(results)

    @app.route('/api/search/doctors')
    @login_required
    def api_search_doctors():
        """API untuk mencari dokter"""
        from models import search_doctors, Doctor
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify([])
        
        doctors = search_doctors(query)
        
        results = []
        for doctor in doctors:
            results.append({
                'id': doctor.id,
                'name': doctor.name,
                'str_number': doctor.str_number,
                'specialization': doctor.specialization,
                'phone': doctor.phone,
                'whatsapp': doctor.whatsapp,
                'hospital_clinic': doctor.hospital_clinic
            })
        
        return jsonify(results)

    @app.route('/api/sales/create', methods=['POST'])
    @login_required
    def create_sale():
        """Create new sale transaction"""
        from models import Sale, SaleItem, Medicine, MedicineBatch, Customer, Doctor
        import uuid
        
        try:
            data = request.get_json()
            
            # Validate required data
            if not data.get('customer_name') or not data.get('customer_nik'):
                return jsonify({
                    'success': False,
                    'message': 'Nama dan NIK pelanggan wajib diisi'
                }), 400
            
            # Generate invoice number
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Save or update customer data
            customer = Customer.query.filter_by(nik=data.get('customer_nik')).first()
            if customer:
                # Update existing customer
                customer.name = data.get('customer_name')
                customer.phone = data.get('customer_phone')
                customer.whatsapp = data.get('customer_whatsapp')
                customer.updated_at = datetime.utcnow()
            else:
                # Create new customer
                customer = Customer(
                    name=data.get('customer_name'),
                    nik=data.get('customer_nik'),
                    phone=data.get('customer_phone'),
                    whatsapp=data.get('customer_whatsapp')
                )
                db.session.add(customer)
            
            # Save doctor data if prescription
            if data.get('is_prescription') and data.get('doctor_name'):
                doctor = Doctor.query.filter_by(name=data.get('doctor_name')).first()
                if not doctor:
                    # Create new doctor record if not exists
                    doctor = Doctor(
                        name=data.get('doctor_name'),
                        str_number=data.get('doctor_name', 'TEMP-' + str(uuid.uuid4())[:8]),  # Temporary STR if not provided
                        phone=data.get('doctor_phone'),
                        whatsapp=data.get('doctor_whatsapp')
                    )
                    db.session.add(doctor)
            
            # Create sale record
            sale = Sale(
                invoice_number=invoice_number,
                customer_name=data.get('customer_name'),
                customer_nik=data.get('customer_nik'),
                customer_phone=data.get('customer_phone'),
                customer_whatsapp=data.get('customer_whatsapp'),
                doctor_name=data.get('doctor_name'),
                doctor_phone=data.get('doctor_phone'),
                doctor_whatsapp=data.get('doctor_whatsapp'),
                prescription_number=data.get('prescription_number'),
                is_prescription=data.get('is_prescription', False),
                payment_method=data.get('payment_method', 'cash'),
                cash_amount=data.get('cash_amount'),
                change_amount=data.get('change_amount'),
                notes=data.get('notes'),
                cashier_id=current_user.id,
                total_amount=data.get('total_amount', 0)
            )
            db.session.add(sale)
            db.session.flush()  # Get sale ID
            
            # Add sale items and update stock
            for item_data in data.get('items', []):
                medicine = Medicine.query.get(item_data['medicine_id'])
                if not medicine:
                    raise ValueError(f"Medicine with ID {item_data['medicine_id']} not found")
                
                # Get available batch with oldest expiry date (FIFO)
                available_batch = MedicineBatch.query.filter(
                    MedicineBatch.medicine_id == item_data['medicine_id'],
                    MedicineBatch.quantity >= item_data['quantity'],
                    MedicineBatch.expiry_date > datetime.now().date()
                ).order_by(MedicineBatch.expiry_date.asc()).first()
                
                if not available_batch:
                    raise ValueError(f"Stok tidak mencukupi untuk {medicine.name}")
                
                sale_item = SaleItem(
                    sale_id=sale.id,
                    medicine_id=item_data['medicine_id'],
                    batch_id=available_batch.id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                db.session.add(sale_item)
                
                # Update batch stock
                available_batch.quantity -= item_data['quantity']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'sale_id': sale.id,
                'invoice_number': sale.invoice_number,
                'message': 'Transaksi berhasil disimpan'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 400

    @app.route('/api/sale/<int:sale_id>/receipt/pdf')
    @login_required
    def generate_receipt_pdf(sale_id):
        """Generate PDF receipt untuk transaksi"""
        from models import Sale, PharmacyProfile
        try:
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            import tempfile
            import os
        except ImportError:
            # Fallback to simple text-based PDF if reportlab not available
            from flask import Response
            sale = Sale.query.get_or_404(sale_id)
            profile = PharmacyProfile.query.first()
            
            # Create simple text receipt
            receipt_text = f"""
APOTEK MANAGEMENT SYSTEM
{profile.name if profile else 'Apotek'}
{profile.address if profile else ''}
{profile.phone if profile else ''}

STRUK PEMBAYARAN
================
No. Invoice: {sale.invoice_number}
Tanggal: {sale.created_at.strftime('%d/%m/%Y %H:%M')}
Pelanggan: {sale.customer_name or 'Umum'}
Kasir: {sale.cashier.full_name}
Pembayaran: {sale.payment_method.replace('_', ' ').title()}

DETAIL PEMBELIAN:
================
"""
            
            total = 0
            for item in sale.sale_items:
                receipt_text += f"{item.medicine_ref.name:<30} {item.quantity:>3} x {item.unit_price:>8,.0f} = {item.total_price:>10,.0f}\n"
                total += float(item.total_price)
            
            receipt_text += f"\n{'='*60}\nTOTAL: Rp {total:,.0f}\n\nTerima kasih atas kunjungan Anda!"
            
            return Response(
                receipt_text,
                mimetype='text/plain',
                headers={'Content-Disposition': f'attachment; filename=receipt_{sale.invoice_number}.txt'}
            )
        
        sale = Sale.query.get_or_404(sale_id)
        profile = PharmacyProfile.query.first()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        if profile:
            title = Paragraph(f"<b>{profile.name}</b>", styles['Title'])
            address = Paragraph(profile.address, styles['Normal'])
            contact = Paragraph(f"Telp: {profile.phone} | Email: {profile.email}", styles['Normal'])
            license_info = Paragraph(f"SIPA: {profile.license_number}", styles['Normal'])
        else:
            title = Paragraph("<b>APOTEK MANAGEMENT</b>", styles['Title'])
            address = Paragraph("", styles['Normal'])
            contact = Paragraph("", styles['Normal'])
            license_info = Paragraph("", styles['Normal'])
        
        story.append(title)
        if profile:
            story.append(address)
            story.append(contact)
            story.append(license_info)
        story.append(Spacer(1, 20))
        
        # Receipt title
        receipt_title = Paragraph("<b>STRUK PEMBAYARAN</b>", styles['Heading2'])
        story.append(receipt_title)
        story.append(Spacer(1, 10))
        
        # Transaction info
        info_data = [
            ['No. Invoice:', sale.invoice_number],
            ['Tanggal:', sale.created_at.strftime('%d/%m/%Y %H:%M')],
            ['Pelanggan:', sale.customer_name or 'Umum'],
            ['Kasir:', sale.cashier.full_name],
            ['Pembayaran:', sale.payment_method.replace('_', ' ').title()]
        ]
        
        # Add cash payment details if applicable
        if sale.payment_method == 'cash' and sale.cash_amount:
            info_data.extend([
                ['Jumlah Bayar:', f'Rp {float(sale.cash_amount):,.0f}'],
                ['Kembalian:', f'Rp {float(sale.change_amount or 0):,.0f}']
            ])
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Items table
        item_data = [['Item', 'Qty', 'Harga', 'Total']]
        total_amount = 0
        
        for item in sale.sale_items:
            item_data.append([
                item.medicine_ref.name,
                str(item.quantity),
                f"Rp {item.unit_price:,.0f}",
                f"Rp {item.total_price:,.0f}"
            ])
            total_amount += float(item.total_price)
        
        # Add total row
        item_data.append(['', '', 'TOTAL:', f"Rp {total_amount:,.0f}"])
        
        items_table = Table(item_data, colWidths=[3*inch, 0.7*inch, 1.2*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer = Paragraph("<i>Terima kasih atas kunjungan Anda!<br/>Barang yang sudah dibeli tidak dapat dikembalikan</i>", styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'receipt_{sale.invoice_number}.pdf',
            mimetype='application/pdf'
        )