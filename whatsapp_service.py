
"""
WhatsApp notification service untuk sistem reminder apotek
"""
import requests
import json
from datetime import datetime
from models import Notification, CustomerWaitlist, Medicine, Customer
from database import db

class WhatsAppService:
    """Service untuk mengirim notifikasi WhatsApp"""
    
    def __init__(self, api_url=None, api_token=None):
        # Konfigurasi API WhatsApp (bisa menggunakan WhatsApp Business API, Twilio, atau layanan lainnya)
        self.api_url = api_url or "https://api.whatsapp.com/send"  # Default fallback
        self.api_token = api_token
        
    def format_phone_number(self, phone):
        """Format nomor telepon untuk WhatsApp (format internasional)"""
        if not phone:
            return None
            
        # Hapus karakter non-digit
        phone = ''.join(filter(str.isdigit, phone))
        
        # Tambahkan kode negara Indonesia jika belum ada
        if phone.startswith('0'):
            phone = '62' + phone[1:]
        elif not phone.startswith('62'):
            phone = '62' + phone
            
        return phone
    
    def send_restock_notification(self, customer_id, medicine_id, waitlist_id):
        """Kirim notifikasi restock ke pelanggan"""
        try:
            customer = Customer.query.get(customer_id)
            medicine = Medicine.query.get(medicine_id)
            waitlist = CustomerWaitlist.query.get(waitlist_id)
            
            if not customer or not medicine or not waitlist:
                return False, "Data tidak lengkap"
            
            # Format nomor WhatsApp
            whatsapp_number = self.format_phone_number(customer.whatsapp)
            if not whatsapp_number:
                return False, "Nomor WhatsApp tidak valid"
            
            # Buat pesan
            message = self._create_restock_message(customer, medicine, waitlist)
            
            # Kirim via WhatsApp (implementasi tergantung provider)
            success = self._send_whatsapp_message(whatsapp_number, message)
            
            if success:
                # Update status waitlist
                waitlist.is_notified = True
                waitlist.notified_at = datetime.utcnow()
                
                # Buat log notifikasi
                notification = Notification(
                    title=f"WhatsApp Terkirim: {medicine.name}",
                    message=f"Notifikasi restock berhasil dikirim ke {customer.name} ({customer.whatsapp})",
                    type='customer_notification',
                    customer_id=customer_id,
                    medicine_id=medicine_id,
                    priority='normal'
                )
                db.session.add(notification)
                db.session.commit()
                
                return True, "Notifikasi berhasil dikirim"
            else:
                return False, "Gagal mengirim WhatsApp"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _create_restock_message(self, customer, medicine, waitlist):
        """Buat template pesan WhatsApp"""
        message = f"""🏥 *APOTEK NOTIFICATION*

Halo {customer.name}! 👋

Kabar baik! Obat yang Anda tunggu sudah tersedia kembali:

💊 *{medicine.name}*
📦 Jumlah tersedia: {medicine.total_quantity} {medicine.unit}
📅 Tanggal permintaan: {waitlist.created_at.strftime('%d/%m/%Y')}

Silakan datang ke apotek kami untuk mengambil obat tersebut. 

Stok terbatas, jadi pastikan Anda datang segera! 

📍 Alamat: [Alamat Apotek]
📞 Telepon: [Nomor Telepon]
🕒 Jam buka: [Jam Operasional]

Terima kasih! 🙏"""
        
        return message
    
    def _send_whatsapp_message(self, phone_number, message):
        """Kirim pesan WhatsApp (implementasi sesuai provider)"""
        try:
            # Untuk demo, kita log pesan ke console
            # Dalam implementasi nyata, ganti dengan API WhatsApp yang digunakan
            
            print(f"=== WHATSAPP NOTIFICATION ===")
            print(f"To: {phone_number}")
            print(f"Message: {message}")
            print(f"Timestamp: {datetime.now()}")
            print("============================")
            
            # Simulasi berhasil kirim
            return True
            
            # Contoh implementasi dengan API provider:
            # payload = {
            #     'to': phone_number,
            #     'message': message,
            #     'token': self.api_token
            # }
            # response = requests.post(self.api_url, json=payload)
            # return response.status_code == 200
            
        except Exception as e:
            print(f"WhatsApp send error: {str(e)}")
            return False
    
    def send_bulk_notifications(self, medicine_id):
        """Kirim notifikasi ke semua pelanggan di waitlist untuk obat tertentu"""
        try:
            waitlist_items = CustomerWaitlist.query.filter_by(
                medicine_id=medicine_id,
                is_notified=False
            ).all()
            
            success_count = 0
            failed_count = 0
            
            for item in waitlist_items:
                success, message = self.send_restock_notification(
                    item.customer_id, 
                    item.medicine_id, 
                    item.id
                )
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    print(f"Failed to send to {item.customer.name}: {message}")
            
            return success_count, failed_count
            
        except Exception as e:
            print(f"Bulk notification error: {str(e)}")
            return 0, 0

# Instance global untuk digunakan di seluruh aplikasi
whatsapp_service = WhatsAppService()
