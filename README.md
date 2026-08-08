<div align="center">

# 📋 JobScout v2.1

### Your Personal Government Job Alert Bot

**AI-Powered** • **Nightly PDF Digest** • **100% Free**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_AI-Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Brevo](https://img.shields.io/badge/Brevo-Email-0B66C2?style=for-the-badge&logo=sendinblue&logoColor=white)](https://www.brevo.com)
[![Render](https://img.shields.io/badge/Render-Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

<br>

*Never miss a Sarkari Naukri again. JobScout monitors 4 government job portals 24/7,*  
*extracts structured data with AI, matches jobs to your profile, and delivers a*  
*professional PDF digest to your inbox every night — completely free.*

<br>

---

</div>

## ✨ What Makes This Special?

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Extraction
Traditional scrapers break when websites change. JobScout uses **Google Gemini** to understand page context and extract structured job data — no brittle CSS selectors.

### 📄 Nightly PDF Digest  
No more scattered notifications. Get **one professional PDF** every night at 10 PM IST with all matching jobs — complete with eligibility, salary, exam details, and deadlines.

</td>
<td width="50%">

### 🎯 Smart Matching
Three-dimensional matching against your **qualification** (B.Tech, BSc, Law...), **interests** (PSU, Banking, Railways...), and **experience level** — only relevant jobs reach you.

### 💸 Completely Free
Runs entirely on free tiers: Render hosting, Supabase database, Gemini AI, Brevo email. **$0/month** for personal use.

</td>
</tr>
</table>

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
                       │ Extracted jobs
                       ▼
              ┌─────────────────┐
              │  Profile Match  │  ← Qualification + Interests + Experience
              └────────┬────────┘
                       │ Matched jobs → daily_digest table
                       ▼
              ┌─────────────────┐
              │  Nightly Cron   │  ← Render Cron (10 PM IST)
              │  PDF Generator  │
              │  (ReportLab)    │
              └────────┬────────┘
                       │ Professional PDF
                       ▼
              ┌─────────────────┐
              │  Brevo Email    │  ← PDF attachment
              │  API            │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  📧 Your Inbox  │  ← One PDF, all jobs, every night
              └─────────────────┘
```

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI + Uvicorn | Profile setup, health checks, APIs |
| **AI Engine** | Google Gemini Flash | Structured job extraction from HTML |
| **Database** | Supabase (PostgreSQL) | Jobs, profiles, digest queue, alerts |
| **PDF Generation** | ReportLab | Professional A4 digest documents |
| **Email** | Brevo (Sendinblue) | Transactional email with PDF attachment |
| **Hosting** | Render | Web service + 3 cron jobs (free tier) |
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

```sql
-- Run sql/schema.sql in Supabase SQL Editor
-- Creates 5 tables: profiles, jobs, sent_alerts, exam_reminders, daily_digest
```

### 3. Deploy to Render

```yaml
# render.yaml is pre-configured with 4 services:
# 1. Web Service (FastAPI)
# 2. Hourly Scraper (Cron)
# 3. Nightly Digest (Cron - 10 PM IST)
# 4. Deadline Reminders (Cron - 8 AM IST)
```

Push to GitHub → Connect in Render → Add env vars → Deploy!

### 4. Setup Profile

Visit `https://your-app.onrender.com/setup` and fill in the form.

> 📖 **Detailed step-by-step guide:** See [`toyourtask.txt`](toyourtask.txt)

---

## 📂 Project Structure

```
jobscout_v2/
├── app/
│   ├── __init__.py          # Package init, version
│   ├── config.py            # Environment variable management (Pydantic)
│   ├── database.py          # Supabase operations with retry logic
│   ├── models.py            # Pydantic data models (Profile, Job, DigestEntry)
│   ├── scraper.py           # 4 web scrapers (NCS, Sarkari, FreeJob, Employment)
│   ├── extractor.py         # Gemini AI job extraction from raw HTML
│   ├── matcher.py           # 3-dimensional job-to-profile matching
│   ├── pdf_generator.py     # ReportLab PDF digest builder
│   ├── brevo_mailer.py      # Brevo transactional email client
│   └── main.py              # FastAPI app (setup form, health, APIs)
│
├── cron/
│   ├── __init__.py
│   ├── scraper_job.py       # Hourly: scrape → extract → match → queue
│   ├── nightly_digest_job.py # Nightly: queue → PDF → email
│   └── reminder_job.py      # Daily: deadline reminders via email
│
├── sql/
│   └── schema.sql           # PostgreSQL schema (5 tables + indexes)
│
├── .env.example             # Environment variable template
├── .gitignore
├── render.yaml              # Render Blueprint (4 services)
├── requirements.txt         # Python dependencies
├── features.md              # Complete feature guide
├── fullartitecture.md       # Deep technical architecture
├── toyourtask.txt           # Step-by-step setup checklist
├── LICENSE                  # MIT License
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
| `APP_ENV` | ⬜ | Default: `production` |
| `LOG_LEVEL` | ⬜ | Default: `INFO` |

---

## 📊 Job Sources

| Portal | URL | Type |
|--------|-----|------|
| 🏛️ **NCS** | ncs.gov.in | Official Government Portal |
| 📊 **SarkariResult** | sarkariresult.com | High-Frequency Aggregator |
| 📋 **FreeJobAlert** | freejobalert.com | Cross-Reference Source |
| 📰 **Employment News** | employmentnews.gov.in | Official Weekly Gazette |

> Want to add more sources? Create a new class in `app/scraper.py` extending `BaseScraper` and add it to `get_all_scrapers()`. That's it!

---

## 💰 Cost Breakdown

| Service | Free Tier Limits | Your Usage |
|---------|-----------------|------------|
| **Render** (Web + 3 Crons) | Free plan | Well within limits |
| **Supabase** (Database) | 500MB + 1GB storage | ~10MB/month |
| **Brevo** (Email) | 300/day, 9000/month | 1-2 emails/day |
| **Gemini** (AI) | 15 RPM, 1M tokens/day | ~50 requests/day |
| **UptimeRobot** (Keep-alive) | 50 monitors | 1 monitor |
| **Total** | — | **$0/month** ✨ |

---

## 🛡️ Resilience & Error Handling

- **Database operations:** 3 retries with exponential backoff
- **Gemini API:** Rate limit detection, 3 retries, fail-safe empty returns
- **Brevo emails:** 3 retries with exponential backoff
- **PDF generation:** Fallback to error notification if generation fails
- **Scraper isolation:** Each source runs independently — one failure doesn't block others
- **Deduplication:** SHA256 hashing prevents duplicate job entries across sources

---

## 📖 Documentation

| File | Description |
|------|-------------|
| [`features.md`](features.md) | Complete feature list, usage guide, and FAQ |
| [`fullartitecture.md`](fullartitecture.md) | Deep technical architecture document |
| [`toyourtask.txt`](toyourtask.txt) | Step-by-step setup checklist |
| [`sql/schema.sql`](sql/schema.sql) | Database schema with comments |

---

## 🗺️ Roadmap

- [ ] PDF job notice parsing (extract text from PDFs posted on portals)
- [ ] Location-based filtering (state/city preferences)
- [ ] Salary range filtering
- [ ] Weekly digest option
- [ ] Multi-user support with authentication
- [ ] Web dashboard for profile management
- [ ] Job application tracking

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for Sarkari Naukri aspirants**

*Stop manually checking job portals. Let AI do it for you.*

⭐ Star this repo if it helped you find your dream government job!

</div>
