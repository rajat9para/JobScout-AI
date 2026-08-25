# JobScout v2.2 — Features & Capabilities Guide

> Complete reference guide for JobScout-AI: Autonomous Government Job Intelligence & Workplace Reality Engine powered by Dual Groq LPU™ AI.

---

## 🎯 Core Features & System Capabilities

### 1. 🧠 AI Job Intelligence & Workplace Reality Engine (NEW v2.2)
- **Dual Groq LPU Agents:**
  - **Groq Agent #1 (Job Intelligence Agent):** Parses job descriptions into structured requirement profiles with prompt injection defenses.
  - **Groq Agent #2 (Job Reality Research & Evidence Engine):** Investigates verified public employee sentiment, work-life balance, management culture, and interview difficulty.
- **Evidence-Based Workplace Reality (/5.0 Ratings):**
  - Employee Sentiment (/5.0)
  - Work-Life Balance (/5.0)
  - Learning & Growth (/5.0)
  - Management Culture (/5.0)
  - Interview Difficulty (/5.0)
- **Interview Intelligence:**
  - Complete selection rounds breakdown (e.g. Prelims, Mains, Interview)
  - Common technical syllabus & exam topics
  - Candidate preparation tips
- **Transparent Source Citations:** Every claim includes source counts, recency, confidence levels, and citations.

---

### 2. 🎯 Deterministic 6-Factor Match Engine
- **Explainable Scoring:** 100% mathematical breakdown avoiding LLM scoring hallucinations:
  - 35% Skills & Degree Qualification Match
  - 20% Experience Level Compatibility
  - 20% Ranked Sector Priority Hierarchy
  - 10% Location Fit
  - 10% Salary / Grade Pay Fit
  - 5% Work Mode Fit
- **Actionable Recommendations:** `🌟 STRONG APPLY`, `✅ APPLY`, `🔍 INVESTIGATE`, `📌 CONSIDER`, `✕ SKIP`.

---

### 3. ⏳ Strict Expired Job Filtering
- Completely excludes past-deadline jobs (`last_date < date.today()`) from matching, email digests, intelligence candidate queues, and generated PDFs.

---

### 4. ⚡ Groq LPU™ Ultra-Fast AI Extraction
- **Inference Engine:** Powered by Groq LPU infrastructure using `openai/gpt-oss-20b` with multi-model fallback (`openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, `groq/compound-mini`).
- **Latency:** Sub-1.2s extraction time per scraped chunk.
- **Structured Fields Extracted:**
  - Official Post Title & Organization
  - Scope of Work & Role Responsibilities
  - Salary Scale & Pay Band
  - Application Form Fee Breakdown (Category-wise)
  - Total Vacancy Count & Category Allocations
  - Age Limits & Relaxation Criteria
  - Complete Eligibility & Degree Requirements
  - Selection Process & Competitive Exam Requirements
  - Application Deadline Dates
  - Direct Application Portal & Official Notification PDF URLs

---

### 5. 📄 Executive-Grade PDF Reports (ReportLab)
- **Standard Daily Digest:** Executive summary, high-DPI badges, category groupings, form fee details, and direct links.
- **AI Reality Intelligence Report:** Specialized deep report with dual Match & Reality badges, 6-factor category progress bars, positive workplace signals, potential concerns, and interview breakdown.

---

### 6. 🚄 Animated Running Train Ticker & Glassmorphism Dashboard
- **Live Alert Train Marquee:** High-speed bullet train element gliding right to left across the header with real-time Sarkari alerts.
- **Crystal Glassmorphism UI:** Built with backdrop-filter blur, multi-color ambient lighting orbs, and neon glowing borders.
- **Theme Switching:** Instant toggle between Dark Indigo and Clean Ice Light themes.
- **Interactive Modals:** Deep Job Intelligence modal with rating meters, category bars, and one-click reality check refresh.

---

### 7. 🗄️ 15-Day Auto-Retention & Permanent Free-Tier ($0/Mo)
- **Data Cleanup:** Automatic daily cleanup at 3:00 AM IST purging records older than 15 days.
- **Keep-Alive Worker:** Runs every 8 hours to ensure Supabase project never enters inactive pause mode.
- **Cost:** Exactly $0.00/month utilizing free tier allocations on Groq, Supabase, Brevo, and Render.

---

### 8. 🕷️ 4-Source Multi-Portal Scraper
- Continuous hourly monitoring across:
  - `SarkariResult.com`
  - `FreeJobAlert.com`
  - `SarkariExam.com`
  - `RojgarResult.com`
