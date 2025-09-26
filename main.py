import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from database import db

load_dotenv()

# Create the app
app = Flask(__name__)

# Setup a secret key, required by sessions
app.secret_key = os.environ.get("SESSION_SECRET") or "secret-key-for-pharmacy-management"

# Configure the database with validation
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Please ensure PostgreSQL database is properly configured.")
    exit(1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

# Setup background scheduler for notifications
scheduler = BackgroundScheduler()
scheduler.start()

with app.app_context():
    # Import models here so tables are created
    import models

    # Create all tables
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register routes after app initialization
from app_routes import register_main_routes
from routes import register_routes

register_main_routes(app, db)
register_routes(app)

# Context processor untuk akses global
@app.context_processor
def inject_pharmacy_profile():
    from models import PharmacyProfile
    def get_pharmacy_profile():
        return PharmacyProfile.query.first()
    return dict(get_pharmacy_profile=get_pharmacy_profile, moment=datetime)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)