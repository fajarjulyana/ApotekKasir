# Overview

ApotekKasir is a comprehensive pharmacy management system designed for Indonesian pharmacies. The application provides complete management functionality for customers, doctors, prescriptions, inventory, and automated notification systems. It features role-based access control, multi-batch inventory tracking, prescription processing with image upload capabilities, and customer waitlist management for out-of-stock medications.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 with custom CSS styling for modern, responsive design
- **JavaScript Libraries**: DataTables for table management, Font Awesome for icons
- **Asset Management**: Static file serving for images, CSS, and JavaScript files
- **Form Handling**: HTML forms with client-side validation and AJAX for dynamic interactions

## Backend Architecture
- **Web Framework**: Flask with modular route organization across multiple files (routes.py, app_routes.py)
- **Authentication**: Flask-Login for session management with role-based access control (admin, pharmacist, restoker)
- **Database ORM**: SQLAlchemy with declarative base for model definitions
- **Background Tasks**: APScheduler for automated notification processing and system maintenance
- **File Upload**: Werkzeug utilities for secure file handling of prescription images
- **Session Management**: Flask sessions with secret key configuration

## Data Storage Solutions
- **Primary Database**: PostgreSQL configured through DATABASE_URL environment variable
- **Connection Pooling**: SQLAlchemy engine with pool recycling and pre-ping for reliability
- **File Storage**: Local filesystem storage for prescription images in `static/receive_dokter` directory
- **Static Assets**: Organized directory structure for product images, logos, and system assets

## Authentication and Authorization
- **User Roles**: Three-tier system with admin, pharmacist, and restoker roles
- **Permission System**: Method-based permissions (can_manage_inventory, can_serve_customers, can_manage_users)
- **Password Security**: Werkzeug password hashing with secure hash generation and verification
- **Session Protection**: Login required decorators and role-based access control throughout the application

## Core Domain Models
- **User Management**: Complete user profiles with role-based permissions
- **Customer Management**: Comprehensive customer data including NIK, emergency contacts, and medical history
- **Doctor Management**: Professional information including STR numbers, specializations, and practice details
- **Medicine Inventory**: Multi-batch tracking with expiry dates, barcode support, and low stock alerts
- **Prescription System**: Digital prescription processing with image upload and workflow management
- **Notification System**: Automated alerts for stock levels, expiry dates, and customer waitlists

## Business Logic Features
- **Inventory Tracking**: Real-time stock monitoring with automatic low stock and expiry alerts
- **Prescription Processing**: Complete workflow from upload to processing with customer-doctor matching
- **Customer Waitlist**: Automated queuing system for out-of-stock medications with priority notifications
- **Sales Management**: Point-of-sale functionality with real-time inventory updates
- **Reporting System**: Comprehensive reports for sales, inventory, and business analytics

# External Dependencies

## Database Systems
- **PostgreSQL**: Primary relational database for all application data storage
- **SQLAlchemy**: ORM layer for database abstraction and query management

## Frontend Libraries
- **Bootstrap 5**: UI component framework for responsive design
- **Font Awesome 6**: Icon library for consistent iconography
- **DataTables**: Advanced table functionality with sorting, filtering, and pagination
- **Google Fonts**: Inter font family for modern typography

## Python Libraries
- **Flask**: Core web framework for application structure
- **Flask-Login**: User authentication and session management
- **APScheduler**: Background task scheduling for automated processes
- **Werkzeug**: Utilities for file handling and security functions
- **Pillow**: Image processing for placeholder generation and file validation
- **openpyxl**: Excel file generation for reporting functionality
- **python-dotenv**: Environment variable management for configuration

## System Dependencies
- **File System**: Local storage for prescription images and static assets
- **Environment Variables**: Configuration management through .env files
- **Background Scheduler**: Automated task execution for system maintenance

## Potential Integrations
- **WhatsApp API**: Customer notification system for medication availability alerts
- **Barcode Scanning**: Integration ready for barcode-based inventory management
- **Payment Gateways**: Extensible architecture for payment processing integration
- **Reporting Tools**: Export capabilities for external analytics and compliance reporting