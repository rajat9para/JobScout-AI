# JobScout v2 — Features & Usage Guide

> Complete list of features, commands, and how to use your personal government job alert bot.

---

## 🎯 Core Features

### 1. AI-Powered Job Extraction
**What it does:** Automatically reads unstructured government job portal pages and extracts structured data (post name, organization, salary, exam, last date, apply link) using Google's Gemini AI.

**Why it matters:** Government websites change layouts frequently. Traditional CSS selectors break every month. Gemini understands context and works regardless of HTML structure changes.

**How to use:** No user action required. Runs automatically every hour.

---

### 2. Smart Profile Matching
**What it does:** Matches extracted jobs against your qualification, interests, and experience level before sending alerts.

**Matching dimensions:**
- **Qualification:** B.Tech, BSc, BCA, Law, MBA, Diploma, etc.
- **Interests:** PSU, Banking, Railways, Defence, IT/Software, SSC, UPSC, Teaching, State Govt, Judiciary, Medical
- **Experience:** Fresher, 0-2 years, 2+ years

**How to use:** Set up during onboarding (send "hello" to start). Update anytime with "UPDATE" command.

---

### 3. WhatsApp Job Alerts
**What it does:** Sends short, focused job alerts directly to your WhatsApp with only the essential information.

**Alert format:**
```
🎓 New Govt Job Alert

📌 Post: Graduate Engineer Trainee
🏢 Org: BHEL
💰 Salary: ₹35,000–₹45,000/month
📝 Exam: GATE 2026
📅 Last Date: 15 Aug 2026
🔗 Details: https://apply-link.com

Reply PAUSE | UPDATE | HELP
```

**How to use:** Automatic once profile is set up. Control with PAUSE/RESUME commands.

---

### 4. Resume Upload & Auto-Detection
**What it does:** Upload your resume PDF and the bot uses Gemini to automatically detect your qualification, degree, and experience level.

**How to use:**
1. During onboarding, send your resume PDF instead of typing qualification
2. The bot parses it and extracts your details
3. Your resume is stored securely in Supabase Storage (private bucket)

**Note:** Resume parsing is basic in v2. For best results, also verify the detected qualification manually.

---

### 5. Multiple Alert Modes

#### ⚡ Instant Mode (Default)
- Sends job alerts immediately when a matching job is found
- Best for: Users who want to apply as soon as possible
- Command: `INSTANT`

#### 📋 Digest Mode
- Sends ONE summary message per day at 9 AM with all matched jobs
- Best for: Users who don't want frequent notifications
- Command: `DIGEST`

#### 📦 Bulk Mode
- Sends ALL new government jobs, not just matched ones
- Best for: Users who want to see everything and decide manually
- Command: `BULK`

#### 🎯 Matched Mode
- Sends ONLY jobs that match your profile (default behavior)
- Best for: Focused job search
- Command: `MATCHED`

#### ⏸️ Paused Mode
- Stops all alerts temporarily
- Best for: When you're busy or on vacation
- Command: `PAUSE`

---

### 6. Exam Deadline Reminders
**What it does:** Automatically reminds you 3 days, 1 day, and on the last day of application deadlines for matched jobs.

**Reminder format:**
```
⏰ 3 Days Left!

📌 Post: Graduate Engineer Trainee
🏢 Org: BHEL
📝 Exam: GATE 2026
📅 Last Date: 15 Aug 2026
🔗 Apply: https://apply-link.com

Don't miss it! 🚀
```

**How to use:** Automatic. Runs daily at 8 AM. No command needed.

---

### 7. Multi-Source Scraping
**What it does:** Monitors 4 major government job portals simultaneously:

| Source | Type | Frequency |
|--------|------|-----------|
| NCS.gov.in | Official Govt Portal | Hourly |
| SarkariResult.com | High-frequency Aggregator | Hourly |
| FreeJobAlert.com | Cross-reference Source | Hourly |
| EmploymentNews.gov.in | Official Gazette | Hourly |

**Isolation:** If one source fails, the other 3 continue working. No single point of failure.

---

### 8. Deduplication Engine
**What it does:** Uses SHA256 hashing to ensure you NEVER receive the same job posting twice, even if it appears on multiple portals.

**How it works:**
- Hash = SHA256(source + title + organization + last_date)
- Every new job is checked against the database
- Duplicates are silently skipped

---

### 9. Graceful Error Handling
**What it does:** The bot never crashes. Every operation has retry logic with exponential backoff.

**Protected operations:**
- Database reads/writes (3 retries)
- Gemini API calls (3 retries with rate limit handling)
- Twilio message sending (immediate failure handling)
- Web scraping (per-source isolation)

---

### 10. Command System

Send any of these commands to the bot at any time:

| Command | What It Does | Response Time |
|---------|-------------|---------------|
| `HELLO` / `HI` / `START` | Start onboarding or show help | Instant |
| `UPDATE` | Restart profile setup | Instant |
| `PAUSE` | Stop all alerts | Instant |
| `RESUME` | Start alerts again | Instant |
| `STATUS` | View your current profile | Instant |
| `INSTANT` | Switch to instant alerts | Instant |
| `DIGEST` | Switch to daily digest | Instant |
| `BULK` | See ALL jobs (not just matched) | Instant |
| `MATCHED` | See only matched jobs | Instant |
| `STATS` | Show today's job statistics | Instant |
| `FEEDBACK <message>` | Send feedback to developer | Instant |
| `HELP` | Show all available commands | Instant |

---

## 📱 How to Use — Complete Walkthrough

### First Time Setup

1. **Send "hello"** to the Twilio WhatsApp sandbox number
2. **Enter your qualification** (e.g., "B.Tech", "BSc", "Law", "MBA")
   - OR upload your resume PDF
3. **Select interests** by replying with numbers:
   - Example: `1,3,5` (PSU, Railways, IT/Software)
   - Or type: `All` for everything
4. **Select experience:**
   - 1 = Fresher
   - 2 = 0-2 yrs
   - 3 = 2+ yrs
5. **Confirm with YES**

Done! You'll start receiving alerts.

### Daily Usage

**Morning check:**
- Send `STATS` to see how many new jobs were found today
- Check your WhatsApp for any overnight alerts

**During the day:**
- Alerts arrive automatically for matching jobs
- Each alert has: Post, Org, Salary, Exam, Last Date, Apply Link

**Evening:**
- If you applied to jobs, no action needed
- If you want fewer notifications tomorrow: send `DIGEST`

### Changing Your Preferences

**Change qualification or interests:**
1. Send `UPDATE`
2. Go through onboarding again
3. Your new preferences take effect immediately

**Stop alerts temporarily:**
- Send `PAUSE` — all alerts stop
- Send `RESUME` when you want them back

**Switch alert frequency:**
- `INSTANT` — get alerts immediately (default)
- `DIGEST` — one summary per day at 9 AM
- `BULK` — see every government job, not just matched ones

---

## 🛠️ Advanced Features

### Resume-Based Matching (v2.1+)
When you upload a resume, the bot:
1. Stores it in encrypted Supabase Storage
2. Parses it with Gemini to detect your degree
3. Uses detected qualification for matching
4. Keeps the resume for future parsing improvements

**Privacy:** Your resume is stored in a private bucket. No one except the bot can access it.

### Interest Keyword Mapping
The bot uses intelligent keyword mapping for interests:

| Interest | Keywords Detected |
|----------|-------------------|
| PSU | BHEL, NTPC, ONGC, IOCL, GAIL, BPCL, SAIL, Coal India, Power Grid |
| Banking | Bank, RBI, SBI, IBPS, NABARD |
| Railways | Railway, RRB, RPF, Metro, Railtel |
| Defence | Army, Navy, Air Force, DRDO, ISRO, BSF, CRPF, CDS, NDA |
| IT/Software | IT, Software, Developer, Programmer, Data Scientist, AI |
| Judiciary | Judge, Judicial, Court, Law Officer, Public Prosecutor |
| Medical | Doctor, Medical Officer, Nurse, AIIMS, ESIC |

### Experience Detection
The bot automatically detects if a job is fresher-friendly:
- Keywords: fresher, trainee, apprentice, intern, graduate, entry-level, no experience
- If no experience requirement is mentioned, assumes fresher-friendly
- Senior roles (2+ years required) are filtered out for fresher profiles

---

## 📊 Alert Examples

### Example 1: PSU Job
```
🎓 New Govt Job Alert

📌 Post: Management Trainee
🏢 Org: NTPC Limited
💰 Salary: ₹40,000–₹55,000/month
📝 Exam: GATE 2026
📅 Last Date: 20 Aug 2026
🔗 Details: https://ntpc.co.in/careers

Reply PAUSE | UPDATE | HELP
```

### Example 2: Banking Job
```
🎓 New Govt Job Alert

📌 Post: Probationary Officer
🏢 Org: State Bank of India
💰 Salary: ₹36,000–₹63,000/month
📝 Exam: SBI PO 2026
📅 Last Date: 12 Aug 2026
🔗 Details: https://sbi.co.in/web/careers

Reply PAUSE | UPDATE | HELP
```

### Example 3: Daily Digest
```
📋 Daily Job Digest

1. Graduate Engineer @ BHEL (Due: 15 Aug)
2. Probationary Officer @ SBI (Due: 12 Aug)
3. Junior Engineer @ Railways (Due: 18 Aug)
4. Scientist @ DRDO (Due: 25 Aug)
5. Stenographer @ SSC (Due: 10 Aug)

...and 3 more.

Reply BULK for full details | PAUSE to stop
```

---

## 🔧 Configuration Options

These are set in your `.env` file or Render environment variables:

| Setting | Default | Description |
|---------|---------|-------------|
| `SCRAPE_INTERVAL_MINUTES` | 60 | How often to check for new jobs |
| `GEMINI_MODEL` | gemini-1.5-flash | AI model for extraction |
| `LOG_LEVEL` | INFO | Detail level in logs (DEBUG/INFO/WARNING/ERROR) |
| `MAX_RETRIES` | 3 | Retry attempts for failed operations |
| `ENABLE_EXAM_REMINDERS` | true | Send deadline reminders |
| `ENABLE_DAILY_DIGEST` | false | Default digest mode |

---

## 🚀 Future Roadmap

### v2.1 (Next)
- [ ] PDF notice parsing (extract text from PDF job notifications)
- [ ] Better resume parsing (extract skills, projects, CGPA)
- [ ] Location-based filtering (state/city preferences)
- [ ] Salary range filtering

### v3.0 (Later)
- [ ] Multi-user support with authentication
- [ ] Web dashboard for profile management
- [ ] Push notifications (Firebase)
- [ ] Job application tracking (applied, shortlisted, rejected)
- [ ] Interview date reminders
- [ ] Community features (share jobs with friends)

---

## 💡 Tips for Best Results

1. **Use specific qualifications:** "B.Tech CSE" is better than just "Engineering"
2. **Select multiple interests:** Don't just pick one — government jobs often span categories
3. **Upload your resume:** Even basic parsing helps with matching accuracy
4. **Check STATS daily:** Know how many jobs the bot found even if none matched
5. **Use DIGEST mode during work hours:** Switch to INSTANT on weekends
6. **Don't ignore Bulk mode:** Sometimes a "non-matching" job is actually relevant
7. **Send FEEDBACK:** Your suggestions directly improve the bot

---

## 🐛 Common Questions

**Q: Why didn't I get any alerts today?**
A: Either no new matching jobs were posted, or your profile is too restrictive. Try BULK mode to see all jobs.

**Q: Can I add more job sources?**
A: Yes! Edit `app/scraper.py`, create a new scraper class, and add it to `get_all_scrapers()`. No other changes needed.

**Q: Is my data safe?**
A: Yes. Your phone number and resume are stored in Supabase with Row Level Security. The resume bucket is private.

**Q: How much does this cost?**
A: Completely free on free tiers. After Twilio trial ($15.50 credit), WhatsApp messages cost ~$0.005 each (~$3-5/month for personal use).

**Q: Can I use this for my friends too?**
A: v2 is single-user. v3 will support multiple users. For now, each friend needs their own deployment.

**Q: The bot stopped responding. What do I do?**
A: Check UptimeRobot dashboard. If monitor is down, check Render logs. Usually fixed by redeploying the web service.

---

*Version: 2.0.0*  
*Last Updated: 2026-08-08*
