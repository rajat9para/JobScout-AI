<div align="center">

# JobScout-AI

### AI-Powered Government Job Intelligence Platform

Automatically scrapes, extracts, matches, and delivers personalized government job notifications — twice daily, via professionally formatted PDF reports.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-3.6_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Brevo](https://img.shields.io/badge/Brevo-Email_API-0B66C2?style=for-the-badge&logo=sendinblue&logoColor=white)](https://www.brevo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[Live Demo Video](https://drive.google.com/file/d/1SjReYiAX0zdldczLEcAKBIWnxih5HJmz/view?usp=drive_link) &nbsp;•&nbsp; [Source Code](https://github.com/rajat9para/JobScout-AI) &nbsp;•&nbsp; [Report an Issue](https://github.com/rajat9para/JobScout-AI/issues)

</div>

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Why JobScout-AI Exists](#why-jobscout-ai-exists)
3. [Core Features](#core-features)
4. [System Architecture](#system-architecture)
5. [Data Pipeline Walkthrough](#data-pipeline-walkthrough)
6. [Project Structure](#project-structure)
7. [Getting Started](#getting-started)
8. [Environment Configuration](#environment-configuration)
9. [Database Setup](#database-setup)
10. [Running Locally](#running-locally)
11. [Deployment Guide](#deployment-guide)
12. [Scheduled Jobs](#scheduled-jobs)
13. [Email Reports](#email-reports)
14. [Matching Algorithm Explained](#matching-algorithm-explained)
15. [API Reference](#api-reference)
16. [Data Safety and Reliability](#data-safety-and-reliability)
17. [Technology Stack](#technology-stack)
18. [Demonstration](#demonstration)
19. [Contributing](#contributing)
20. [License](#license)

---

## Project Overview

**JobScout-AI** is a fully automated pipeline that monitors India's leading government job portals, uses a large language model to convert unstructured HTML into clean structured data, matches each listing against a user's personal profile, and delivers the result as a polished PDF report — twice a day, with zero manual intervention.

The entire system is designed to run on free-tier infrastructure (Supabase, Google Gemini, Brevo, Vercel, and Render), making it a practical, production-grade reference project for anyone learning how to combine web scraping, LLM-based extraction, scheduled automation, and transactional email into a single working product.

---

## Why JobScout-AI Exists

Government job postings in India are scattered across dozens of portals, published in inconsistent formats, and easy to miss. Candidates often rely on manually refreshing multiple websites or subscribing to noisy, unfiltered alert services. JobScout-AI solves this by:

- Continuously monitoring multiple official aggregator sites
- Filtering out irrelevant postings using a personal qualification and interest profile
- Surfacing only what matters, twice a day, in a single readable document
- Tracking upcoming deadlines and sending timely reminders before they are missed

---

## Core Features

| Feature | Description |
|---|---|
| AI-Powered Extraction | Uses Google Gemini 3.6 Flash to convert raw HTML into structured job records |
| Smart Matching | Matches jobs to qualification, interests, and experience using a relaxed 2-of-3 scoring model |
| Automated Reports | Professional PDF reports delivered to the inbox at 10:00 AM and 6:00 PM IST daily |
| 15-Day Rolling Window | Displays the last 15 days of postings, grouped by date, most recent first |
| Automatic Cleanup | Purges records older than 30 days to keep storage within free-tier limits |
| Deadline Alerts | Reminders sent 3 days, 1 day, and on the final day before an application closes |
| Live Dashboard | Real-time view of scraper health, job counts, and system status |
| Multi-Source Coverage | Aggregates listings from four government job portals: SarkariResult, FreeJobAlert, SarkariExam, and RojgarResult |

---

## System Architecture

```
+-------------------------------------------------------------------+
|                            JobScout-AI                            |
+----------+----------+----------+----------+-----------------------+
| Scraper  | Extractor|  Matcher |   PDF    |     Email Service     |
| Engine   | (Gemini) |  Engine  | Generator|      (Brevo API)      |
+----------+----------+----------+----------+-----------------------+
|                    FastAPI  +  APScheduler                        |
+---------------------------------------------------------------------+
|                     Supabase (PostgreSQL)                          |
+---------------------------------------------------------------------+
```

The application is a single FastAPI service. APScheduler runs all background jobs inside the same process, removing the need for separate cron infrastructure. Supabase acts as the system of record for jobs, user profiles, and digest queues.

---

## Data Pipeline Walkthrough

```
 Scrape HTML  -->  Gemini Extraction  -->  Deduplication  -->  Profile Matching  -->  Digest Queue
      |                   |                     |                    |                    |
 4 Gov Portals      Structured JSON        SHA-256 Hash        2-of-3 Scoring      daily_digest table
                                                                                            |
                                                                              +-------------+
                                                                              v
                                                                     PDF Generation (ReportLab)
                                                                              |
                                                                              v
                                                                   Email Delivery (Brevo API)
```

**Step-by-step:**

1. **Scrape** — The scraper engine fetches raw HTML from four government job portals every hour.
2. **Extract** — Gemini 3.6 Flash parses the raw HTML and returns structured JSON: title, organization, qualification, salary, vacancies, exam name, and deadline.
3. **Deduplicate** — Each extracted job is hashed with SHA-256 to prevent duplicate entries from being stored across scrape cycles.
4. **Match** — The matcher engine scores each job against the stored user profile using the 2-of-3 relaxed scoring model.
5. **Queue** — Matched jobs are added to the daily digest queue.
6. **Generate** — Twice daily, ReportLab compiles all queued jobs from the last 15 days into a formatted PDF.
7. **Deliver** — Brevo's transactional email API sends the PDF report directly to the user's inbox.

---

## Project Structure

```
jobscout_v2/
├── api/
│   └── index.py              Vercel serverless entry point
├── app/
│   ├── main.py                FastAPI application and API routes
│   ├── config.py               Environment configuration (Pydantic Settings)
│   ├── database.py             Supabase client: CRUD, 15-day window, cleanup
│   ├── scraper.py              Web scrapers for four government portals
│   ├── extractor.py            Gemini AI job extraction with robust JSON parsing
│   ├── matcher.py               Profile-based job matching (relaxed 2-of-3 scoring)
│   ├── pdf_generator.py         Professional PDF report generator (ReportLab)
│   ├── brevo_mailer.py          Brevo transactional email client
│   ├── scheduler.py             APScheduler: six background jobs
│   ├── dashboard.py             Dashboard HTML generation
│   └── models.py                Pydantic data models
├── cron/
│   ├── scraper_job.py          Hourly scraper pipeline
│   ├── nightly_digest_job.py    PDF digest with three-tier fallback
│   └── reminder_job.py          Deadline reminder emails
├── sql/
│   ├── schema.sql               Database schema
│   └── migrate_v2.2_fix.sql     Migration script
├── static/                     Dashboard assets
├── .env.example                Environment template
├── requirements.txt             Python dependencies
├── render.yaml                  Render deployment blueprint
├── vercel.json                  Vercel deployment configuration
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11 or later
- A [Supabase](https://supabase.com) account (free tier)
- A [Google AI Studio](https://aistudio.google.com) API key (free tier)
- A [Brevo](https://brevo.com) account (free tier — 300 emails/day)

### Clone and Install

```bash
git clone https://github.com/rajat9para/JobScout-AI.git
cd JobScout-AI

python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## Environment Configuration

Copy the example file and populate it with your own credentials:

```bash
cp .env.example .env
```

```env
# Supabase (Dashboard -> Project Settings -> API)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Google Gemini (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.6-flash

# Brevo (https://app.brevo.com -> Settings -> SMTP & API -> API Keys)
BREVO_API_KEY=xkeysib-your-key
SENDER_EMAIL=your-verified-sender@gmail.com
SENDER_NAME=JobScout-AI
USER_EMAIL=your@email.com
```

---

## Database Setup

Run the contents of `sql/schema.sql` inside the Supabase SQL Editor to provision all required tables, indexes, and constraints.

```sql
-- Copy and paste the contents of sql/schema.sql into the Supabase SQL Editor
```

---

## Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` in a browser to view the live dashboard.

---

## Deployment Guide

JobScout-AI is designed to run across two free-tier platforms simultaneously: Vercel for the public dashboard and API, and Render for the always-on background worker that executes scheduled jobs.

### Vercel — Dashboard and API

1. Connect the GitHub repository to [Vercel](https://vercel.com).
2. Add every environment variable listed in `.env.example`.
3. Deploy. Vercel automatically redeploys on every push to the main branch.

> Vercel functions are serverless and cannot maintain a persistent scheduler. Scraper, digest, and cleanup jobs run separately on Render.

### Render — Background Jobs

1. Connect the same GitHub repository to [Render](https://render.com).
2. Use the included `render.yaml` blueprint to provision the service.
3. Add the required environment variables in the Render dashboard.
4. Deploy. The Render web service keeps APScheduler running continuously, executing all six background jobs.

---

## Scheduled Jobs

All jobs run inside the Render web service via APScheduler. No external cron provider is required.

| Job | Schedule | Description |
|---|---|---|
| Scraper | Every hour at :05 | Scrapes all four portals, extracts with Gemini, matches, and queues results |
| Morning Report | 10:00 AM IST | PDF digest email covering the last 15 days of jobs |
| Evening Report | 6:00 PM IST | PDF digest email covering the last 15 days of jobs |
| Reminders | 8:00 AM IST | Deadline alerts at 3 days, 1 day, and last day |
| Database Cleanup | 3:00 AM IST | Deletes records older than 30 days |
| Keep-Alive | Every 8 hours | Pings Supabase to prevent free-tier database sleep |

---

## Email Reports

### Daily PDF Report

- Branded "JobScout-AI" navy-blue theme
- Jobs grouped by posting date, most recent first
- Each entry includes title, organization, salary, qualification, vacancy count, exam name, deadline, and a direct apply link
- Deadline urgency indicators: expired, three days remaining, seven days remaining
- Summary bar showing total jobs, active sources, and open deadlines

### Deadline Reminders

- Triggered at 3 days, 1 day, and on the final day before a deadline
- Includes a direct apply link inside an urgency-coded email template

---

## Matching Algorithm Explained

JobScout-AI uses a **relaxed 2-of-3 scoring model** so that relevant postings are not discarded due to imperfect AI extraction.

| Check | What It Evaluates |
|---|---|
| Qualification | Matches the candidate's degree (B.Tech, MBA, etc.) against the job's stated eligibility |
| Interests | Keyword matching across 11 categories, including banking, SSC, and railways |
| Experience | Compares the candidate's experience level against the job's stated requirement |

A job is included in the digest if:

- The **interest check passes** (treated as the primary filter), **or**
- **At least two of the three** checks pass overall

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/health` | Health check |
| GET | `/api/status` | System status and statistics |
| GET | `/api/trigger-scrape` | Manually trigger a scrape cycle |
| GET | `/api/trigger-digest` | Manually trigger a report email |
| GET | `/api/trigger-test-email` | Send a test email |
| POST | `/api/profile` | Save or update the user profile |
| GET | `/api/profile` | Retrieve the current profile |
| GET | `/api/jobs` | List recent jobs |

---

## Data Safety and Reliability

| Feature | Implementation |
|---|---|
| Automatic Cleanup | Records older than 30 days are deleted daily at 3:00 AM IST |
| Deduplication | SHA-256 hashing prevents duplicate job entries |
| Keep-Alive Pings | Supabase free-tier databases are pinged every 8 hours to prevent sleep |
| Retry Logic | All external calls to Gemini, Brevo, and scraped sources use exponential backoff |

---

## Technology Stack

| Component | Technology | Tier |
|---|---|---|
| Backend | FastAPI + Uvicorn | — |
| AI / Extraction | Google Gemini 3.6 Flash | Free (15 requests/minute) |
| Database | Supabase (PostgreSQL) | Free (500 MB) |
| Email | Brevo Transactional API | Free (300 emails/day) |
| PDF Generation | ReportLab | — |
| Scheduling | APScheduler | — |
| Scraping | Requests + BeautifulSoup | — |
| Hosting | Vercel + Render | Free |

**Total operating cost: $0 per month**, fully functional on free-tier infrastructure across all services.

---

## Demonstration

A full walkthrough of the working system, including the live dashboard, scraper run, and generated PDF report, is available here:

**[Watch the Demo Video](https://drive.google.com/file/d/1SjReYiAX0zdldczLEcAKBIWnxih5HJmz/view?usp=drive_link)**

Full source code is available on GitHub: **[github.com/rajat9para/JobScout-AI](https://github.com/rajat9para/JobScout-AI)**

---

## Contributing

Contributions are welcome. To submit a change:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is open source and released under the [MIT License](LICENSE).

---

<div align="center">

**Built by [Rajat Singh](https://github.com/rajat9para)**

*JobScout-AI — Never miss a government job opportunity again.*

</div>
