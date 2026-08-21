<p align="center">
  <img src="https://img.shields.io/badge/JobScout-AI-1B2A4A?style=for-the-badge&logo=robot&logoColor=60A5FA" alt="JobScout-AI" height="45">
</p>

<h1 align="center">🤖 JobScout-AI</h1>

<p align="center">
  <strong>🎯 AI-Powered Government Job Intelligence Platform</strong>
</p>

<p align="center">
  <em>🔍 Automatically scrapes, extracts, matches, and delivers government job notifications<br>
  tailored to your profile — twice daily via beautifully formatted 📄 PDF reports.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Gemini-3.6_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Brevo-Email_API-0B66C2?style=for-the-badge&logo=sendinblue&logoColor=white" alt="Brevo">
  <img src="https://img.shields.io/badge/Deploy-Vercel_%7C_Render-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Deploy">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/rajat9para/JobScout-AI?style=for-the-badge&color=FFD700&logo=github" alt="Stars">
  <img src="https://img.shields.io/github/forks/rajat9para/JobScout-AI?style=for-the-badge&color=blue&logo=github" alt="Forks">
  <img src="https://img.shields.io/github/last-commit/rajat9para/JobScout-AI?style=for-the-badge&color=orange&logo=github" alt="Last Commit">
  <img src="https://img.shields.io/github/license/rajat9para/JobScout-AI?style=for-the-badge&color=green" alt="License">
  <img src="https://img.shields.io/badge/Cost-%240%2Fmonth-success?style=for-the-badge" alt="Cost">
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1SjReYiAX0zdldczLEcAKBIWnxih5HJmz/view?usp=drive_link"><img src="https://img.shields.io/badge/▶️_Watch-Demo_Video-red?style=for-the-badge&logo=googledrive&logoColor=white" alt="Demo Video"></a>
  <a href="https://github.com/rajat9para/JobScout-AI"><img src="https://img.shields.io/badge/💻_View-Source_Code-181717?style=for-the-badge&logo=github&logoColor=white" alt="Source Code"></a>
</p>

---

## 📚 Table of Contents

| | | | |
|---|---|---|---|
| 🧭 [Project Overview](#-project-overview) | 💡 [Why It Exists](#-why-jobscout-ai-exists) | ✨ [Core Features](#-core-features) | 🏗️ [Architecture](#️-system-architecture) |
| 🔄 [Data Pipeline](#-data-pipeline-walkthrough) | 📁 [Project Structure](#-project-structure) | ⚡ [Quick Start](#-getting-started) | 🔐 [Environment Setup](#-environment-configuration) |
| 🗄️ [Database Setup](#️-database-setup) | 🖥️ [Run Locally](#️-running-locally) | 🚀 [Deployment](#-deployment-guide) | ⏰ [Scheduled Jobs](#-scheduled-jobs) |
| 📧 [Email Reports](#-email-reports) | 🧠 [Matching Logic](#-matching-algorithm-explained) | 🔧 [API Reference](#-api-reference) | 🛡️ [Data Safety](#️-data-safety-and-reliability) |
| 📊 [Tech Stack](#-technology-stack) | 🎬 [Demo](#-demonstration) | 🤝 [Contributing](#-contributing) | 📄 [License](#-license) |

---

## 🧭 Project Overview

**JobScout-AI** is a fully automated pipeline that monitors India's leading government job portals, uses a large language model to convert unstructured HTML into clean structured data, matches each listing against a user's personal profile, and delivers the result as a polished PDF report — twice a day, with zero manual intervention.

The entire system runs on **free-tier infrastructure** — Supabase, Google Gemini, Brevo, Vercel, and Render — making it a practical, production-grade reference project for anyone learning how to combine web scraping, LLM-based extraction, scheduled automation, and transactional email into a single working product.

<p align="center">
  <img src="https://img.shields.io/badge/Sources_Monitored-4-blue?style=flat-square" alt="Sources">
  <img src="https://img.shields.io/badge/Reports_Per_Day-2-blue?style=flat-square" alt="Reports">
  <img src="https://img.shields.io/badge/Job_Window-15_Days-blue?style=flat-square" alt="Window">
  <img src="https://img.shields.io/badge/Data_Retention-30_Days-blue?style=flat-square" alt="Retention">
  <img src="https://img.shields.io/badge/Emails_Free_Tier-300%2Fday-blue?style=flat-square" alt="Emails">
</p>

---

## 💡 Why JobScout-AI Exists

Government job postings in India are scattered across dozens of portals, published in inconsistent formats, and easy to miss. Candidates often rely on manually refreshing multiple websites or subscribing to noisy, unfiltered alert services. JobScout-AI solves this by:

- 🌐 Continuously monitoring multiple official aggregator sites
- 🎯 Filtering out irrelevant postings using a personal qualification and interest profile
- 📬 Surfacing only what matters, twice a day, in a single readable document
- ⏳ Tracking upcoming deadlines and sending timely reminders before they are missed

---

## ✨ Core Features

| # | Feature | Description |
|---|---------|-------------|
| 🤖 | **AI-Powered Extraction** | Uses Google Gemini 3.6 Flash to convert raw HTML into structured job records |
| 🧠 | **Smart Matching** | Matches jobs to qualification, interests, and experience using a relaxed 2-of-3 scoring model |
| 📧 | **Automated Reports** | Professional PDF reports delivered at **10:00 AM** and **6:00 PM IST** daily |
| 📅 | **15-Day Rolling Window** | Displays the last 15 days of postings, grouped by date, most recent first |
| 🗑️ | **Automatic Cleanup** | Purges records older than 30 days to keep storage within free-tier limits |
| 🔔 | **Deadline Alerts** | Reminders sent at 3 days, 1 day, and on the final day before an application closes |
| 📊 | **Live Dashboard** | Real-time view of scraper health, job counts, and system status |
| 🌐 | **Multi-Source Coverage** | Aggregates listings from **4 government portals**: SarkariResult, FreeJobAlert, SarkariExam, RojgarResult |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         🤖 JobScout-AI                          │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ 🕷️ Scraper│ 🧠 Extractor│ 🎯 Matcher│ 📄 PDF   │   📧 Email Service   │
│  Engine   │  (Gemini)   │  Engine   │Generator │     (Brevo API)     │
├──────────┴──────────┴──────────┴──────────┴─────────────────────┤
│                  ⚙️ FastAPI + APScheduler                        │
├─────────────────────────────────────────────────────────────────┤
│                  🗄️ Supabase (PostgreSQL)                        │
└─────────────────────────────────────────────────────────────────┘
```

The application is a single FastAPI service. APScheduler runs all background jobs inside the same process, removing the need for separate cron infrastructure. Supabase acts as the system of record for jobs, user profiles, and digest queues.

---

## 🔄 Data Pipeline Walkthrough

```
  🕷️ Scrape HTML → 🧠 Gemini Extraction → 🔁 Deduplication → 🎯 Profile Matching → 📥 Queue
        │                   │                     │                  │              │
   4 Gov Portals      Structured JSON        SHA-256 Hash       2/3 Scoring   daily_digest table
                                                                                       │
                                                                       ┌───────────────┘
                                                                       ▼
                                                             📄 PDF Generation
                                                                       │
                                                                       ▼
                                                              📧 Email Delivery
                                                           (Brevo Transactional)
```

**Step-by-step:**

1. 🕷️ **Scrape** — The scraper engine fetches raw HTML from four government job portals every hour.
2. 🧠 **Extract** — Gemini 3.6 Flash parses the raw HTML and returns structured JSON: title, organization, qualification, salary, vacancies, exam name, and deadline.
3. 🔁 **Deduplicate** — Each extracted job is hashed with SHA-256 to prevent duplicate entries from being stored across scrape cycles.
4. 🎯 **Match** — The matcher engine scores each job against the stored user profile using the 2-of-3 relaxed scoring model.
5. 📥 **Queue** — Matched jobs are added to the daily digest queue.
6. 📄 **Generate** — Twice daily, ReportLab compiles all queued jobs from the last 15 days into a formatted PDF.
7. 📧 **Deliver** — Brevo's transactional email API sends the PDF report directly to the user's inbox.

---

## 📁 Project Structure

```
jobscout_v2/
├── 📂 api/
│   └── index.py              # Vercel serverless entry point
├── 📂 app/
│   ├── main.py                # FastAPI application & API routes
│   ├── config.py               # Environment configuration (Pydantic Settings)
│   ├── database.py             # Supabase client — CRUD, 15-day window, cleanup
│   ├── scraper.py              # Web scrapers for 4 government portals
│   ├── extractor.py            # Gemini AI job extraction with robust JSON parsing
│   ├── matcher.py                # Profile-based job matching (relaxed 2/3 scoring)
│   ├── pdf_generator.py          # Professional PDF report generator (ReportLab)
│   ├── brevo_mailer.py           # Brevo transactional email client
│   ├── scheduler.py              # APScheduler — 6 background jobs
│   ├── dashboard.py              # Dashboard HTML generation
│   └── models.py                 # Pydantic data models
├── 📂 cron/
│   ├── scraper_job.py           # Hourly scraper pipeline
│   ├── nightly_digest_job.py     # PDF digest with 3-tier fallback
│   └── reminder_job.py           # Deadline reminder emails
├── 📂 sql/
│   ├── schema.sql                # Database schema
│   └── migrate_v2.2_fix.sql      # Migration script
├── 📂 static/                    # Dashboard assets
├── ⚙️ .env.example               # Environment template
├── 📦 requirements.txt           # Python dependencies
├── 🚀 render.yaml                # Render deployment blueprint
├── 🚀 vercel.json                # Vercel deployment config
└── 📄 README.md
```

---

## ⚡ Getting Started

### ✅ Prerequisites

- 🐍 Python 3.11+
- 🗄️ [Supabase](https://supabase.com) account (free tier)
- 🧠 [Google AI Studio](https://aistudio.google.com) API key (free tier)
- 📧 [Brevo](https://brevo.com) account (free tier — 300 emails/day)

### 1️⃣ Clone & Install

```bash
git clone https://github.com/rajat9para/JobScout-AI.git
cd JobScout-AI

python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# 🗄️ Supabase (Dashboard → Project Settings → API)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# 🧠 Google Gemini (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.6-flash

# 📧 Brevo (https://app.brevo.com → Settings → SMTP & API → API Keys)
BREVO_API_KEY=xkeysib-your-key
SENDER_EMAIL=your-verified-sender@gmail.com
SENDER_NAME=JobScout-AI
USER_EMAIL=your@email.com
```

---

## 🗄️ Database Setup

Run the SQL schema in your Supabase SQL Editor:

```sql
-- Copy and paste contents of sql/schema.sql
```

---

## 🖥️ Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000` for the 📊 live dashboard.

---

## 🚀 Deployment Guide

### ▲ Vercel (Dashboard + API)

1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Add all environment variables from `.env.example`
3. Deploy — Vercel auto-deploys on every push

> ⚠️ **Note:** Vercel is serverless — scheduled jobs (scraper, digest, cleanup) run on Render.

### ⬤ Render (Background Jobs)

1. Connect your GitHub repo to [Render](https://render.com)
2. Use the included `render.yaml` blueprint
3. Add environment variables in the Render dashboard
4. Deploy — the web service runs all cron jobs via APScheduler

---

## ⏰ Scheduled Jobs

All jobs run inside the web service via APScheduler — no separate cron services needed.

| ⏱️ | Job | Schedule | Description |
|---|-----|----------|-------------|
| 🔍 | **Scraper** | Every hour at :05 | Scrapes 4 portals, extracts with Gemini, matches & queues |
| 🌅 | **Morning Report** | 10:00 AM IST | PDF digest email with last 15 days of jobs |
| 🌇 | **Evening Report** | 6:00 PM IST | PDF digest email with last 15 days of jobs |
| 🔔 | **Reminders** | 8:00 AM IST | Deadline alerts (3 days, 1 day, last day) |
| 🗑️ | **DB Cleanup** | 3:00 AM IST | Deletes data older than 30 days |
| 💓 | **Keep-Alive** | Every 8 hours | Prevents Supabase free-tier database sleep |

---

## 📧 Email Reports

### 📄 Daily PDF Report
- 🎨 Professional "JobScout-AI" branding with navy blue theme
- 📅 Jobs **grouped by date** — most recent first
- 🧾 Each job shows: title, organization, salary, qualification, vacancies, exam, deadline, apply link
- 🚦 Deadline urgency indicators: 🔴 Expired · 🟡 3 days left · 🔵 7 days left
- 📊 Summary stats bar: total jobs, sources, open deadlines

### 🔔 Deadline Reminders
- ⏳ Sent at 3 days, 1 day, and last day before deadlines
- 🔗 Direct apply links with urgency-colored templates

---

## 🧠 Matching Algorithm Explained

JobScout-AI uses a **relaxed 2-of-3 scoring** system:

| ✅ | Check | What It Does |
|---|-------|---------------|
| 📚 | **Qualification** | Matches your degree (B.Tech, MBA, etc.) against job eligibility |
| 💼 | **Interests** | Keyword matching across 11 categories (banking, SSC, railway, etc.) |
| 📊 | **Experience** | Compares your experience level with job requirements |

A job is included if:
- ✅ **Interests match** (primary filter), **OR**
- ✅ **At least 2 out of 3** checks pass

This ensures relevant jobs aren't filtered out when AI extraction is imperfect.

---

## 🔧 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | 📊 Dashboard |
| `GET` | `/health` | 💓 Health check |
| `GET` | `/api/status` | 📈 System status & stats |
| `GET` | `/api/trigger-scrape` | 🕷️ Manual scrape trigger |
| `GET` | `/api/trigger-digest` | 📧 Manual report email trigger |
| `GET` | `/api/trigger-test-email` | ✉️ Send test email |
| `POST` | `/api/profile` | 💾 Save/update user profile |
| `GET` | `/api/profile` | 👤 Get current profile |
| `GET` | `/api/jobs` | 📋 List recent jobs |

---

## 🛡️ Data Safety and Reliability

| Feature | Implementation |
|---------|---------------|
| 🗑️ **Auto-Cleanup** | Jobs older than 30 days are automatically deleted daily at 3 AM IST |
| 🔁 **Deduplication** | SHA-256 hash prevents duplicate jobs from being stored |
| 💓 **Keep-Alive** | Supabase free-tier databases are pinged every 8 hours |
| 🔄 **Retry Logic** | All external calls (Gemini, Brevo, scrapers) have exponential backoff |

---

## 📊 Technology Stack

| Component | Technology | Tier |
|-----------|-----------|------|
| ⚙️ **Backend** | FastAPI + Uvicorn | — |
| 🧠 **AI** | Google Gemini 3.6 Flash | Free (15 RPM) |
| 🗄️ **Database** | Supabase (PostgreSQL) | Free (500 MB) |
| 📧 **Email** | Brevo Transactional API | Free (300/day) |
| 📄 **PDF** | ReportLab | — |
| ⏰ **Scheduler** | APScheduler | — |
| 🕷️ **Scraping** | Requests + BeautifulSoup | — |
| 🚀 **Hosting** | Vercel + Render | Free |

<p align="center">
  <img src="https://img.shields.io/badge/💰_Total_Cost-%240%2Fmonth-brightgreen?style=for-the-badge" alt="Total Cost">
</p>

> **Total cost: $0/month** — fully operational on free tiers.

---

## 🎬 Demonstration

<p align="center">
  <a href="https://drive.google.com/file/d/1SjReYiAX0zdldczLEcAKBIWnxih5HJmz/view?usp=drive_link">
    <img src="https://img.shields.io/badge/▶️_Watch_Full_Demo-Google_Drive-red?style=for-the-badge&logo=googledrive&logoColor=white" alt="Watch Demo" height="45">
  </a>
</p>

A complete walkthrough of the working system — including the live dashboard, a full scraper run, AI extraction in action, and a sample generated PDF report — is available in the demo video above.

<p align="center">
  <a href="https://github.com/rajat9para/JobScout-AI">
    <img src="https://img.shields.io/badge/💻_Explore_the-Full_Codebase-181717?style=for-the-badge&logo=github&logoColor=white" alt="View Code" height="45">
  </a>
</p>

---

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/your-feature`
3. 💾 Commit changes: `git commit -m 'feat: add your feature'`
4. 📤 Push to branch: `git push origin feature/your-feature`
5. 🔀 Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>❤️ Built with love by <a href="https://github.com/rajat9para">Rajat Singh</a></strong>
</p>

<p align="center">
  <sub>🚀 JobScout-AI — Never miss a government job opportunity again.</sub>
</p>
