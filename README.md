# AcxiomCRM — Python Flask Edition

A role-based CRM implementation based on the supplied AcxiomCRM assignment specification.

## Features
- Flask + SQLAlchemy
- Register / Login / Logout
- Password hashing
- Failed-login lockout
- Roles: Admin, Manager, Sales Executive
- Dashboard KPIs + Chart.js
- Customer CRUD + validation + duplicate checks
- Lead management + statuses
- Opportunity management + business rules
- Follow-up scheduling + date validation
- User management for Admin
- Audit logging
- REST APIs for Customers, Leads and Opportunities
- Reports
- CSRF protection on forms
- SQLite by default; MySQL supported through DATABASE_URL

## Run on Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Open: http://127.0.0.1:5000

## Demo admin
Email: admin@acxiomcrm.com
Password: Admin@123

Change the demo password before production use.

## MySQL
Set in `.env`:

DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/acxiomcrm

Create the database first:

CREATE DATABASE acxiomcrm;

## API examples
GET /api/customers
POST /api/customers
GET /api/customers/<id>
PUT /api/customers/<id>
DELETE /api/customers/<id>
GET /api/leads
POST /api/leads
GET /api/opportunities

All protected APIs require an authenticated session.

## Notes
This is a complete runnable project baseline for the assignment. Before production deployment, add HTTPS, production secret management, stronger password policy, rate limiting, migrations, pagination/export hardening, automated tests, and a production WSGI server.
