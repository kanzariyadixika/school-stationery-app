# School Stationery Management System

A complete, production-ready PWA (Progressive Web App) for managing school stationery shops.

## Features
- **Admin Dashboard**: Sales stats, stock alerts, total due.
- **Student Management**: Wallet balance, transaction history, due tracking.
- **POS / Billing**: Quick billing, auto-stock deduction, invoice generation.
- **Stock Management**: Inventory tracking, low stock warnings.
- **App Like**: installable on mobile (Android/iOS) via PWA.
- **WhatsApp**: Send due reminders and bills.

## Tech Stack
- Python Flask
- MySQL / SQLite
- SQLAlchemy
- Bootstrap 5
- Service Worker (Offline Support)

## Setup Instructions

### 1. Local Development
1.  **Install Python** (3.8 or higher).
2.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the App**:
    ```bash
    python run.py
    ```
    *This will create a local SQLite database `school_shop.db` and a default admin user.*
4.  **Login**:
    - URL: `http://localhost:5000`
    - Username: `admin`
    - Password: `admin123`

### 2. Deployment (Render / Railway)
1.  Create a `Procfile` (Included).
2.  Set Environment Variables in your host dashboard:
    - `SECRET_KEY`: (Random string)
    - `DATABASE_URL`: `mysql+mysqlconnector://user:pass@host/dbname` (or use internal Postgres/MySQL URL provided by host)
3.  Push to GitHub and connect to Render/Railway.

## PWA Installation
- Open the site in Chrome on Android.
- Tap "Add to Home Screen".
- It will install as a standalone app.

## Project Structure
- `app/models.py`: Database Schema
- `app/routes/`: Backend Logic
- `app/templates/`: HTML Frontend
- `app/static/`: CSS/JS/PWA Files
