-- JobScout v2 Database Schema (Supabase/PostgreSQL)
-- Run this in Supabase SQL Editor to initialize your database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Profiles Table ──
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    whatsapp_number TEXT UNIQUE NOT NULL,
    qualification TEXT,
    interests TEXT[],
    experience_level TEXT,
    resume_url TEXT,
    resume_parsed_text TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused')),
    alert_mode TEXT DEFAULT 'instant' CHECK (alert_mode IN ('instant', 'digest', 'paused', 'bulk')),
    onboarding_state TEXT DEFAULT 'welcome',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Jobs Table ──
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    eligibility TEXT,
    degree_tags TEXT[],
    salary TEXT,
    vacancies TEXT,
    exam_required TEXT,
    last_date DATE,
    apply_link TEXT,
    raw_hash TEXT UNIQUE NOT NULL,
    raw_text TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Sent Alerts Table ──
CREATE TABLE sent_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Exam Reminders Table ──
CREATE TABLE exam_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL CHECK (reminder_type IN ('3_days', '1_day', 'today')),
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ──
CREATE INDEX idx_profiles_whatsapp ON profiles(whatsapp_number);
CREATE INDEX idx_profiles_status ON profiles(status);
CREATE INDEX idx_jobs_raw_hash ON jobs(raw_hash);
CREATE INDEX idx_jobs_scraped_at ON jobs(scraped_at);
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_last_date ON jobs(last_date);
CREATE INDEX idx_sent_alerts_job_id ON sent_alerts(job_id);
CREATE INDEX idx_exam_reminders_job_type ON exam_reminders(job_id, reminder_type);

-- ── Storage Bucket ──
-- Create manually in Supabase Dashboard → Storage → New Bucket
-- Name: resumes | Public: OFF

-- ── Row Level Security ──
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sent_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_reminders ENABLE ROW LEVEL SECURITY;

-- Service role access (for v1 single-user)
CREATE POLICY "service_full_access_profiles" ON profiles FOR ALL USING (true);
CREATE POLICY "service_full_access_jobs" ON jobs FOR ALL USING (true);
CREATE POLICY "service_full_access_alerts" ON sent_alerts FOR ALL USING (true);
CREATE POLICY "service_full_access_reminders" ON exam_reminders FOR ALL USING (true);

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
