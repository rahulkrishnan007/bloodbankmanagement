# 🩸 LifeFlow — Blood Bank Management System

**A modern, responsive Django web application designed to streamline blood donation, blood inventory management, and emergency blood requests.**

LifeFlow connects blood donors, patients, hospitals, and blood bank administrators through a centralized platform that helps manage donations, monitor blood stock, process requests, and improve access to donor information.

> **Project Note:** This project is based on the original Blood Bank Management System by Sumit Kumar, licensed under the MIT License. The application has been enhanced with a redesigned interface, additional functionality, security improvements, and automated tests. Please retain the original license and copyright notices.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [User Roles](#-user-roles)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Configuration](#-environment-configuration)
- [Database Setup](#-database-setup)
- [Demo Accounts](#-demo-accounts)
- [Automated Testing](#-automated-testing)
- [Deployment on Render](#-deployment-on-render)
- [Configuration Options](#-configuration-options)
- [Security and Best Practices](#-security-and-best-practices)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## 🌟 Overview

LifeFlow is a web-based blood bank management solution built with Django. It provides dedicated interfaces for donors, patients, and administrators, making it easier to coordinate blood donations and requests.

The system combines blood inventory tracking, donor management, request prioritization, donation camp publishing, and dashboard analytics in one application.

### Project Highlights

- Modern and responsive user interface
- Role-based authentication and authorization
- Blood inventory monitoring and request validation
- Donation and blood request approval workflows
- Emergency request prioritization
- Donor discovery by blood group and area
- Administrative dashboards and CSV exports
- CSRF-protected administrative actions
- Automated application tests

## 🚀 Key Features

### 🌐 Public Website

- Modern landing page with a responsive layout.
- Live blood-stock status indicators: **Available, Low, and Critical**.
- Blood group compatibility chart showing donation compatibility.
- Donation camp listings and information.
- Blood donation eligibility checklist.
- Frequently asked questions to help users understand the process.

### 🛡️ Administrator Dashboard

- Centralized dashboard for managing the blood bank.
- Charts for donations versus requests, blood stock by group, and request status.
- Low-stock indicators and emergency alerts.
- Search, filtering, and pagination for donors and patients.
- Create, view, update, and delete donor and patient records.
- Approve or reject blood donations and blood requests.
- Automatic stock updates following approved transactions.
- Stock availability validation before approving requests.
- Manual blood inventory corrections.
- Request history with filtering options.
- Donation camp publishing and management.
- CSV exports for donors, donations, and blood requests.
- In-app notifications following approval or rejection actions.
- Priority-based request management for Normal, Urgent, and Emergency cases.

### 🩸 Donor Portal

- Donor registration, login, and personalized dashboard.
- Blood donation eligibility checks based on age and donation interval.
- Configurable 90-day donation interval.
- Blood group validation during donation submission.
- Prevention of multiple simultaneous pending donation requests.
- Donation history and donation statistics.
- Total donations and donated volume tracking.
- Lives-impacted estimates and donor achievement badges.
- Printable donation certificates.
- Blood request submission and history.
- Cancellation of pending requests.
- Profile management.
- Privacy control to enable or disable visibility in donor search.

### 🏥 Patient Portal

- Patient registration, login, and personalized dashboard.
- Blood request form with pre-filled profile information.
- Blood group and request history tracking.
- Cancellation of pending blood requests.
- Profile management.
- Donor discovery by blood group and geographical area.
- Access to available donor information based on donor visibility settings.

### 🚨 Blood Inventory and Request Management

- Blood stock tracking by blood group.
- Visual stock status indicators.
- Validation of available inventory before request approval.
- Automatic deduction of stock after an approved request.
- Automatic addition of stock after an approved donation.
- Priority-based request processing.
- Hospital details and required-by dates for blood requests.
- Request history for administrative tracking.

### 🔐 Security and Reliability

- Role-based access restrictions for donors, patients, and administrators.
- Protection against unauthorized access to administrative pages.
- POST requests and CSRF protection for sensitive administrative actions.
- Validation to prevent duplicate donation approvals.
- Correct handling of requests when available stock equals the requested quantity.
- Password validation and secure password handling through Django authentication.
- Environment-driven application settings.
- Automated tests for important application workflows.

## 👥 User Roles

| Role | Responsibilities |
|---|---|
| Administrator | Manage users, blood inventory, donations, requests, camps, reports, and notifications. |
| Donor | Manage a profile, submit donations, view history, and request blood. |
| Patient | Request blood, view request history, manage a profile, and discover eligible visible donors. |
| Public Visitor | Explore blood availability, donation camps, compatibility information, and FAQs. |

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Django | Backend web framework |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Client-side interactions and interface enhancements |
| SQLite / PostgreSQL | Database, depending on configuration |
| Django Templates | Server-rendered user interface |
| Django Authentication | User authentication and password management |
| Django Testing Framework | Automated application testing |
| Render | Supported deployment platform |

**Note:** The production database depends on the configured environment. PostgreSQL should be configured for a persistent production deployment.

## 📂 Project Structure

The following is a representative structure. Actual filenames may differ depending on the repository version.

```text
bloodbankmanagement/
│
├── manage.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
│
├── bloodbankmanagement/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── static/
│   ├── css/
│   │   └── theme.css
│   └── image/
│       ├── hero-bg.svg
│       ├── hero-art.svg
│       ├── auth-bg.svg
│       └── logo.svg
│
├── templates/
│   └── ...
│
├── requirements.txt
└── venv/                 # Local environment; do not commit
```

> This tree illustrates the main project components. Confirm the actual application folders and filenames in your repository before using it as an exact directory reference.

## 💻 Getting Started

Follow these steps to run LifeFlow locally.

### Prerequisites

Install the following:

- Python 3.10 or a version supported by the project's dependencies.
- pip, Python's package installer.
- Git.
- A terminal such as Windows Command Prompt or PowerShell.

### 1. Clone the Repository

```bash
git clone https://github.com/rahulkrishnan007/bloodbankmanagement.git
cd bloodbankmanagement
```

### 2. Create a Virtual Environment

**Windows — Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows — PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your own administrator username, email address, and password.

### 6. Load Optional Demo Data

```bash
python manage.py seed_demo
```

This command is optional and should be run only if the project's `seed_demo` management command is available.

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

**http://127.0.0.1:8000/**

To access Django's default administration interface, visit **http://127.0.0.1:8000/admin/** if the project has the standard admin route configured.

## ⚙️ Environment Configuration

Configure environment variables according to the application's settings.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables or disables Django debug mode |
| `DATABASE_URL` | Optional database connection URL when supported by the project |
| `ALLOWED_HOSTS` | Hosts permitted to serve the application, if configured |

Example local environment configuration:

```text
SECRET_KEY=replace-with-a-secure-secret
DEBUG=True
```

Use a secure, unique secret key in production. Never commit `.env` files, production credentials, or private API keys to GitHub.

> Verify the variable names and database URL parsing against the actual `settings.py` implementation before deployment.

## 🗄️ Database Setup

LifeFlow can be configured to use SQLite for local development and PostgreSQL for a production environment.

For local development, run:

```bash
python manage.py migrate
```

Django applies the database migrations defined by the installed applications.

For PostgreSQL deployment:

1. Create a PostgreSQL database.
2. Set the appropriate database connection environment variable.
3. Verify that the project's settings support the configured connection URL.
4. Run migrations during deployment.
5. Test database connectivity before accepting production traffic.

## 🧪 Automated Testing

LifeFlow includes a reported suite of 20 automated tests.

Run the tests using:

```bash
python manage.py test
```

Use automated tests to validate critical workflows, including:

- User authentication and access control.
- Donation approval and inventory updates.
- Blood request approval and stock validation.
- Duplicate transaction prevention.
- Request and donation management.
- Role-based access restrictions.

The test count and coverage should be updated whenever the test suite changes.

## 👤 Demo Accounts

If the optional demo seeding command creates these accounts, they can be used for local testing:

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin12345` |
| Donor | `donor1` | `demo12345` |
| Patient | `patient1` | `demo12345` |

**Important:** These are development-only credentials. Do not use them on a public deployment. Create a secure administrator account and change or remove demo accounts before making the application publicly accessible.

## ☁️ Deployment on Render

The repository includes a `render.yaml` deployment configuration.

General deployment workflow:

1. Push the latest code to GitHub.
2. Sign in to Render and create a service connected to the repository.
3. Review the settings specified in `render.yaml`.
4. Configure a secure `SECRET_KEY`.
5. Set `DEBUG=False`.
6. Configure `ALLOWED_HOSTS` and HTTPS-related Django settings as appropriate.
7. Configure a persistent PostgreSQL database and set `DATABASE_URL` if supported.
8. Ensure database migrations run during deployment.
9. Deploy and verify the public website, authentication, dashboard, and inventory workflows.

### Production Considerations

- SQLite is generally unsuitable for a multi-instance production application.
- Uploaded profile photos may not persist on ephemeral deployment disks.
- Use persistent object storage for user uploads when required.
- Review logging, database backups, error handling, and access controls before production use.
- Never expose debug pages or demo credentials publicly.

## 🔧 Configuration Options

The following settings can be adjusted in `bloodbankmanagement/settings.py`, subject to the current project implementation.

| Setting | Purpose |
|---|---|
| `DONATION_GAP_DAYS` | Minimum interval between eligible donations |
| `DONOR_MIN_AGE` | Minimum donor age |
| `DONOR_MAX_AGE` | Maximum donor age |
| `LOW_STOCK_ML` | Threshold for low blood stock |
| `CRITICAL_STOCK_ML` | Threshold for critical blood stock |

Default donor eligibility settings described by the project are 18–65 years of age and a 90-day donation interval. These are application rules, not a substitute for medical screening or professional eligibility guidance.

## 🎨 Customizing the Interface

The application includes SVG artwork for its landing and authentication pages.

Relevant assets include:

- `static/image/hero-bg.svg`
- `static/image/hero-art.svg`
- `static/image/auth-bg.svg`
- `static/image/logo.svg`

The `.hero` and `.auth-art` styles in `static/css/theme.css` can be adjusted to change backgrounds, artwork, and visual presentation.

## 🔐 Security and Best Practices

Before using LifeFlow with real users or medical-related data:

- Use HTTPS in production.
- Store secrets in environment variables.
- Disable debug mode in production.
- Use strong, unique passwords and secure administrative accounts.
- Restrict access according to user roles.
- Validate all user input on the server.
- Protect state-changing requests with CSRF safeguards.
- Keep dependencies updated.
- Back up the production database.
- Review privacy requirements before publishing donor information.
- Test inventory changes for concurrent requests and duplicate submissions.
- Do not treat displayed blood stock or donor information as a guarantee of real-time clinical availability.

## 🛣️ Future Enhancements

Potential improvements for future releases include:

- Email and SMS notifications.
- Hospital and blood bank integration.
- Maps and location-based donor discovery.
- Advanced analytics and downloadable PDF reports.
- Audit logs for administrative actions.
- Improved accessibility and multilingual support.
- Automated deployment checks and continuous integration.
- Additional test coverage for concurrency and inventory consistency.
- Privacy controls and consent management for donor information.

These are proposed enhancements and are not claims about existing functionality.

## 🤝 Contributing

Contributions, suggestions, bug reports, and feature requests are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Run the relevant automated tests.
5. Commit your changes with a descriptive message.
6. Open a pull request explaining the changes.

For significant changes, consider opening an issue before starting implementation.

## 📄 License

This project is based on an original project by Sumit Kumar, reported to be licensed under the MIT License.

Please retain the original copyright and license notices and verify the repository's `LICENSE` file before redistributing modified versions.

## 🙏 Acknowledgements

- **Original Project:** Sumit Kumar
- **Framework:** Django
- **Community:** Python and open-source contributors

---

## 👨‍💻 Project Maintainer

**Rahul Krishnan**

GitHub: [@rahulkrishnan007](https://github.com/rahulkrishnan007)

Repository: [LifeFlow — Blood Bank Management System](https://github.com/rahulkrishnan007/bloodbankmanagement)

*Built to explore full-stack web development, database-driven applications, authentication, inventory workflows, and responsive user interface design.*

