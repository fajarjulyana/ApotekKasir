"""
Main application routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta

def register_main_routes(app, db):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            from models import User
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            
            flash('Username atau password salah!', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Berhasil logout!', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        from models import Medicine, Sale, get_expiring_medicines, get_low_stock_medicines
        
        # Get dashboard statistics
        total_medicines = Medicine.query.count()
        expiring_soon = len(get_expiring_medicines())
        low_stock = len(get_low_stock_medicines())
        
        # Get recent sales (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_sales = Sale.query.filter(Sale.created_at >= week_ago).count()
        
        return render_template('dashboard.html', 
                             total_medicines=total_medicines,
                             expiring_soon=expiring_soon,
                             low_stock=low_stock,
                             recent_sales=recent_sales)