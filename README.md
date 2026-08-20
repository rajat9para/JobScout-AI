<p align="center">
  <img src="https://img.shields.io/badge/JobScout-AI-1B2A4A?style=for-the-badge&logo=robot&logoColor=60A5FA" alt="JobScout-AI" height="40">
</p>

<h1 align="center">JobScout-AI</h1>

<p align="center">
  <strong>AI-Powered Government Job Intelligence Platform</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Gemini-3.6_Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Brevo-Email_API-0B66C2?style=flat-square&logo=sendinblue&logoColor=white" alt="Brevo">
  <img src="https://img.shields.io/badge/Deploy-Vercel_%7C_Render-000000?style=flat-square&logo=vercel&logoColor=white" alt="Deploy">
</p>

<p align="center">
  <em>Automatically scrapes, extracts, matches, and delivers government job notifications<br>tailored to your profile — twice daily via beautifully formatted PDF reports.</em>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Extraction** | Uses Google Gemini 3.6 Flash to intelligently extract structured job data from raw HTML |
| 🔍 **Smart Matching** | Matches jobs to your qualification, interests, and experience with relaxed 2/3 scoring |
| 📧 **Automated Reports** | Professional PDF reports delivered to your inbox at 10 AM & 6 PM IST daily |
| 📅 **15-Day Window** | Always see the last 15 days of jobs, grouped by date with the most recent first |
| 🗑️ **Auto-Cleanup** | Automatically deletes data older than 30 days to prevent storage overflow |
| 🔔 **Deadline Alerts** | Smart reminders at 3 days, 1 day, and last day before application deadlines |
| 📊 **Live Dashboard** | Real-time monitoring of scraper status, job counts, and system health |
| 🌐 **4 Government Sources** | SarkariResult, FreeJobAlert, SarkariExam, RojgarResult |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        JobScout-AI                              │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ Scraper  │Extractor │ Matcher  │   PDF    │    Email Service    │
│ Engine   │ (Gemini) │ Engine   │Generator │     (Brevo API)     │
├──────────┴──────────┴──────────┴──────────┴─────────────────────┤
│                    FastAPI + APScheduler                        │
├─────────────────────────────────────────────────────────────────┤
│                   Supabase (PostgreSQL)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Pipeline

```
  Scrape HTML  →  Gemini Extraction  →  Deduplication  →  Profile Matching  →  Queue
       │                │                     │                  │               │
  4 Gov Portals    Structured JSON       SHA-256 Hash      2/3 Scoring      daily_digest
                                                                                │
                                                                    ┌───────────┘
                                                                    ▼
                                                          PDF Generation
                                                                    │
                                                                    ▼
                                                           Email Delivery
                                                        (Brevo Transactional)
```

---

## 📁 Project Structure

```
jobscout_v2/
├── api/
│   └── index.py              # Vercel serverless entry point
├── app/
│   ├── main.py               # FastAPI application & API routes
│   ├── config.py              # Environment configuration (Pydantic Settings)
│   ├── database.py            # Supabase client — CRUD, 15-day window, cleanup
│   ├── scraper.py             # Web scrapers for 4 government portals
│   ├── extractor.py           # Gemini AI job extraction with robust JSON parsing
│   ├── matcher.py             # Profile-based job matching (relaxed 2/3 scoring)
│   ├── pdf_generator.py       # Professional PDF report generator (ReportLab)
│   ├── brevo_mailer.py        # Brevo transactional email client
│   ├── scheduler.py           # APScheduler — 6 background jobs
│   ├── dashboard.py           # Dashboard HTML generation
│   └── models.py              # Pydantic data models
├── cron/
│   ├── scraper_job.py         # Hourly scraper pipeline
│   ├── nightly_digest_job.py  # PDF digest with 3-tier fallback
│   └── reminder_job.py        # Deadline reminder emails
├── sql/
│   ├── schema.sql             # Database schema
│   └── migrate_v2.2_fix.sql   # Migration script
├── static/                    # Dashboard assets
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── render.yaml                # Render deployment blueprint
├── vercel.json                # Vercel deployment config
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- [Supabase](https://supabase.com) account (free tier)
- [Google AI Studio](https://aistudio.google.com) API key (free tier)
- [Brevo](https://brevo.com) account (free tier — 300 emails/day)

### 1. Clone & Install

```bash
git clone https://github.com/rajat9para/JobScout-AI.git
cd JobScout-AI

python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase (Dashboard → Project Settings → API)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Google Gemini (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.6-flash

# Brevo (https://app.brevo.com → Settings → SMTP & API → API Keys)
BREVO_API_KEY=xkeysib-your-key
SENDER_EMAIL=your-verified-sender@gmail.com
SENDER_NAME=JobScout-AI
USER_EMAIL=your@email.com
```

### 3. Setup Database

Run the SQL schema in your Supabase SQL Editor:

```sql
-- Copy and paste contents of sql/schema.sql
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000` for the dashboard.

---

## 🚀 Deployment

### Vercel (Dashboard + API)

1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Add all environment variables from `.env.example`
3. Deploy — Vercel auto-deploys on every push

> **Note:** Vercel is serverless — scheduled jobs (scraper, digest, cleanup) run on Render.

### Render (Background Jobs)

1. Connect your GitHub repo to [Render](https://render.com)
2. Use the included `render.yaml` blueprint
3. Add environment variables in the Render dashboard
4. Deploy — the web service runs all cron jobs via APScheduler

---

## ⏰ Scheduled Jobs

All jobs run inside the web service via APScheduler — no separate cron services needed.

| Job | Schedule | Description |
|-----|----------|-------------|
| 🔍 **Scraper** | Every hour at :05 | Scrapes 4 portals, extracts with Gemini, matches & queues |
| 🌅 **Morning Report** | 10:00 AM IST | PDF digest email with last 15 days of jobs |
| 🌇 **Evening Report** | 6:00 PM IST | PDF digest email with last 15 days of jobs |
| 🔔 **Reminders** | 8:00 AM IST | Deadline alerts (3 days, 1 day, last day) |
| 🗑️ **DB Cleanup** | 3:00 AM IST | Deletes data older than 30 days |
| 💓 **Keep-Alive** | Every 8 hours | Prevents Supabase free-tier database sleep |

---

## 📧 Email Reports

### Daily PDF Report
- **Professional "JobScout-AI" branding** with navy blue theme
- Jobs **grouped by date** — most recent first
- Each job shows: title, organization, salary, qualification, vacancies, exam, deadline, apply link
- Deadline urgency indicators (🔴 Expired, 🟡 3 days left, 🔵 7 days left)
- Summary stats bar: total jobs, sources, open deadlines

### Deadline Reminders
- Sent at 3 days, 1 day, and last day before deadlines
- Direct apply links with urgency-colored templates

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard |
| `GET` | `/health` | Health check |
| `GET` | `/api/status` | System status & stats |
| `GET` | `/api/trigger-scrape` | Manual scrape trigger |
| `GET` | `/api/trigger-digest` | Manual report email trigger |
| `GET` | `/api/trigger-test-email` | Send test email |
| `POST` | `/api/profile` | Save/update user profile |
| `GET` | `/api/profile` | Get current profile |
| `GET` | `/api/jobs` | List recent jobs |

---

## 🧠 How Matching Works

JobScout-AI uses a **relaxed 2-of-3 scoring** system:

| Check | What It Does |
|-------|-------------|
| 📚 **Qualification** | Matches your degree (B.Tech, MBA, etc.) against job eligibility |
| 💼 **Interests** | Keyword matching across 11 categories (banking, SSC, railway, etc.) |
| 📊 **Experience** | Compares your experience level with job requirements |

A job is included if:
- ✅ **Interests match** (primary filter), OR
- ✅ **At least 2 out of 3** checks pass

This ensures relevant jobs aren't filtered out when AI extraction is imperfect.

---

## 🛡️ Data Safety

| Feature | Implementation |
|---------|---------------|
| **Auto-Cleanup** | Jobs older than 30 days are automatically deleted daily at 3 AM IST |
| **Deduplication** | SHA-256 hash prevents duplicate jobs from being stored |
| **Keep-Alive** | Supabase free-tier databases are pinged every 8 hours |
| **Retry Logic** | All external calls (Gemini, Brevo, scrapers) have exponential backoff |

---

## 📊 Tech Stack

| Component | Technology | Tier |
|-----------|-----------|------|
| **Backend** | FastAPI + Uvicorn | — |
| **AI** | Google Gemini 3.6 Flash | Free (15 RPM) |
| **Database** | Supabase (PostgreSQL) | Free (500 MB) |
| **Email** | Brevo Transactional API | Free (300/day) |
| **PDF** | ReportLab | — |
| **Scheduler** | APScheduler | — |
| **Scraping** | Requests + BeautifulSoup | — |
| **Hosting** | Vercel + Render | Free |

> **Total cost: $0/month** — fully operational on free tiers.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'feat: add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>Built with ❤️ by <a href="https://github.com/rajat9para">Rajat Singh</a></strong>
</p>

<p align="center">
  <sub>JobScout-AI — Never miss a government job opportunity again.</sub>
</p>
