Temple Donation Management System (TDMS)
Product Requirements Document (PRD)
Product Name: Temple Donation Management System (TDMS)
Platform: Android App + Django Admin Backend + REST APIs
Backend: Python Django + Django REST Framework
Database: PostgreSQL
Authentication: OTP based Mobile Login
Receipt Generation: PDF (Multi-language)

1. Objective
Build a simple, secure and easy-to-use donation management application for temple committees to record donations, print receipts, manage volunteers, and monitor donation targets.

2. Users
Admin:
- Invite/suspend/reactivate members
- Configure donation categories, receipt templates, temple settings
- View/export reports, manage goals, audit logs

Member:
- Login via invited phone number
- Add donations
- Generate/reprint receipts
- Search/view own donations

3. Authentication
- OTP login
- Signup allowed only for invited phone numbers
- Admin can invite members from Django Admin or backend API

4. Donation Categories
- Configurable by admin
- Active/Inactive
- Goal amount
- Color and sort order
- Examples: Annadanam, Renovation, Daily Pooja, Hundi, Festival, Go Seva

5. Donation Entry
Fields:
- Donation date (editable)
- Donor name
- Phone (optional)
- Address (optional)
- Category
- Amount
- Payment mode (Cash/UPI)
- UTR mandatory for UPI
- Remarks
- Receipt language (English/Kannada/Marathi)
- Collected by (logged-in member)
- Auto receipt number

6. Receipt Generation
- PDF receipt
- Print, Share, Save
- Configurable header/footer/logo
- English, Kannada, Marathi
- Preview before printing

Receipt contains:
Temple logo, temple details, receipt no, donor, category, amount, payment mode, UTR, collector, signature, footer.

7. Reports
Filters:
- Date range
- Category
- Member
- Payment mode

Metrics:
- Total collection
- Cash vs UPI
- Donation count
- Member-wise collection
- Category-wise collection
- Goal progress

Exports:
PDF, Excel, CSV

8. Category Goals
- Configurable target amount
- Progress shown as collected/target
- Continue accepting donations even after 100%

9. Member Management
Statuses:
Pending, Active, Suspended, Inactive
Suspend/reactivate with mandatory reason.

10. Django Admin
Manage:
- Members
- Invitations
- Categories
- Goals
- Receipt templates
- Temple settings
- Audit logs
- Reports

11. APIs
Authentication:
/login
/verify-otp

Members:
/invite
/members

Categories:
/categories

Donations:
/donation

Receipts:
/receipt/{id}
/receipt/pdf/{id}

Reports:
/reports/category
/reports/member
/reports/date

12. Core Database Tables
Users
Invitations
DonationCategories
Donations
ReceiptTemplates
AuditLogs
TempleSettings

13. Android Screens
Splash
Login
OTP
Dashboard
Add Donation
Receipt Preview
Reports
Search
Members
Settings

14. Non-functional Requirements
- JWT secured APIs
- PostgreSQL
- Docker deployment
- Daily backups
- Audit trail
- <500 ms API response (typical)
- 99.9% availability target

15. Future Enhancements
- Multi-temple support
- Bluetooth thermal printing
- WhatsApp receipts
- SMS
- Online payments
- Offline sync
- QR code receipts
- Donor history
- Expense management
- Accounting integration

Recommended Stack:
Android: Kotlin + Jetpack Compose
Backend: Django + DRF
DB: PostgreSQL
PDF: ReportLab/WeasyPrint
Storage: S3/Azure Blob
Deployment: Docker + Nginx + Gunicorn
