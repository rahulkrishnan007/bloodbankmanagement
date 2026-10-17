# LifeFlow - Blood Bank Management System

A Django web application that connects **blood donors**, **patients** and the **blood bank administrator**.
Redesigned with a modern, responsive interface and many new features.

> Original project by Sumit Kumar (MIT licence). All original features are kept.

## Features

### Public website
- Modern landing page with **live blood-stock availability** (Available / Low / Critical)
- Blood group **compatibility chart** (who can donate to whom)
- **Donation camps** listing, eligibility checklist and FAQ

### Admin
- Dashboard with **charts** (donations vs requests, stock per group, request status), low-stock and emergency alerts
- View / update / delete donors and patients with **search, blood-group filter and pagination**
- Approve / reject **donations** (adds to stock) and **blood requests** (deducts from stock, with a stock check)
- Requests carry **priority** (Normal / Urgent / Emergency), hospital and "needed by" date - emergencies are shown first
- Manual stock correction, request history with filters
- Publish / delete **donation camps**
- **CSV export** of donors, requests and donations
- Every approve / reject sends an **in-app notification** to the user

### Donor
- Signup, login, dashboard with **eligibility ring** (90-day gap), total donations / ml / lives impacted and **badge levels**
- Donate blood (age 18-65, blood-group check, one pending donation at a time), donation history
- Printable **donation certificate**
- Request blood, request history, cancel a pending request
- Profile editing and a **"show me in donor search"** switch

### Patient
- Signup, login, dashboard, request blood (form pre-filled), request history, cancel pending request, profile
- **Find available donors** by blood group / area

### Security & quality fixes
- Role based access: donors / patients can no longer open admin pages
- Approve / reject / delete now use **POST + CSRF** (they were plain links)
- Fixed: stock equal to the requested amount could not be approved; a donation could be approved twice (double stock)
- Passwords are validated; admin can leave the password blank when editing a user
- Complete, environment-driven `settings.py` (the committed one was missing `INSTALLED_APPS`, templates, etc.)
- 20 automated tests (`python manage.py test`)

## Run locally

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser                      # your admin account
python manage.py seed_demo                            # OPTIONAL: demo donors, patients, camps
python manage.py runserver
```

Open http://127.0.0.1:8000/ - the demo command creates:
`admin / admin12345`, `donor1 / demo12345`, `patient1 / demo12345`.

## Deploy on Render
`render.yaml` is included (it now also runs `migrate`). Set `SECRET_KEY` (auto-generated), `DEBUG=False` and, for PostgreSQL, `DATABASE_URL`.
On Render's free plan uploaded profile photos are not permanent (ephemeral disk).

## Settings you may want to change (`bloodbankmanagement/settings.py`)
`DONATION_GAP_DAYS`, `DONOR_MIN_AGE`, `DONOR_MAX_AGE`, `LOW_STOCK_ML`, `CRITICAL_STOCK_ML`.

## Replacing the artwork
The background / hero graphics are vector files in `static/image/` (`hero-bg.svg`, `hero-art.svg`, `auth-bg.svg`, `logo.svg`).
To use a real photo, change the `background` URL of `.hero` or `.auth-art` in `static/css/theme.css`.
