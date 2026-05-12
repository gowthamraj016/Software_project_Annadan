# AnnaDaan – Smart Food Donation Management System

**AnnaDaan** connects food donors (individuals, restaurants, caterers) with NGOs to reduce food waste using AI-powered prioritization, real-time pickup tracking, and explainable AI.

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.10+
- pip

### 1. Install Dependencies
```bash
pip install -r Requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Custom Admin Account
```bash
python manage.py shell -c "
from administration.models import Admin
Admin.objects.create(username='admin', email='admin@annadaan.com', password='Admin@123', full_name='Super Admin')
"
```

### 5. Start Development Server
```bash
python manage.py runserver
```

---

## 🔐 Default Credentials

| Role | Username/Email | Password |
|------|----------------|----------|
| Admin (custom panel) | `admin` | `Admin@123` |
| Admin (Django admin) | Create via `createsuperuser` | — |

---

## 📌 URL Reference

### Public / User URLs
| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/register/` | Register as Donor or NGO |
| `/login/` | Login |
| `/verify/?email=...` | OTP verification |
| `/dashboard/` | Role-based dashboard |
| `/profile/` | User profile with map |
| `/logout/` | Logout |

### Donation URLs (Sprint 2-4)
| URL | Role | Description |
|-----|------|-------------|
| `/donations/create/` | Donor | Create new donation |
| `/donations/my-donations/` | Donor | View my donations |
| `/donations/manage-requests/` | Donor | Manage NGO requests |
| `/donations/browse/` | NGO | Browse donations (AI sorted) |
| `/donations/my-requests/` | NGO | My requests status |
| `/donations/<id>/` | Both | Donation detail |
| `/donations/<id>/request/` | NGO | Request a donation |
| `/donations/pickup/<id>/track/` | Both | Track pickup live |

### API Endpoints
| URL | Description |
|-----|-------------|
| `POST /api/get-location/` | Geocode address → lat/lng |
| `POST /api/get-address/` | Reverse geocode lat/lng → address |
| `POST /donations/api/chatbot/` | Explain AI priority score |
| `GET /donations/api/notifications/` | Get user notifications |

### Admin Panel (`/panel/`)
| URL | Description |
|-----|-------------|
| `/panel/` | Admin login |
| `/panel/dashboard/` | Overview with stats |
| `/panel/users/` | Manage donors & NGOs |
| `/panel/donations/` | View all donations |
| `/panel/pickups/` | Manage pickups |
| `/panel/analytics/` | 📊 Charts & analytics |
| `/panel/logs/` | Activity logs |
| `/panel/export/donations/` | CSV export |
| `/panel/export/users/` | CSV export |

---

## 🧠 AI Priority Scoring (Sprint 3)

The priority score (0–100) is computed using:
```
score = urgency_score + quantity_score + distance_score

urgency_score  = (1 / (hours_to_expiry + 1)) × 50   # 50 pts max
quantity_score = (quantity / 100) × 30                # 30 pts max
distance_score = (1 - dist_km / 50) × 20             # 20 pts max
```
- **Red** (≥70): Collect immediately
- **Yellow** (40–69): High priority
- **Green** (<40): Can wait

---

## 🤖 AI Chatbot (Sprint 4)

The floating chatbot on the Browse Donations page allows NGOs to:
- Click **"Explain AI Score"** on any donation card
- Get a detailed breakdown of why a donation received its score
- Ask free-text questions (handled by the rule-based engine)

Chatbot logs are stored in the `ChatbotLog` model.

---

## ✅ Running Tests
```bash
python manage.py test donations --verbosity=2
```
**12 tests** covering:
- AI priority score range and ordering
- Donation request flow
- Pickup tracking JSON updates

---

## 🏗️ Project Structure

```
annadaan/
├── annadaan/           # Django project settings & URLs
├── users/              # Sprint 1: Auth, Donor, Receiver, OTP
├── administration/     # Sprint 1: Custom admin panel
│   └── templates/admin/
│       ├── dashboard.html
│       ├── users.html
│       ├── donations.html
│       ├── pickups.html
│       ├── analytics.html  # Sprint 4: Charts
│       └── logs.html
├── donations/          # Sprints 2-4
│   ├── models.py       # Donation, DonationRequest, Pickup, Notification, ChatbotLog
│   ├── views.py        # All donation & chatbot views
│   ├── urls.py
│   └── tests.py        # 12 unit tests
└── templates/
    ├── base.html        # Tailwind CSS + Leaflet + animations
    ├── dashboard.html   # Role-based dashboard
    └── donations/
        ├── create_donation.html    # Map-based form
        ├── list_donations.html     # AI-sorted + chatbot
        ├── donation_detail.html    # Detail + request button
        ├── create_request.html     # Request form
        ├── manage_requests.html    # Donor: accept/reject + schedule
        ├── my_donations.html       # Donor: all donations
        ├── my_requests.html        # NGO: all requests
        └── track_pickup.html       # Live map tracking
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Tailwind CSS, Leaflet.js, Chart.js |
| AI | Weighted formula (scikit-learn ready) |
| Maps | OpenStreetMap / Leaflet.js |
| Email | Django SMTP (Gmail) |
| Auth | Custom session-based auth |
