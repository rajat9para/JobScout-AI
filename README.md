<div align="center">

<img src="weblogo.png" alt="JobScout Logo" width="180">

# JobScout v2.2

### Your Personal Government Job Alert Bot

**AI-Powered** • **Dual Daily PDF Digest** • **Web Dashboard** • **100% Free**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_AI-Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Brevo](https://img.shields.io/badge/Brevo-Email-0B66C2?style=for-the-badge&logo=sendinblue&logoColor=white)](https://www.brevo.com)
[![Render](https://img.shields.io/badge/Render-Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

<br>

*Never miss a Sarkari Naukri again. JobScout monitors 4 government job portals 24/7,*  
*extracts structured data with AI, matches jobs to your profile, and delivers*  
*professional PDF digests twice daily — at 10 AM and 6 PM IST.*

<br>

---

</div>

## ✨ What Makes This Special?

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Extraction
Traditional scrapers break when websites change. JobScout uses **Google Gemini** to understand page context and extract structured job data — no brittle CSS selectors.

### 📄 Dual Daily PDF Digest  
Get **two professional PDFs** daily — at **10 AM** and **6 PM IST** — with all matching jobs including eligibility, salary, exam details, deadlines, and clickable apply links.

</td>
<td width="50%">

### 🎯 Smart Matching
Three-dimensional matching against your **qualification**, **interests** (11 sectors), and **experience level** — only relevant jobs reach you.

### 🌐 Interactive Web Dashboard
Beautiful dark-mode dashboard to manage your profile, pause/resume notifications, upload resume, view digest history, and trigger actions — all from your browser.

</td>
</tr>
</table>

---

## 🖥️ Web Dashboard

The interactive dashboard lets you control everything from your browser:

- **📊 Live Stats** — Pending jobs, total scraped, digests sent
- **👤 Profile Editor** — Update qualification, interests, experience with chip selectors
- **⏸️ Pause/Resume** — One-click notification toggle
- **📄 Resume Upload** — Drag & drop resume, AI-parsed automatically
- **📬 Digest History** — Track all sent digests with job counts
- **⚡ Quick Actions** — Manually trigger scraper or digest

---

## 🏗️ Architecture

```
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │  NCS.gov.in  │     │SarkariResult │     │ FreeJobAlert │   ... +1 more
   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
          │                    │                    │
          └────────────┬───────┘────────────────────┘
                       ▼
              ┌─────────────────┐
              │  Hourly Scraper │  ← Render Cron (every hour)
              │  + Gemini AI    │
              └────────┬────────┘
                       │ Extracted & matched jobs
                       ▼
              ┌─────────────────┐
              │  Daily Digest   │  ← Supabase daily_digest table
              │  Queue          │
              └───────┬─┬───────┘
                      │ │
            ┌─────────┘ └─────────┐
            ▼                     ▼
   ┌─────────────────┐  ┌─────────────────┐
   │ 🌅 Morning Cron │  │ 🌇 Evening Cron │
   │   10:00 AM IST  │  │   6:00 PM IST   │
   │  PDF + Email    │  │  PDF + Email     │
   └────────┬────────┘  └────────┬────────┘
            │                    │
            └────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │  📧 Your Inbox  │
            │  2 PDFs / day   │
            └─────────────────┘
```

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI + Uvicorn | Dashboard, APIs, health checks |
| **AI Engine** | Google Gemini Flash | Structured job extraction from HTML |
| **Database** | Supabase (PostgreSQL) | Jobs, profiles, digest queue, history |
| **PDF Generation** | ReportLab | Professional A4 digest documents |
| **Email** | Brevo (Sendinblue) | Transactional email with PDF attachment |
| **Hosting** | Render | Web service + 4 cron jobs (free tier) |
| **Keep-Alive** | UptimeRobot | Prevents Render free-tier spin-down |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Free accounts: [Supabase](https://supabase.com), [Brevo](https://www.brevo.com), [Google AI Studio](https://aistudio.google.com), [Render](https://render.com), [UptimeRobot](https://uptimerobot.com)

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/jobscout-v2.git
cd jobscout-v2
cp .env.example .env
# Fill in your credentials in .env
```

### 2. Setup Database

Run `sql/schema.sql` in Supabase SQL Editor — creates 6 tables:
`profiles`, `jobs`, `sent_alerts`, `exam_reminders`, `daily_digest`, `digest_history`

### 3. Deploy to Render

Push to GitHub → Connect in Render → Add env vars → Deploy!

Render auto-detects `render.yaml` and creates 5 services:
- Web Dashboard (always-on)
- Hourly Scraper (cron)
- Morning Digest — 10 AM IST (cron)
- Evening Digest — 6 PM IST (cron)
- Deadline Reminders — 8 AM IST (cron)

### 4. Open Dashboard

Visit `https://your-app.onrender.com` — the interactive dashboard opens.

> 📖 **Detailed step-by-step guide:** See [`toyourtask.txt`](toyourtask.txt)

---

## 📂 Project Structure

```
jobscout_v2/
├── app/
│   ├── __init__.py          # Package init, version
│   ├── config.py            # Environment variables (Pydantic)
│   ├── database.py          # Supabase operations with retry logic
│   ├── models.py            # Pydantic data models
│   ├── scraper.py           # 4 web scrapers
│   ├── extractor.py         # Gemini AI job extraction + resume parsing
│   ├── matcher.py           # 3-dimensional job-to-profile matching
│   ├── pdf_generator.py     # ReportLab PDF digest builder
│   ├── brevo_mailer.py      # Brevo transactional email client
│   ├── dashboard.py         # Interactive web dashboard HTML/CSS/JS
│   └── main.py              # FastAPI app (dashboard, APIs)
│
├── cron/
│   ├── scraper_job.py       # Hourly: scrape → extract → match → queue
│   ├── nightly_digest_job.py # Dual: morning/evening PDF digest
│   └── reminder_job.py      # Daily: deadline reminders via email
│
├── static/
│   └── weblogo.png          # Dashboard logo
│
├── sql/
│   └── schema.sql           # PostgreSQL schema (6 tables)
│
├── .env.example             # Environment variable template
├── .gitignore
├── render.yaml              # Render Blueprint (5 services)
├── requirements.txt         # Python dependencies
├── weblogo.png              # Project logo
├── features.md              # Feature guide
├── fullartitecture.md       # Technical architecture
├── toyourtask.txt           # Setup checklist
└── README.md                # ← You are here
```

---

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon public key |
| `SUPABASE_SERVICE_KEY` | ✅ | Supabase service role key |
| `BREVO_API_KEY` | ✅ | Brevo transactional API key |
| `SENDER_EMAIL` | ✅ | Verified sender email in Brevo |
| `SENDER_NAME` | ✅ | Email "From" display name |
| `USER_EMAIL` | ✅ | Your email (receives digests) |
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key |
| `GEMINI_MODEL` | ⬜ | Default: `gemini-1.5-flash` |

---

## 📊 Job Sources

| Portal | URL | Type |
|--------|-----|------|
| 🏛️ **NCS** | ncs.gov.in | Official Government Portal |
| 📊 **SarkariResult** | sarkariresult.com | High-Frequency Aggregator |
| 📋 **FreeJobAlert** | freejobalert.com | Cross-Reference Source |
| 📰 **Employment News** | employmentnews.gov.in | Official Weekly Gazette |

---

## 💰 Cost Breakdown

| Service | Free Tier Limits | Your Usage |
|---------|-----------------|------------|
| **Render** (Web + 4 Crons) | Free plan | Well within limits |
| **Supabase** (Database) | 500MB + 1GB storage | ~10MB/month |
| **Brevo** (Email) | 300/day, 9000/month | 2-4 emails/day |
| **Gemini** (AI) | 15 RPM, 1M tokens/day | ~50 requests/day |
| **UptimeRobot** | 50 monitors | 1 monitor |
| **Total** | — | **$0/month** ✨ |

---

## 🛡️ Resilience

- **Database:** 3 retries with exponential backoff
- **Gemini API:** Rate limit detection, automatic retry
- **Brevo:** 3 retries with exponential backoff
- **PDF:** Fallback error notification if generation fails
- **Scrapers:** Per-source isolation — one failure doesn't block others
- **Deduplication:** SHA256 hashing prevents duplicate entries

---

## 📖 Documentation

| File | Description |
|------|-------------|
| [`features.md`](features.md) | Complete feature list and usage guide |
| [`fullartitecture.md`](fullartitecture.md) | Deep technical architecture |
| [`toyourtask.txt`](toyourtask.txt) | Step-by-step setup checklist |
| [`sql/schema.sql`](sql/schema.sql) | Database schema |

---

## 🗺️ Roadmap

- [x] AI-powered job extraction (Gemini)
- [x] Multi-source scraping (4 portals)
- [x] Smart profile matching
- [x] PDF digest generation
- [x] Brevo email delivery
- [x] Web dashboard with profile management
- [x] Dual daily digests (10 AM + 6 PM)
- [x] Resume upload & AI parsing
- [x] Digest history tracking
- [ ] PDF notice parsing from portals
- [ ] Location-based filtering
- [ ] Multi-user support
- [ ] Mobile app

---

<div align="center">

**Built with ❤️ for Sarkari Naukri aspirants**

*Stop manually checking job portals. Let AI do it for you.*

⭐ Star this repo if it helped you find your dream government job!

</div>
