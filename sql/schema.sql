-- JobScout v2.1 Database Schema (Supabase/PostgreSQL)
-- Run this in Supabase SQL Editor to initialize your database
-- v2.1: Replaced WhatsApp/Twilio with Brevo Email + PDF Digest

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Profiles Table ──
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    qualification TEXT,
    interests TEXT[],
    experience_level TEXT,
    resume_url TEXT,
    resume_parsed_text TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Jobs Table ──
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    description TEXT,                  -- NEW v2.3: 2-3 sentence job summary
    eligibility TEXT,
    age_limit TEXT,                    -- NEW v2.3: age limit extracted separately
    degree_tags TEXT[],
    salary TEXT,
    vacancies TEXT,
    selection_process TEXT,            -- NEW v2.3: how candidates are selected
    exam_required TEXT,
    last_date DATE,
    apply_link TEXT,
    notification_link TEXT,            -- NEW v2.3: URL to full article/notification
    raw_hash TEXT UNIQUE NOT NULL,
    raw_text TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Sent Alerts Table ──
-- Tracks which jobs have already been processed (dedup for digest queue)
CREATE TABLE IF NOT EXISTS sent_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Exam Reminders Table ──
CREATE TABLE IF NOT EXISTS exam_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL CHECK (reminder_type IN ('3_days', '1_day', 'today')),
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Daily Digest Table (NEW in v2.1) ──
-- Queues matched jobs throughout the day for the nightly PDF email
CREATE TABLE IF NOT EXISTS daily_digest (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    digest_date DATE DEFAULT CURRENT_DATE,
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Digest History Table (NEW in v2.2) ──
-- Tracks every digest email sent for dashboard history view
CREATE TABLE IF NOT EXISTS digest_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    digest_date DATE DEFAULT CURRENT_DATE,
    job_count INTEGER DEFAULT 0,
    digest_type TEXT DEFAULT 'scheduled' CHECK (digest_type IN ('scheduled', 'manual', 'morning', 'evening')),
    sent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ──
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
CREATE INDEX IF NOT EXISTS idx_jobs_raw_hash ON jobs(raw_hash);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_last_date ON jobs(last_date);
CREATE INDEX IF NOT EXISTS idx_sent_alerts_job_id ON sent_alerts(job_id);
CREATE INDEX IF NOT EXISTS idx_exam_reminders_job_type ON exam_reminders(job_id, reminder_type);
CREATE INDEX IF NOT EXISTS idx_daily_digest_date_sent ON daily_digest(digest_date, sent);
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_digest_unique ON daily_digest(job_id, digest_date);

-- ── Storage Bucket ──
-- Create manually in Supabase Dashboard → Storage → New Bucket
-- Name: resumes | Public: OFF

-- ── Row Level Security ──
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sent_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_digest ENABLE ROW LEVEL SECURITY;

-- Service role access (for v2.1 single-user)
CREATE POLICY "service_full_access_profiles" ON profiles FOR ALL USING (true);
CREATE POLICY "service_full_access_jobs" ON jobs FOR ALL USING (true);
CREATE POLICY "service_full_access_alerts" ON sent_alerts FOR ALL USING (true);
CREATE POLICY "service_full_access_reminders" ON exam_reminders FOR ALL USING (true);
CREATE POLICY "service_full_access_digest" ON daily_digest FOR ALL USING (true);

-- Enable RLS on digest_history
ALTER TABLE digest_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_full_access_digest_history" ON digest_history FOR ALL USING (true);

-- ── Auto-update Trigger ──
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Migration from v2.0 (if upgrading) ──
-- Run these if you have an existing v2.0 database:
--
-- ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT;
-- ALTER TABLE profiles DROP COLUMN IF EXISTS whatsapp_number;
-- ALTER TABLE profiles DROP COLUMN IF EXISTS alert_mode;
-- ALTER TABLE profiles DROP COLUMN IF EXISTS onboarding_state;
--
-- CREATE TABLE IF NOT EXISTS daily_digest ( ... );  -- use full definition above

-- ── Migration v2.3: Add rich detail columns to jobs ──
-- RUN THESE in Supabase SQL Editor if you have an existing database:
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS age_limit TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS selection_process TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS notification_link TEXT;
