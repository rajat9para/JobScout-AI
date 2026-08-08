"""Dashboard HTML generator — beautiful single-page web dashboard.

Serves a complete interactive dashboard for:
- Viewing bot status and digest queue
- Pausing/resuming notifications
- Modifying profile (interests, qualification, experience)
- Uploading resume
- Viewing past digest history
- Triggering manual digest
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobScout — Dashboard</title>
    <link rel="icon" type="image/png" href="/static/weblogo.png">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        :root {
            --bg-dark: #0f0f23;
            --bg-card: #1a1a2e;
            --bg-card-hover: #1f1f35;
            --accent: #4f8cff;
            --accent-glow: rgba(79, 140, 255, 0.3);
            --accent-green: #00d68f;
            --accent-red: #ff6b6b;
            --accent-orange: #ffa94d;
            --accent-purple: #b197fc;
            --text-primary: #e8e8f0;
            --text-secondary: #8b8ba3;
            --text-muted: #5a5a7a;
            --border: #2a2a45;
            --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-2: linear-gradient(135deg, #4f8cff 0%, #00d68f 100%);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ── Background Animation ── */
        body::before {
            content: '';
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 30% 40%, rgba(79,140,255,0.05) 0%, transparent 50%),
                        radial-gradient(circle at 70% 60%, rgba(118,75,162,0.05) 0%, transparent 50%);
            animation: bgPulse 15s ease-in-out infinite alternate;
            z-index: 0;
        }
        @keyframes bgPulse {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-20px, -20px) rotate(3deg); }
        }

        /* ── Header ── */
        .header {
            position: relative; z-index: 10;
            background: rgba(15, 15, 35, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 16px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .logo {
            width: 42px; height: 42px;
            border-radius: 10px;
            object-fit: cover;
            border: 2px solid var(--accent);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        .header-title {
            font-size: 22px;
            font-weight: 700;
            background: var(--gradient-2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header-version {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
        }
        .header-right {
            display: flex; gap: 12px; align-items: center;
        }

        /* ── Status Badge ── */
        .status-badge {
            display: flex; align-items: center; gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .status-active {
            background: rgba(0, 214, 143, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(0, 214, 143, 0.3);
        }
        .status-active:hover { background: rgba(0, 214, 143, 0.25); }
        .status-paused {
            background: rgba(255, 107, 107, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        .status-paused:hover { background: rgba(255, 107, 107, 0.25); }
        .status-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        .status-active .status-dot { background: var(--accent-green); }
        .status-paused .status-dot { background: var(--accent-red); animation: none; }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        /* ── Main Layout ── */
        .main {
            position: relative; z-index: 10;
            max-width: 1200px;
            margin: 0 auto;
            padding: 28px 24px 60px;
        }

        /* ── Tabs ── */
        .tabs {
            display: flex;
            gap: 4px;
            margin-bottom: 28px;
            background: var(--bg-card);
            border-radius: 14px;
            padding: 5px;
            border: 1px solid var(--border);
        }
        .tab {
            flex: 1;
            padding: 12px 16px;
            border-radius: 10px;
            text-align: center;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            background: none;
        }
        .tab:hover { color: var(--text-primary); background: rgba(79,140,255,0.08); }
        .tab.active {
            background: var(--accent);
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 12px var(--accent-glow);
        }

        /* ── Tab Content ── */
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* ── Card ── */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .card:hover { border-color: rgba(79,140,255,0.3); box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .card-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* ── Stats Grid ── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-3px); border-color: var(--accent); }
        .stat-value {
            font-size: 32px;
            font-weight: 800;
            background: var(--gradient-2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* ── Form Elements ── */
        .form-group { margin-bottom: 22px; }
        .form-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255,255,255,0.04);
            border: 1.5px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 15px;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            outline: none;
        }
        .form-input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        .form-input::placeholder { color: var(--text-muted); }

        /* ── Chips (Interest Selection) ── */
        .chips { display: flex; flex-wrap: wrap; gap: 10px; }
        .chip {
            padding: 10px 18px;
            border-radius: 25px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            border: 1.5px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text-secondary);
            transition: all 0.3s ease;
            user-select: none;
        }
        .chip:hover { border-color: var(--accent); color: var(--text-primary); }
        .chip.selected {
            background: rgba(79,140,255,0.15);
            border-color: var(--accent);
            color: var(--accent);
            font-weight: 600;
        }

        /* ── Buttons ── */
        .btn {
            padding: 12px 28px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-family: 'Inter', sans-serif;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: var(--accent);
            color: white;
            box-shadow: 0 4px 12px var(--accent-glow);
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px var(--accent-glow); }
        .btn-success { background: var(--accent-green); color: #0a3d23; }
        .btn-success:hover { transform: translateY(-2px); }
        .btn-danger {
            background: rgba(255,107,107,0.15);
            color: var(--accent-red);
            border: 1.5px solid rgba(255,107,107,0.3);
        }
        .btn-danger:hover { background: rgba(255,107,107,0.25); }
        .btn-outline {
            background: transparent;
            color: var(--accent);
            border: 1.5px solid var(--accent);
        }
        .btn-outline:hover { background: rgba(79,140,255,0.1); }
        .btn-group { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }

        /* ── File Upload ── */
        .upload-zone {
            border: 2px dashed var(--border);
            border-radius: 14px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        .upload-zone:hover, .upload-zone.dragover {
            border-color: var(--accent);
            background: rgba(79,140,255,0.05);
        }
        .upload-zone input { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; }
        .upload-icon { font-size: 40px; margin-bottom: 12px; }
        .upload-text { font-size: 14px; color: var(--text-secondary); }
        .upload-hint { font-size: 12px; color: var(--text-muted); margin-top: 8px; }

        /* ── Digest History ── */
        .history-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }
        .history-item:hover { border-color: var(--accent); background: var(--bg-card-hover); }
        .history-date { font-weight: 600; font-size: 14px; }
        .history-meta { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
        .history-badge {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-sent { background: rgba(0,214,143,0.15); color: var(--accent-green); }
        .badge-pending { background: rgba(255,169,77,0.15); color: var(--accent-orange); }

        /* ── Toast ── */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            z-index: 1000;
            animation: slideUp 0.4s ease;
            box-shadow: var(--shadow);
        }
        .toast-success { background: var(--accent-green); color: #0a3d23; }
        .toast-error { background: var(--accent-red); color: white; }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

        /* ── Radio Group ── */
        .radio-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .radio-option {
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 13px;
            cursor: pointer;
            border: 1.5px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text-secondary);
            transition: all 0.3s ease;
        }
        .radio-option:hover { border-color: var(--accent); }
        .radio-option.selected {
            background: rgba(79,140,255,0.15);
            border-color: var(--accent);
            color: var(--accent);
            font-weight: 600;
        }

        /* ── Schedule Display ── */
        .schedule-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 16px;
        }
        .schedule-card {
            background: rgba(79,140,255,0.06);
            border: 1px solid rgba(79,140,255,0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        .schedule-time {
            font-size: 28px;
            font-weight: 800;
            background: var(--gradient-2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .schedule-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 6px;
            text-transform: uppercase;
        }

        /* ── Loading ── */
        .spinner {
            width: 20px; height: 20px;
            border: 2.5px solid rgba(255,255,255,0.2);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            display: inline-block;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Responsive ── */
        @media (max-width: 768px) {
            .header { padding: 12px 16px; }
            .main { padding: 16px 12px; }
            .tabs { flex-wrap: wrap; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .schedule-grid { grid-template-columns: 1fr; }
            .btn-group { flex-direction: column; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <img src="/static/weblogo.png" alt="JobScout" class="logo">
            <div>
                <div class="header-title">JobScout</div>
                <div class="header-version">v2.2 — Email Digest Edition</div>
            </div>
        </div>
        <div class="header-right">
            <div id="statusBadge" class="status-badge status-active" onclick="toggleStatus()">
                <span class="status-dot"></span>
                <span id="statusText">Active</span>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main">
        <!-- Stats -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-value" id="statPending">—</div>
                <div class="stat-label">Pending Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statTotalJobs">—</div>
                <div class="stat-label">Total Jobs Scraped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statDigestsSent">—</div>
                <div class="stat-label">Digests Sent</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statSources">4</div>
                <div class="stat-label">Active Sources</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('profile')">👤 Profile</button>
            <button class="tab" onclick="switchTab('schedule')">📅 Schedule</button>
            <button class="tab" onclick="switchTab('resume')">📄 Resume</button>
            <button class="tab" onclick="switchTab('history')">📬 History</button>
            <button class="tab" onclick="switchTab('actions')">⚡ Actions</button>
        </div>

        <!-- Tab: Profile -->
        <div id="tab-profile" class="tab-content active">
            <div class="card">
                <div class="card-title">📧 Email & Qualification</div>
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" class="form-input" id="inputEmail" placeholder="your@email.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Qualification / Degree</label>
                    <input type="text" class="form-input" id="inputQualification" placeholder="e.g., B.Tech, BSc, BCA, Law, MBA">
                </div>
            </div>

            <div class="card">
                <div class="card-title">📋 Interests</div>
                <p style="font-size:13px;color:var(--text-muted);margin-bottom:14px;">Select job sectors you're interested in</p>
                <div class="chips" id="interestChips"></div>
            </div>

            <div class="card">
                <div class="card-title">💼 Experience Level</div>
                <div class="radio-group" id="experienceGroup"></div>
            </div>

            <div class="btn-group">
                <button class="btn btn-primary" onclick="saveProfile()">💾 Save Profile</button>
            </div>
        </div>

        <!-- Tab: Schedule -->
        <div id="tab-schedule" class="tab-content">
            <div class="card">
                <div class="card-title">📅 Digest Schedule</div>
                <p style="color:var(--text-secondary);font-size:14px;margin-bottom:16px;">
                    You receive two PDF digest emails daily with all matched government jobs.
                </p>
                <div class="schedule-grid">
                    <div class="schedule-card">
                        <div style="font-size:24px;margin-bottom:8px;">🌅</div>
                        <div class="schedule-time">10:00 AM</div>
                        <div class="schedule-label">Morning Digest</div>
                    </div>
                    <div class="schedule-card">
                        <div style="font-size:24px;margin-bottom:8px;">🌇</div>
                        <div class="schedule-time">6:00 PM</div>
                        <div class="schedule-label">Evening Digest</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">🔔 Deadline Reminders</div>
                <p style="color:var(--text-secondary);font-size:14px;">
                    Automatic email reminders are sent <strong>3 days</strong>, <strong>1 day</strong>, 
                    and on the <strong>last day</strong> of application deadlines for matched jobs.
                </p>
            </div>
        </div>

        <!-- Tab: Resume -->
        <div id="tab-resume" class="tab-content">
            <div class="card">
                <div class="card-title">📄 Upload Resume</div>
                <p style="color:var(--text-secondary);font-size:14px;margin-bottom:20px;">
                    Upload your resume to improve job matching. The AI extracts your skills,
                    qualifications, and experience automatically.
                </p>
                <div class="upload-zone" id="uploadZone">
                    <input type="file" id="resumeFile" accept=".pdf,.doc,.docx,.txt" onchange="handleResumeUpload(event)">
                    <div class="upload-icon">📎</div>
                    <div class="upload-text">Drag & drop your resume or click to browse</div>
                    <div class="upload-hint">Supports PDF, DOC, DOCX, TXT (max 5MB)</div>
                </div>
                <div id="resumeStatus" style="margin-top:16px;display:none;"></div>
            </div>
            <div class="card" id="resumeInfoCard" style="display:none;">
                <div class="card-title">✅ Resume on File</div>
                <div id="resumeInfo" style="font-size:14px;color:var(--text-secondary);line-height:1.8;"></div>
            </div>
        </div>

        <!-- Tab: History -->
        <div id="tab-history" class="tab-content">
            <div class="card">
                <div class="card-title">📬 Digest History</div>
                <div id="historyList">
                    <p style="color:var(--text-muted);text-align:center;padding:30px;">Loading history...</p>
                </div>
            </div>
        </div>

        <!-- Tab: Actions -->
        <div id="tab-actions" class="tab-content">
            <div class="card">
                <div class="card-title">⚡ Quick Actions</div>
                <div class="btn-group" style="flex-direction:column;gap:14px;">
                    <button class="btn btn-primary" onclick="triggerDigest()" id="btnTriggerDigest" style="width:100%;justify-content:center;">
                        📧 Send Digest Now
                    </button>
                    <button class="btn btn-outline" onclick="triggerScrape()" id="btnScrape" style="width:100%;justify-content:center;">
                        🔍 Run Scraper Now
                    </button>
                    <button class="btn btn-danger" onclick="toggleStatus()" id="btnToggle" style="width:100%;justify-content:center;">
                        ⏸️ Pause Notifications
                    </button>
                </div>
            </div>
            <div class="card">
                <div class="card-title">🔗 Quick Links</div>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <a href="/health" target="_blank" style="color:var(--accent);text-decoration:none;font-size:14px;">🩺 Health Check →</a>
                    <a href="/api/profile" target="_blank" style="color:var(--accent);text-decoration:none;font-size:14px;">📊 Profile JSON →</a>
                    <a href="/api/digest-status" target="_blank" style="color:var(--accent);text-decoration:none;font-size:14px;">📋 Digest Status →</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ── Config ──
        const INTERESTS = [
            {name: "PSU", emoji: "🏭"}, {name: "Banking", emoji: "🏦"},
            {name: "Railways", emoji: "🚂"}, {name: "Defence", emoji: "🎖️"},
            {name: "IT/Software", emoji: "💻"}, {name: "SSC", emoji: "📊"},
            {name: "UPSC", emoji: "🏛️"}, {name: "Teaching", emoji: "📚"},
            {name: "State Govt", emoji: "🏘️"}, {name: "Judiciary", emoji: "⚖️"},
            {name: "Medical", emoji: "🏥"}
        ];
        const EXPERIENCE_LEVELS = ["Fresher", "0-2 yrs", "2+ yrs"];

        let selectedInterests = [];
        let selectedExperience = "Fresher";
        let currentStatus = "active";

        // ── Init ──
        document.addEventListener("DOMContentLoaded", () => {
            renderInterestChips();
            renderExperienceOptions();
            loadProfile();
            loadStats();
            loadHistory();
        });

        // ── Tab Switching ──
        function switchTab(tabId) {
            document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
            document.getElementById("tab-" + tabId).classList.add("active");
            event.target.classList.add("active");
            if (tabId === "history") loadHistory();
        }

        // ── Interest Chips ──
        function renderInterestChips() {
            const container = document.getElementById("interestChips");
            container.innerHTML = INTERESTS.map(i =>
                `<div class="chip ${selectedInterests.includes(i.name) ? 'selected' : ''}"
                     onclick="toggleInterest('${i.name}', this)">${i.emoji} ${i.name}</div>`
            ).join("");
        }
        function toggleInterest(name, el) {
            if (selectedInterests.includes(name)) {
                selectedInterests = selectedInterests.filter(i => i !== name);
                el.classList.remove("selected");
            } else {
                selectedInterests.push(name);
                el.classList.add("selected");
            }
        }

        // ── Experience Options ──
        function renderExperienceOptions() {
            const container = document.getElementById("experienceGroup");
            container.innerHTML = EXPERIENCE_LEVELS.map(exp =>
                `<div class="radio-option ${selectedExperience === exp ? 'selected' : ''}"
                     onclick="selectExperience('${exp}', this)">${exp}</div>`
            ).join("");
        }
        function selectExperience(exp, el) {
            selectedExperience = exp;
            document.querySelectorAll("#experienceGroup .radio-option").forEach(e => e.classList.remove("selected"));
            el.classList.add("selected");
        }

        // ── Load Profile ──
        async function loadProfile() {
            try {
                const res = await fetch("/api/profile");
                if (!res.ok) return;
                const profile = await res.json();
                document.getElementById("inputEmail").value = profile.email || "";
                document.getElementById("inputQualification").value = profile.qualification || "";
                selectedInterests = profile.interests || [];
                selectedExperience = profile.experience_level || "Fresher";
                currentStatus = profile.status || "active";
                renderInterestChips();
                renderExperienceOptions();
                updateStatusUI();
                if (profile.resume_url) {
                    document.getElementById("resumeInfoCard").style.display = "block";
                    document.getElementById("resumeInfo").innerHTML =
                        `<strong>📎 Resume uploaded</strong><br>
                         Qualification: ${profile.qualification || "—"}<br>
                         Experience: ${profile.experience_level || "—"}`;
                }
            } catch (e) { console.error("Profile load error:", e); }
        }

        // ── Load Stats ──
        async function loadStats() {
            try {
                const res = await fetch("/api/stats");
                if (!res.ok) return;
                const stats = await res.json();
                document.getElementById("statPending").textContent = stats.pending_today ?? "0";
                document.getElementById("statTotalJobs").textContent = stats.total_jobs ?? "—";
                document.getElementById("statDigestsSent").textContent = stats.digests_sent ?? "0";
            } catch (e) { console.error("Stats load error:", e); }
        }

        // ── Load History ──
        async function loadHistory() {
            try {
                const res = await fetch("/api/digest-history");
                if (!res.ok) { document.getElementById("historyList").innerHTML = "<p style='color:var(--text-muted);text-align:center;'>No digest history yet.</p>"; return; }
                const history = await res.json();
                if (!history.length) {
                    document.getElementById("historyList").innerHTML = "<p style='color:var(--text-muted);text-align:center;padding:30px;'>No digests sent yet. Jobs will be collected and emailed at 10 AM and 6 PM IST.</p>";
                    return;
                }
                document.getElementById("historyList").innerHTML = history.map(h => `
                    <div class="history-item">
                        <div>
                            <div class="history-date">📧 ${h.date}</div>
                            <div class="history-meta">${h.job_count} jobs • ${h.type || 'Daily Digest'}</div>
                        </div>
                        <span class="history-badge ${h.sent ? 'badge-sent' : 'badge-pending'}">
                            ${h.sent ? '✅ Sent' : '⏳ Pending'}
                        </span>
                    </div>
                `).join("");
            } catch (e) {
                document.getElementById("historyList").innerHTML = "<p style='color:var(--text-muted);text-align:center;'>Could not load history.</p>";
            }
        }

        // ── Save Profile ──
        async function saveProfile() {
            const email = document.getElementById("inputEmail").value.trim();
            const qualification = document.getElementById("inputQualification").value.trim();
            if (!email || !qualification) { showToast("Email and Qualification are required", "error"); return; }
            if (selectedInterests.length === 0) { showToast("Select at least one interest", "error"); return; }

            try {
                const res = await fetch("/api/profile", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        email, qualification,
                        interests: selectedInterests,
                        experience_level: selectedExperience
                    })
                });
                if (res.ok) { showToast("Profile saved successfully! ✅", "success"); loadStats(); }
                else { const data = await res.json(); showToast(data.error || "Save failed", "error"); }
            } catch (e) { showToast("Network error. Check connection.", "error"); }
        }

        // ── Toggle Status ──
        async function toggleStatus() {
            const newStatus = currentStatus === "active" ? "paused" : "active";
            try {
                const res = await fetch("/api/status", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({status: newStatus})
                });
                if (res.ok) {
                    currentStatus = newStatus;
                    updateStatusUI();
                    showToast(newStatus === "active" ? "Notifications resumed! 🔔" : "Notifications paused ⏸️", "success");
                }
            } catch (e) { showToast("Failed to update status", "error"); }
        }

        function updateStatusUI() {
            const badge = document.getElementById("statusBadge");
            const text = document.getElementById("statusText");
            const btn = document.getElementById("btnToggle");
            if (currentStatus === "active") {
                badge.className = "status-badge status-active";
                text.textContent = "Active";
                if (btn) { btn.textContent = "⏸️ Pause Notifications"; btn.className = "btn btn-danger"; }
            } else {
                badge.className = "status-badge status-paused";
                text.textContent = "Paused";
                if (btn) { btn.textContent = "▶️ Resume Notifications"; btn.className = "btn btn-success"; }
            }
        }

        // ── Trigger Digest ──
        async function triggerDigest() {
            const btn = document.getElementById("btnTriggerDigest");
            btn.innerHTML = '<span class="spinner"></span> Sending...';
            btn.disabled = true;
            try {
                const res = await fetch("/api/trigger-digest");
                const data = await res.json();
                if (res.ok) { showToast(`Digest sent! ${data.jobs} jobs emailed 📧`, "success"); loadHistory(); }
                else { showToast(data.error || "Digest failed", "error"); }
            } catch (e) { showToast("Network error", "error"); }
            btn.innerHTML = "📧 Send Digest Now";
            btn.disabled = false;
        }

        // ── Trigger Scrape ──
        async function triggerScrape() {
            const btn = document.getElementById("btnScrape");
            btn.innerHTML = '<span class="spinner"></span> Scraping...';
            btn.disabled = true;
            showToast("Scraper triggered! This runs in background.", "success");
            try {
                await fetch("/api/trigger-scrape");
                loadStats();
            } catch (e) {}
            setTimeout(() => { btn.innerHTML = "🔍 Run Scraper Now"; btn.disabled = false; }, 5000);
        }

        // ── Resume Upload ──
        async function handleResumeUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) { showToast("File too large (max 5MB)", "error"); return; }

            const status = document.getElementById("resumeStatus");
            status.style.display = "block";
            status.innerHTML = '<span class="spinner"></span> Uploading and analyzing...';

            const formData = new FormData();
            formData.append("file", file);

            try {
                const res = await fetch("/api/resume", { method: "POST", body: formData });
                const data = await res.json();
                if (res.ok) {
                    status.innerHTML = `<span style="color:var(--accent-green);">✅ Resume uploaded and analyzed!</span>`;
                    showToast("Resume uploaded! Profile updated with extracted data.", "success");
                    loadProfile();
                } else {
                    status.innerHTML = `<span style="color:var(--accent-red);">❌ ${data.error || 'Upload failed'}</span>`;
                }
            } catch (e) {
                status.innerHTML = `<span style="color:var(--accent-red);">❌ Network error</span>`;
            }
        }

        // Drag & drop
        const zone = document.getElementById("uploadZone");
        if (zone) {
            zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
            zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
            zone.addEventListener("drop", e => { e.preventDefault(); zone.classList.remove("dragover");
                document.getElementById("resumeFile").files = e.dataTransfer.files;
                handleResumeUpload({target: {files: e.dataTransfer.files}});
            });
        }

        // ── Toast ──
        function showToast(msg, type) {
            const existing = document.querySelector(".toast");
            if (existing) existing.remove();
            const toast = document.createElement("div");
            toast.className = `toast toast-${type}`;
            toast.textContent = msg;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        }
    </script>
</body>
</html>
"""
