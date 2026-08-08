# JobScout v2 — Full Architecture Document

> **Project:** Personal Sarkari Naukri Job Alert Bot  
> **Version:** 2.0.0  
> **Stack:** Python, FastAPI, Supabase, Twilio, Google Gemini, Render  
> **Scope:** Government job monitoring with AI-powered extraction and WhatsApp delivery

---

## 1. Executive Summary

JobScout is an autonomous WhatsApp bot that monitors 4 major Indian government job portals 24/7, extracts structured job data using Google's Gemini AI, matches postings against a user-defined profile, and delivers personalized alerts directly to WhatsApp. The entire system runs on free-tier cloud infrastructure with zero operational cost.

**Key Innovation:** Instead of brittle CSS selectors that break when websites redesign, JobScout uses Large Language Model (LLM) extraction. Raw HTML text is passed to Gemini, which reliably parses unstructured job notices into structured data regardless of layout changes.

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

**Solution:** An intelligent bot that filters noise and delivers only relevant, actionable alerts.

---

## 3. System Architecture

### 3.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (WhatsApp)                                │
│                         ┌─────────────────────┐                             │
│                         │  Sends "hello"      │                             │
│                         │  Sends commands     │                             │
│                         │  Receives alerts    │                             │
│                         └──────────┬──────────┘                             │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TWILIO WHATSAPP API                               │
│  • Receives inbound messages (webhook POST)                                 │
│  • Sends outbound alerts (programmatic API)                                 │
│  • Free sandbox for development → approved sender for production              │
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
│  │ /webhook            │◄───┼──────────────┤  │ Pipeline:           │    │
│  │ Handles onboarding  │    │              │  │ 1. Scrape 4 sources │    │
│  │ & user commands     │    │              │  │ 2. Gemini extract   │    │
│  └─────────────────────┘    │              │  │ 3. Deduplicate      │    │
│                             │              │  │ 4. Match vs profile │    │
│  ┌─────────────────────┐    │              │  │ 5. Send WhatsApp    │    │
│  │ /health             │◄───┼── UptimeRobot│  └─────────────────────┘    │
│  │ Keep-alive ping     │    │  (5 min)     │                             │
│  └─────────────────────┘    │              │  ┌─────────────────────┐    │
│                             │              │  │ Reminder Job        │    │
│  ┌─────────────────────┐    │              │  │ Runs: Daily 8 AM    │    │
│  │ /profile (debug)    │    │              │  │ Checks deadlines    │    │
│  └─────────────────────┘    │              │  │ Sends 3/1/0-day     │    │
│                             │              │  │ deadline reminders  │    │
└─────────────────────────────┘              │  └─────────────────────┘    │
              │                              └─────────────────────────────┘
              │                                             │
              │ reads/writes                                │ reads/writes
              │                                             │
              ▼                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE (PostgreSQL + Storage)                     │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ profiles     │  │ jobs         │  │ sent_alerts  │  │ exam_remind..│   │
│  │ ───────────  │  │ ───────────  │  │ ───────────  │  │ ───────────  │   │
│  │ id (UUID)    │  │ id (UUID)    │  │ id (UUID)    │  │ id (UUID)    │   │
│  │ whatsapp_no  │  │ source       │  │ job_id (FK)  │  │ job_id (FK)  │   │
│  │ qualification│  │ title        │  │ sent_at      │  │ reminder_type│   │
│  │ interests[]  │  │ organization │  └──────────────┘  │ sent_at      │   │
│  │ experience   │  │ eligibility  │                    └──────────────┘   │
│  │ status       │  │ degree_tags[]│                                             │
│  │ alert_mode   │  │ salary       │  ┌──────────────┐                        │
│  │ resume_url   │  │ exam_required│  │ Storage      │                        │
│  └──────────────┘  │ last_date    │  │ ───────────  │                        │
│                    │ apply_link   │  │ resumes/     │                        │
│                    │ raw_hash     │  │   user/      │                        │
│                    │ raw_text     │  │   resume.pdf │                        │
│                    └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Breakdown

#### A. Twilio WhatsApp API
- **Inbound:** Webhook POST to `/webhook` on every user message
- **Outbound:** Programmatic message creation via Twilio REST API
- **Media:** Supports PDF resume uploads via `MediaUrl0` parameter
- **Sandbox:** Free tier with 24-hour session window (sufficient for personal use)

#### B. Render Web Service (FastAPI)
- **Runtime:** Python 3.11 + Uvicorn ASGI server
- **Endpoints:**
  - `POST /webhook` — Main Twilio webhook handler
  - `GET /health` — Health check for UptimeRobot + monitoring
  - `GET /profile` — Debug endpoint to inspect current profile
- **State Management:** Stateless — all state persisted in Supabase
- **Keep-Alive:** UptimeRobot pings `/health` every 5 minutes to prevent Render free-tier spin-down

#### C. Render Cron Jobs
- **Job 1 — Scraper:** Runs hourly (`0 * * * *`)
  - Orchestrates the full pipeline
  - Isolated per-source error handling
  - Logs all operations for debugging
- **Job 2 — Reminders:** Runs daily at 8 AM (`0 8 * * *`)
  - Queries jobs with `last_date` = today+3, today+1, today
  - Sends deadline reminder WhatsApp messages
  - Prevents duplicate reminders via `exam_reminders` table

#### D. Supabase (Backend)
- **PostgreSQL:** 4 tables with indexes, RLS policies, auto-update triggers
- **Storage:** Private bucket for resume PDFs
- **Connection:** Service role key for admin operations (bypasses RLS in v1)

---

## 4. Data Flow

### 4.1 Onboarding Flow

```
User sends "hello"
    │
    ▼
Twilio webhook → POST /webhook
    │
    ▼
FastAPI receives message
    │
    ▼
Check if profile exists in Supabase
    │
    ├── No  → Create new profile (state = "welcome")
    │
    └── Yes → Check onboarding_state
                │
                ├── "welcome"        → Send welcome, ask qualification
                ├── "qualification"  → Save degree OR parse resume
                ├── "interests"      → Save sector preferences
                ├── "experience"     → Save experience level
                ├── "confirmation"   → Show summary, wait for YES/NO
                └── "complete"       → Handle commands or default reply
    │
    ▼
Build TwiML response → Return XML to Twilio
    │
    ▼
Twilio delivers message to user's WhatsApp
```

### 4.2 Job Alert Pipeline (Cron Job)

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
    If matched AND not already alerted:
    │
    ├── Format short alert message
    ├── Send via Twilio WhatsApp API
    └── Record in sent_alerts table
```

### 4.3 Exam Reminder Flow

```
Daily at 8 AM
    │
    ▼
Query jobs WHERE last_date = TODAY+3, TODAY+1, TODAY
    │
    ▼
For each job:
    ├── Check if reminder already sent (exam_reminders table)
    ├── Match against user profile
    │   ├── No match → Skip
    │   └── Match → Send reminder WhatsApp
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
│ whatsapp_no │       │ source      │       │ job_id (FK) │
│ qualification│      │ title       │       │ sent_at     │
│ interests[] │       │ organization│       └─────────────┘
│ experience  │       │ eligibility │
│ status      │       │ degree_tags[]
│ alert_mode  │       │ salary      │
│ resume_url  │       │ exam_required│      ┌─────────────┐
│ created_at  │       │ last_date   │      │exam_remind..│
│ updated_at  │       │ apply_link  │      ├─────────────┤
└─────────────┘       │ raw_hash    │      │ id (PK)     │
                      │ scraped_at  │      │ job_id (FK) │
                      └─────────────┘      │ reminder_type
                                           │ sent_at     │
                                           └─────────────┘
```

### 5.2 Table Details

**profiles**
- Stores user preferences and onboarding state
- `alert_mode` controls delivery: instant | digest | paused | bulk
- `onboarding_state` drives the conversation flow

**jobs**
- Stores all scraped job postings
- `raw_hash` (SHA256) enables deduplication across sources
- `exam_required` tracks exams like GATE, UPSC, SSC, Banking
- `degree_tags` array for fast qualification filtering

**sent_alerts**
- Prevents duplicate WhatsApp messages
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

## 8. Security & Privacy

- **Environment variables:** All secrets stored in Render environment, never in code
- **Database:** Row Level Security (RLS) enabled with service-role policies
- **Resume storage:** Private Supabase Storage bucket, no public access
- **WhatsApp:** Twilio handles end-to-end encryption; bot only sees message content
- **No PII logging:** Phone numbers are logged only for debugging, not stored externally

---

## 9. Scalability & Extensibility

### 9.1 Current Limits (Free Tier)
- **User count:** 1 (v1 single-user design)
- **Scrape frequency:** Hourly (adjustable in render.yaml)
- **Message volume:** ~500-1000/month within Twilio trial
- **Data storage:** 500MB PostgreSQL + 1GB file storage

### 9.2 Extension Points
- **Multi-user:** Add `user_id` foreign key to all tables, add auth layer
- **New sources:** Implement `BaseScraper` class, add to `get_all_scrapers()`
- **Better matching:** Replace keyword matching with embedding-based semantic search
- **Web dashboard:** Add React frontend using Supabase auth
- **Push notifications:** Add Firebase Cloud Messaging for non-WhatsApp alerts

---

## 10. Technology Choices Justification

| Component | Choice | Alternative | Why This One |
|-----------|--------|-------------|--------------|
| WhatsApp | Twilio | Meta Business API | Twilio handles complexity, sandbox for free testing |
| Web Framework | FastAPI | Flask/Django | Async-native, automatic OpenAPI docs, Twilio-friendly |
| Database | Supabase | Firebase, AWS RDS | Free tier includes auth + storage + Postgres + realtime |
| AI | Gemini Flash | Claude, GPT-4 | Free tier generous, fast, good at structured extraction |
| Hosting | Render | Heroku, Railway | Native cron jobs, free tier sufficient, simple deploy |
| Keep-Alive | UptimeRobot | Pingdom | Free 5-minute intervals, 50 monitors |

---

## 11. Monitoring & Observability

- **Render Logs:** Real-time stdout/stderr for all services
- **UptimeRobot:** External health check with email alerts on downtime
- **Twilio Logs:** Message delivery status and error tracking
- **Supabase Dashboard:** Query performance, storage usage, connection stats
- **Application Logs:** Structured logging with source tags for easy filtering

---

## 12. Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| Scraper fails on one source | Other 3 sources continue | Automatic on next cron run |
| Gemini rate limit | Jobs missed for 1 cycle | Exponential backoff retry |
| Twilio API error | Alert not sent | Job stays in DB, retried next cycle |
| Database connection lost | Operations fail | 3 retries with backoff, fail-safe defaults |
| Render web service spins down | Webhook timeout | UptimeRobot prevents this |
| User sends invalid command | Bot replies with help | No crash, graceful degradation |

---

*Document Version: 2.0.0*  
*Last Updated: 2026-08-08*  
*Author: Rajat9para*
