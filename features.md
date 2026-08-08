# JobScout v2.1 — Features & Usage Guide

> Complete list of features, commands, and how to use your personal government job alert bot.
> **v2.1: Email Digest Edition** — Nightly PDF digest via Brevo email, replacing WhatsApp alerts.

---

## 🎯 Core Features

### 1. AI-Powered Job Extraction
**What it does:** Automatically reads unstructured government job portal pages and extracts structured data (post name, organization, salary, exam, last date, apply link) using Google's Gemini AI.

**Why it matters:** Government websites change layouts frequently. Traditional CSS selectors break every month. Gemini understands context and works regardless of HTML structure changes.

**How to use:** No user action required. Runs automatically every hour.

---

### 2. Smart Profile Matching
**What it does:** Matches extracted jobs against your qualification, interests, and experience level before adding them to your digest.

**Matching dimensions:**
- **Qualification:** B.Tech, BSc, BCA, Law, MBA, Diploma, etc.
- **Interests:** PSU, Banking, Railways, Defence, IT/Software, SSC, UPSC, Teaching, State Govt, Judiciary, Medical
- **Experience:** Fresher, 0-2 years, 2+ years

**How to use:** Set up via the web form at `/setup`. Update anytime by revisiting the form.

---

### 3. 📧 Nightly PDF Email Digest (NEW in v2.1)
**What it does:** Every night at 10 PM IST, generates a professional **PDF report** containing medium-length descriptions of all matched government jobs found during the day, and emails it to your inbox.

**What's in the PDF:**
- 📋 Summary statistics (job count, sources, open deadlines)
- For each job:
  - 📌 Post title
  - 🏢 Organization name
  - 📚 Eligibility requirements
  - 💰 Salary/pay scale
  - 👥 Number of vacancies
  - 📝 Required exam (GATE, UPSC, SSC, etc.)
  - 📅 Last date with urgency indicator (3 days left!, Last Day!, etc.)
  - 🔗 Direct apply link
  - 📡 Source portal
  - 🎓 Degree tags
- Page numbers and generation timestamp
- Clean, professional formatting with color-coded headers

**How to use:** Automatic once profile is set up. Check your email every night!

---

### 4. 📅 Exam Deadline Reminders
**What it does:** Automatically sends email reminders 3 days, 1 day, and on the last day of application deadlines for matched jobs.

**Reminder emails include:**
- Job title and organization
- Exam name
- Last date (highlighted with urgency)
- Direct "Apply Now" button/link

**How to use:** Automatic. Runs daily at 8 AM IST. No action needed.

---

### 5. Multi-Source Scraping
**What it does:** Monitors 4 major government job portals simultaneously:

| Source | Type | Frequency |
|--------|------|-----------|
| NCS.gov.in | Official Govt Portal | Hourly |
| SarkariResult.com | High-frequency Aggregator | Hourly |
| FreeJobAlert.com | Cross-reference Source | Hourly |
| EmploymentNews.gov.in | Official Gazette | Hourly |

**Isolation:** If one source fails, the other 3 continue working. No single point of failure.

---

### 6. Deduplication Engine
**What it does:** Uses SHA256 hashing to ensure you NEVER receive the same job posting twice, even if it appears on multiple portals.

**How it works:**
- Hash = SHA256(source + title + organization + last_date)
- Every new job is checked against the database
- Duplicates are silently skipped

---

### 7. Graceful Error Handling
**What it does:** The system never crashes. Every operation has retry logic with exponential backoff.

**Protected operations:**
- Database reads/writes (3 retries)
- Gemini API calls (3 retries with rate limit handling)
- Brevo email sending (3 retries with exponential backoff)
- Web scraping (per-source isolation)
- PDF generation (fallback on error)

---

### 8. Web-Based Profile Setup
**What it does:** Simple, beautiful web form to set up your profile. No WhatsApp onboarding needed.

**Profile fields:**
- 📧 Email address (for receiving digests)
- 📚 Qualification (B.Tech, BSc, Law, MBA, etc.)
- 📋 Interest sectors (checkboxes)
- 💼 Experience level (radio buttons)

**How to use:** Visit `/setup` on your deployed web service.

---

## 📱 How to Use — Complete Walkthrough

### First Time Setup

1. **Deploy** the project on Render (follow `toyourtask.txt`)
2. **Visit** `https://your-app.onrender.com/setup`
3. **Fill in** the profile form:
   - Your email address
   - Your qualification (e.g., B.Tech, BSc, Law, MBA)
   - Select interest sectors (PSU, Banking, Railways, etc.)
   - Select experience level (Fresher, 0-2 yrs, 2+ yrs)
4. **Click "Save Profile"**

Done! You'll start receiving nightly PDF digests.

### Daily Usage

**Morning:**
- Check your email for deadline reminders (sent at 8 AM IST)

**During the day:**
- Jobs are scraped hourly and matched against your profile
- Matched jobs are queued for tonight's digest

**Night (10 PM IST):**
- 📧 Receive PDF digest email
- Open the PDF attachment
- Review all matched jobs in one place
- Apply to interesting positions

### Changing Your Preferences

**Update profile:**
1. Visit `/setup` again
2. Modify your details
3. Click "Save Profile"
4. Changes take effect immediately

### Web Endpoints

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check for UptimeRobot |
| `/setup` | GET | Profile setup form |
| `/setup` | POST | Save/update profile |
| `/profile` | GET | View profile as JSON |
| `/digest-status` | GET | Check pending digest jobs |
| `/trigger-digest` | GET | Manually send digest (testing) |

---

## 🛠️ Advanced Features

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

## 📊 What You Receive

### Nightly PDF Digest (10 PM IST)
```
📋 JobScout — Daily Job Digest
Generated on Friday, 08 August 2026 • 7 matching jobs found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Graduate Engineer Trainee
   🏢 BHEL
   📚 Eligibility: B.Tech/B.E. in any branch, 60% min
   💰 Salary: ₹35,000–₹45,000/month
   👥 Vacancies: 150
   📝 Exam: GATE 2026
   📅 Last Date: 15 Aug 2026 (7 days left)
   🔗 Apply: https://bhel.com/careers
   🎓 Degrees: B.Tech, B.E.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. Probationary Officer
   🏢 State Bank of India
   ...
```

### Deadline Reminder Email
```
Subject: ⏰ 3 Days Left — Graduate Engineer Trainee @ BHEL

📌 Post: Graduate Engineer Trainee
🏢 Organization: BHEL
📝 Exam: GATE 2026
📅 Last Date: 15 Aug 2026

[Apply Now →]
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
| `SENDER_NAME` | JobScout Bot | Name shown in email "From" field |

---

## 🚀 Future Roadmap

### v2.2 (Next)
- [ ] PDF notice parsing (extract text from PDF job notifications)
- [ ] Better resume parsing (extract skills, projects, CGPA)
- [ ] Location-based filtering (state/city preferences)
- [ ] Salary range filtering
- [ ] Weekly digest option (in addition to daily)

### v3.0 (Later)
- [ ] Multi-user support with authentication
- [ ] Web dashboard for profile management
- [ ] Job application tracking (applied, shortlisted, rejected)
- [ ] Interview date reminders
- [ ] Community features (share jobs with friends)
- [ ] Push notifications (Firebase)

---

## 💡 Tips for Best Results

1. **Use specific qualifications:** "B.Tech CSE" is better than just "Engineering"
2. **Select multiple interests:** Don't just pick one — government jobs often span categories
3. **Check your email nightly:** The PDF arrives at 10 PM IST with all day's matches
4. **Check spam folder:** Add the sender email to your contacts for reliable delivery
5. **Use /trigger-digest for testing:** Manually trigger a digest to verify everything works
6. **Monitor Brevo dashboard:** Check email delivery logs if digests stop arriving

---

## 🐛 Common Questions

**Q: Why didn't I get a digest email today?**
A: Check Brevo API key is valid, sender email is verified, and check spam folder. Try `/trigger-digest` to test manually.

**Q: Can I add more job sources?**
A: Yes! Edit `app/scraper.py`, create a new scraper class, and add it to `get_all_scrapers()`. No other changes needed.

**Q: Is my data safe?**
A: Yes. Your email and profile are stored in Supabase with Row Level Security. The resume bucket is private.

**Q: How much does this cost?**
A: Completely free on free tiers. Brevo gives 300 emails/day free (you only need 1-2/day).

**Q: The PDF is empty every night. What do I do?**
A: Widen your interests on the `/setup` page. Check scraper logs in Render to see if jobs are being found and matched.

**Q: Can I change the digest time?**
A: Yes! Update the cron schedule in `render.yaml`. The default is `30 16 * * *` (4:30 PM UTC = 10 PM IST).

---

*Version: 2.1.0*  
*Last Updated: 2026-08-08*
