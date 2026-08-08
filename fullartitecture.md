# JobScout v2.1 — Full Architecture Document

> **Project:** Personal Sarkari Naukri Job Alert Bot  
> **Version:** 2.1.0  
> **Stack:** Python, FastAPI, Supabase, Brevo, ReportLab, Google Gemini, Render  
> **Scope:** Government job monitoring with AI-powered extraction and nightly PDF email digest

---

## 1. Executive Summary

JobScout is an autonomous job monitoring system that watches 4 major Indian government job portals 24/7, extracts structured job data using Google's Gemini AI, matches postings against a user-defined profile, and delivers a comprehensive **nightly PDF digest** via email using Brevo's free transactional email service. The entire system runs on free-tier cloud infrastructure with zero operational cost.

**Key Innovation:** Instead of brittle CSS selectors that break when websites redesign, JobScout uses Large Language Model (LLM) extraction. Raw HTML text is passed to Gemini, which reliably parses unstructured job notices into structured data regardless of layout changes.

**v2.1 Change:** Replaced Twilio WhatsApp alerts with a nightly PDF email digest. All matched jobs from the day are collected, formatted into a professional PDF, and emailed at 10 PM IST — giving you a single, comprehensive document instead of scattered messages.

---

## 2. Problem Statement

Government job postings in India are fragmented across multiple portals:
- **NCS.gov.in** (National Career Service)
- **SarkariResult.com** (high-frequency aggregator)
- **FreeJobAlert.com** (cross-reference source)
- **EmploymentNews.gov.in** (official gazette)

These portals use inconsistent formats: HTML tables, PDF notices, dynamic JavaScript, and unstructured text. Manually checking all sources daily is:
- **Time-consuming** (30+ minutes per day)
- **Error-prone** (easy to miss deadlines)
- **Inefficient** (most postings are irrelevant to the user's qualification)

**Solution:** An intelligent bot that filters noise and delivers only relevant, actionable alerts — consolidated into one PDF every night.

---

## 3. System Architecture

### 3.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Email Inbox)                             │
│                         ┌─────────────────────┐                             │
│                         │  Receives PDF digest │                             │
│                         │  at 10 PM IST daily  │                             │
│                         │  Deadline reminders  │                             │
│                         └──────────┬──────────┘                             │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BREVO TRANSACTIONAL EMAIL API                        │
│  • Sends nightly PDF digest (with attachment)                               │
│  • Sends deadline reminder emails (HTML)                                    │
│  • Free tier: 300 emails/day, 9000/month                                   │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              │                                             │
              ▼                                             ▼
┌─────────────────────────────┐              ┌─────────────────────────────┐
│   RENDER WEB SERVICE        │              │   RENDER CRON JOBS          │
│   (FastAPI + Uvicorn)       │              │                             │
│   Always-on, port $PORT     │              │  ┌─────────────────────┐    │
│                             │              │  │ Scraper Job         │    │
│  ┌─────────────────────┐    │              │  │ Runs: Every hour    │    │
│  │ /setup              │    │              │  │ Pipeline:           │    │
│  │ Profile setup form  │    │              │  │ 1. Scrape 4 sources │    │
│  └─────────────────────┘    │              │  │ 2. Gemini extract   │    │
│                             │              │  │ 3. Deduplicate      │    │
│  ┌─────────────────────┐    │              │  │ 4. Match vs profile │    │
│  │ /health             │◄───┼── UptimeRobot│  │ 5. Queue to digest  │    │
│  │ Keep-alive ping     │    │  (5 min)     │  └─────────────────────┘    │
│  └─────────────────────┘    │              │                             │
│                             │              │  ┌─────────────────────┐    │
│  ┌─────────────────────┐    │              │  │ Nightly Digest      │    │
│  │ /profile (debug)    │    │              │  │ Runs: 10 PM IST     │    │
│  │ /digest-status      │    │              │  │ 1. Fetch queue      │    │
│  │ /trigger-digest     │    │              │  │ 2. Generate PDF     │    │
│  └─────────────────────┘    │              │  │ 3. Email via Brevo  │    │
│                             │              │  └─────────────────────┘    │
└─────────────────────────────┘              │                             │
              │                              │  ┌─────────────────────┐    │
              │                              │  │ Reminder Job        │    │
              │ reads/writes                 │  │ Runs: Daily 8 AM    │    │
              │                              │  │ Checks deadlines    │    │
              │                              │  │ Sends email alerts  │    │
              ▼                              │  └─────────────────────┘    │
┌────────────────────────────┐               └─────────────────────────────┘
│  SUPABASE (PostgreSQL)     │                             │
│                            │                  reads/writes│
│  ┌────────────┐ ┌────────┐ │◄────────────────────────────┘
│  │ profiles   │ │ jobs   │ │
│  │ ────────── │ │ ────── │ │
│  │ email      │ │ source │ │  ┌──────────────┐
│  │ qualific.  │ │ title  │ │  │ daily_digest │
│  │ interests[]│ │ org    │ │  │ ──────────── │
│  │ experience │ │ salary │ │  │ job_id (FK)  │
│  │ status     │ │ exam   │ │  │ digest_date  │
│  └────────────┘ │ last_dt│ │  │ sent (bool)  │
│                 │ hash   │ │  └──────────────┘
│                 └────────┘ │
│  ┌────────────┐ ┌────────┐ │
│  │sent_alerts │ │exam_rem│ │
│  └────────────┘ └────────┘ │
└────────────────────────────┘
```

### 3.2 Component Breakdown

#### A. Brevo Transactional Email API
- **Digest:** Nightly email with PDF attachment at 10 PM IST
- **Reminders:** HTML emails for deadline alerts (3 days, 1 day, today)
- **Free tier:** 300 emails/day, 9000/month — ample for single-user
- **Retry:** 3 attempts with exponential backoff on API errors

#### B. Render Web Service (FastAPI)
- **Runtime:** Python 3.11 + Uvicorn ASGI server
- **Endpoints:**
  - `GET /setup` — Profile setup web form
  - `POST /setup` — Save profile to database
  - `GET /health` — Health check for UptimeRobot
  - `GET /profile` — Debug endpoint to view profile JSON
  - `GET /digest-status` — Check pending digest job count
  - `GET /trigger-digest` — Manual digest trigger for testing
- **State Management:** Stateless — all state persisted in Supabase
- **Keep-Alive:** UptimeRobot pings `/health` every 5 minutes

#### C. Render Cron Jobs
- **Job 1 — Scraper:** Runs hourly (`0 * * * *`)
  - Orchestrates the full scrape → extract → match pipeline
  - Matched jobs queued into `daily_digest` table
  - Isolated per-source error handling
- **Job 2 — Nightly Digest:** Runs at 10 PM IST (`30 16 * * *` UTC)
  - Fetches pending digest entries
  - Generates professional PDF via ReportLab
  - Emails PDF via Brevo
  - Marks entries as sent
- **Job 3 — Reminders:** Runs daily at 8 AM IST (`30 2 * * *` UTC)
  - Queries jobs with approaching deadlines
  - Sends reminder emails for matched jobs

#### D. Supabase (Backend)
- **PostgreSQL:** 5 tables with indexes, RLS policies, auto-update triggers
- **New Table:** `daily_digest` — queues matched jobs for nightly PDF
- **Connection:** Service role key for admin operations

---

## 4. Data Flow

### 4.1 Profile Setup Flow

```
User visits /setup
    │
    ▼
FastAPI serves HTML form
    │
    ▼
User fills: email, qualification, interests, experience
    │
    ▼
POST /setup → Upsert profile in Supabase
    │
    ▼
Success page with profile summary
```

### 4.2 Job Alert Pipeline (Hourly Cron)

```
Cron trigger (every hour)
    │
    ▼
For each scraper (4 sources):
    │
    ├── Fetch HTML page
    ├── Clean HTML → plain text
    ├── Chunk text (max 12K chars for Gemini)
    │
    ▼
For each text chunk:
    │
    ├── Send to Gemini API with extraction prompt
    ├── Parse JSON response → List[Job] objects
    │
    ▼
For each extracted job:
    │
    ├── Generate SHA256 hash (source + title + org + date)
    ├── Check if hash exists in jobs table
    │   ├── Yes → Skip (duplicate)
    │   └── No  → Save to database
    │
    ▼
    Match against user profile:
    │
    ├── Qualification match (B.Tech ↔ B.E., Any Graduate, etc.)
    ├── Interest match (PSU, Banking, Railways, etc.)
    └── Experience match (Fresher-friendly detection)
    │
    ▼
    If matched:
    │
    └── Insert into daily_digest table
        (will be included in tonight's PDF email)
```

### 4.3 Nightly PDF Digest Flow

```
Nightly at 10 PM IST
    │
    ▼
Fetch user profile from Supabase
    │
    ├── Not found or paused → Skip
    │
    ▼
Query daily_digest WHERE date = TODAY AND sent = FALSE
    │
    ▼
Join with jobs table for full details
    │
    ▼
Generate PDF with ReportLab:
    │
    ├── Header: title, date, job count
    ├── Summary: stats bar (jobs, sources, deadlines)
    ├── For each job: medium-length description card
    │   ├── Title, Org, Eligibility, Salary
    │   ├── Vacancies, Exam, Last Date (urgency)
    │   ├── Apply Link, Source, Degree Tags
    │   └── Divider between jobs
    └── Footer: page numbers, generation timestamp
    │
    ▼
Send email via Brevo:
    │
    ├── HTML body with summary
    ├── PDF attachment
    └── 3 retries with exponential backoff
    │
    ▼
Mark digest entries as sent in database
```

### 4.4 Exam Reminder Flow

```
Daily at 8 AM IST
    │
    ▼
Query jobs WHERE last_date = TODAY+3, TODAY+1, TODAY
    │
    ▼
For each job:
    ├── Check if reminder already sent (exam_reminders table)
    ├── Match against user profile
    │   ├── No match → Skip
    │   └── Match → Send reminder email via Brevo
    └── Record reminder sent
```

---

## 5. Database Schema

### 5.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  profiles   │       │    jobs     │       │ sent_alerts │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │◄──────│ id (PK)     │
│ email       │       │ source      │       │ job_id (FK) │
│ qualification│      │ title       │       │ sent_at     │
│ interests[] │       │ organization│       └─────────────┘
│ experience  │       │ eligibility │
│ status      │       │ degree_tags[]│      ┌──────────────┐
│ created_at  │       │ salary      │      │ daily_digest │
│ updated_at  │       │ vacancies   │      ├──────────────┤
└─────────────┘       │ exam_required│     │ id (PK)     │
                      │ last_date   │◄─────│ job_id (FK) │
                      │ apply_link  │      │ digest_date │
                      │ raw_hash    │      │ sent (bool) │
                      │ scraped_at  │      │ created_at  │
                      └─────────────┘      └──────────────┘
                             │
                      ┌──────┴──────┐
                      ▼             ▼
               ┌─────────────┐ ┌──────────────┐
               │ sent_alerts │ │exam_reminders│
               └─────────────┘ └──────────────┘
```

### 5.2 Table Details

**profiles**
- Stores user preferences set via web form at `/setup`
- `email` — recipient for nightly digest and reminders
- `status` controls whether the system is active or paused

**jobs**
- Stores all scraped job postings
- `raw_hash` (SHA256) enables deduplication across sources
- `exam_required` tracks exams like GATE, UPSC, SSC, Banking
- `degree_tags` array for fast qualification filtering

**daily_digest** (NEW in v2.1)
- Queues matched jobs throughout the day
- `digest_date` — the date this job was queued for
- `sent` — flipped to TRUE after the nightly email goes out
- Unique constraint on (job_id, digest_date) prevents duplicates

**sent_alerts**
- Prevents duplicate processing
- One-to-many relationship with jobs

**exam_reminders**
- Tracks which deadline reminders have been sent
- Types: 3_days, 1_day, today

---

## 6. AI Extraction Layer (Gemini)

### 6.1 Why Gemini Instead of Traditional Scraping?

| Approach | Fragility | Maintenance | Accuracy | Cost |
|----------|-----------|-------------|----------|------|
| CSS Selectors | High (breaks on redesign) | Weekly | Medium | Free |
| Regex Patterns | High (breaks on format change) | Weekly | Low | Free |
| **Gemini LLM** | **Low (understands context)** | **Monthly** | **High** | **Free tier** |

### 6.2 Extraction Prompt Engineering

The system uses a carefully crafted prompt that:
1. **Defines the schema** — title, organization, eligibility, salary, exam, last_date, apply_link
2. **Sets domain constraints** — government jobs ONLY, ignore private companies
3. **Standardizes dates** — converts "15 Aug 2026" → "2026-08-15"
4. **Handles equivalences** — B.Tech ↔ B.E., Any Graduate catch-all
5. **Enforces output format** — strict JSON array, no markdown

### 6.3 Rate Limiting & Resilience

- **Free tier limits:** 15 requests/minute, 1M tokens/day
- **Exponential backoff:** 2^attempt seconds on rate limit
- **Fail-safe:** Returns empty list on extraction failure (does not crash pipeline)
- **Chunking:** Large pages split into ~12K character chunks to stay within context limits

---

## 7. Matching Algorithm

### 7.1 Three-Dimensional Matching

The matcher evaluates jobs across three dimensions, ALL must pass:

1. **Qualification Match (40% weight)**
   - Exact degree match (B.Tech, BSc, Law, MBA)
   - Equivalence mapping (B.Tech ↔ B.E.)
   - Domain equivalence (BSc/BCA for IT roles)
   - "Any Graduate" catch-all

2. **Interest Match (40% weight)**
   - Keyword mapping for 11 sectors (PSU, Banking, Railways, Defence, etc.)
   - Searches title + organization + eligibility + exam fields
   - "All" interest matches everything

3. **Experience Match (20% weight)**
   - Fresher keyword detection (trainee, intern, graduate, entry-level)
   - Experience level mapping (Fresher/0-2 yrs/2+ yrs)
   - Senior role exclusion for freshers

### 7.2 Scoring

Relevance score = 0.0 to 1.0 used for internal ranking and future improvements.

---

## 8. PDF Generation (ReportLab)

### 8.1 Design Specifications

The nightly PDF digest uses professional formatting:

| Element | Style |
|---------|-------|
| Title | "JobScout — Daily Job Digest" in brand blue (#1a73e8), 22pt |
| Date | Gray subtitle, centered, with job count |
| Summary | Stats bar: total jobs, sources, open deadlines |
| Job Cards | Numbered, with org in blue, fields with emoji labels |
| Urgency | Last date shows "3 days left!", "Last Day!", etc. |
| Links | Clickable blue hyperlinks in PDF |
| Footer | Page numbers, generation timestamp |
| Empty State | "No matching jobs found today" message |

### 8.2 Edge Cases

- **Empty digest:** Generates a PDF with "no jobs found" message (still sent so user knows system is working)
- **Very long digest (50+ jobs):** Multi-page PDF with automatic page breaks and KeepTogether for job cards
- **Missing fields:** Gracefully handles null salary, exam, apply_link
- **PDF generation failure:** Sends error notification email as fallback

---

## 9. Security & Privacy

- **Environment variables:** All secrets stored in Render environment, never in code
- **Database:** Row Level Security (RLS) enabled with service-role policies
- **Resume storage:** Private Supabase Storage bucket, no public access
- **Email:** Brevo handles secure SMTP delivery; API key never exposed to client
- **No PII logging:** Email addresses are logged only for debugging

---

## 10. Scalability & Extensibility

### 10.1 Current Limits (Free Tier)
- **User count:** 1 (v2.1 single-user design)
- **Scrape frequency:** Hourly (adjustable in render.yaml)
- **Email volume:** 300/day free (only need 1-2/day)
- **Data storage:** 500MB PostgreSQL + 1GB file storage

### 10.2 Extension Points
- **Multi-user:** Add `user_id` foreign key to all tables, add auth layer
- **New sources:** Implement `BaseScraper` class, add to `get_all_scrapers()`
- **Better matching:** Replace keyword matching with embedding-based semantic search
- **Web dashboard:** Add React frontend using Supabase auth
- **Weekly digest:** Add a weekly summary option alongside daily

---

## 11. Technology Choices Justification

| Component | Choice | Alternative | Why This One |
|-----------|--------|-------------|--------------|
| Email | Brevo (Free) | SendGrid, Mailgun | 300/day free, simple SDK, reliable |
| PDF | ReportLab | WeasyPrint, FPDF | Industry standard, pure Python, flexible styling |
| Web Framework | FastAPI | Flask/Django | Async-native, automatic OpenAPI docs |
| Database | Supabase | Firebase, AWS RDS | Free tier includes auth + storage + Postgres |
| AI | Gemini Flash | Claude, GPT-4 | Free tier generous, fast, good at structured extraction |
| Hosting | Render | Heroku, Railway | Native cron jobs, free tier sufficient |
| Keep-Alive | UptimeRobot | Pingdom | Free 5-minute intervals, 50 monitors |

---

## 12. Monitoring & Observability

- **Render Logs:** Real-time stdout/stderr for all services
- **UptimeRobot:** External health check with email alerts on downtime
- **Brevo Dashboard:** Email delivery logs, bounce tracking, quota usage
- **Supabase Dashboard:** Query performance, storage usage, connection stats
- **Application Logs:** Structured logging with source tags for easy filtering

---

## 13. Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| Scraper fails on one source | Other 3 sources continue | Automatic on next cron run |
| Gemini rate limit | Jobs missed for 1 cycle | Exponential backoff retry |
| Brevo API error | Digest not sent | 3 retries with backoff; jobs stay in queue |
| PDF generation error | No PDF attachment | Error notification email sent as fallback |
| Database connection lost | Operations fail | 3 retries with backoff, fail-safe defaults |
| Render web service spins down | /setup unavailable | UptimeRobot prevents this |
| Email lands in spam | User doesn't see digest | Add sender to contacts; verify DKIM in Brevo |

---

*Document Version: 2.1.0*  
*Last Updated: 2026-08-08*  
*Author: Rajat9para*
