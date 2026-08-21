"""Dashboard HTML — Premium SaaS web dashboard.

Complete single-page app for managing JobScout:
- Profile management with chip selectors
- Pause/resume notifications
- Resume upload with drag-drop
- Digest history timeline
- Test email, trigger scrape, trigger digest
- Scheduler status monitoring
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobScout — Command Center</title>
    <link rel="icon" type="image/png" href="/static/weblogo.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Light Theme (Supabase Inspired) */
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-hover: #f1f5f9;
            --border: #e2e8f0;
            --border-hover: #cbd5e1;
            
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-dim: #94a3b8;
            
            --primary: #10B981;
            --primary-hover: #059669;
            --primary-glow: rgba(16, 185, 129, 0.2);
            --primary-text: #ffffff;
            --primary-border: #047857;
            
            --accent-glow: rgba(16, 185, 129, 0.15);
            
            --green-bg: rgba(16, 185, 129, 0.1);
            --green-text: #059669;
            --green-border: rgba(16, 185, 129, 0.2);
            
            --red-bg: rgba(239, 68, 68, 0.1);
            --red-text: #dc2626;
            --red-border: rgba(239, 68, 68, 0.2);
            
            --orange-bg: rgba(245, 158, 11, 0.1);
            --orange-text: #d97706;
            --orange-border: rgba(245, 158, 11, 0.2);
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
            --shadow-card: 0 2px 10px rgba(0,0,0,0.02), 0 0 1px rgba(0,0,0,0.1);
            
            --radius: 12px;
            --radius-sm: 8px;
            --radius-full: 9999px;
            
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-focus: #10B981;
            --input-focus-ring: rgba(16, 185, 129, 0.2);
        }

        [data-theme="dark"] {
            /* Dark Theme (Premium Charcoal & Red) */
            --bg-base: #09090b;
            --bg-surface: #18181b;
            --bg-surface-hover: #27272a;
            --border: rgba(255,255,255,0.08);
            --border-hover: rgba(255,255,255,0.15);
            
            --text-main: #f8fafc;
            --text-muted: #a1a1aa;
            --text-dim: #71717a;
            
            --primary: #ef4444;
            --primary-hover: #dc2626;
            --primary-glow: rgba(239, 68, 68, 0.3);
            --primary-text: #ffffff;
            --primary-border: #b91c1c;
            
            --accent-glow: rgba(239, 68, 68, 0.15);
            
            --green-bg: rgba(16, 185, 129, 0.15);
            --green-text: #34d399;
            --green-border: rgba(16, 185, 129, 0.3);
            
            --red-bg: rgba(239, 68, 68, 0.15);
            --red-text: #f87171;
            --red-border: rgba(239, 68, 68, 0.3);
            
            --orange-bg: rgba(245, 158, 11, 0.15);
            --orange-text: #fbbf24;
            --orange-border: rgba(245, 158, 11, 0.3);
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.25);
            --shadow-card: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
            
            --input-bg: #09090b;
            --input-border: #3f3f46;
            --input-focus: #ef4444;
            --input-focus-ring: rgba(239, 68, 68, 0.25);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.5;
            transition: background-color 0.3s ease, color 0.3s ease;
            -webkit-font-smoothing: antialiased;
        }

        /* ═══ Header ═══ */
        .header {
            position: sticky; top: 0; z-index: 50;
            background-color: rgba(var(--bg-surface-rgb), 0.8);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0 24px;
            height: 72px;
            display: flex; align-items: center; justify-content: center;
            background: var(--bg-surface); opacity: 0.98; backdrop-filter: none;
        }
        
        .header-content {
            width: 100%; max-width: 1200px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .brand-section { display: flex; align-items: center; gap: 16px; }
        .logo {
            width: 36px; height: 36px; border-radius: var(--radius-sm);
            object-fit: cover;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }
        .brand-text { display: flex; flex-direction: column; }
        .brand-text h1 { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; color: var(--text-main); line-height: 1.2; }
        .version { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        
        .header-actions { display: flex; align-items: center; gap: 12px; }

        /* ═══ Buttons & Controls ═══ */
        .icon-btn {
            background: var(--bg-base); border: 1px solid var(--border);
            border-radius: var(--radius-full); width: 36px; height: 36px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 16px; color: var(--text-muted);
            transition: all 0.2s ease;
        }
        .icon-btn:hover { background: var(--bg-surface-hover); color: var(--text-main); transform: scale(1.05); }

        .btn {
            padding: 8px 16px; border-radius: var(--radius-sm);
            font-size: 13px; font-weight: 600; cursor: pointer;
            transition: all 0.2s ease; border: 1px solid transparent;
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            font-family: inherit;
        }
        .btn:active { transform: translateY(1px); }
        
        .btn-primary {
            background-color: var(--primary);
            color: var(--primary-text);
            border-color: var(--primary-border);
            box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.15);
        }
        .btn-primary:hover { background-color: var(--primary-hover); box-shadow: 0 4px 12px var(--primary-glow); }
        .btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
        
        .btn-outline {
            background-color: transparent;
            color: var(--text-main);
            border-color: var(--border);
        }
        .btn-outline:hover { background-color: var(--bg-surface-hover); border-color: var(--border-hover); }

        .btn-danger-outline {
            background-color: transparent;
            color: var(--red-text);
            border-color: var(--red-border);
        }
        .btn-danger-outline:hover { background-color: var(--red-bg); }

        .status-pill {
            display: flex; align-items: center; gap: 8px;
            padding: 6px 14px; border-radius: var(--radius-full);
            font-size: 12px; font-weight: 600; cursor: pointer;
            transition: all 0.2s ease; user-select: none;
            background: var(--bg-surface); border: 1px solid var(--border);
        }
        .status-pill:hover { transform: scale(1.02); }
        .status-pill.active { background: var(--green-bg); border-color: var(--green-border); color: var(--green-text); }
        .status-pill.paused { background: var(--red-bg); border-color: var(--red-border); color: var(--red-text); }
        
        .dot { width: 8px; height: 8px; border-radius: 50%; }
        .active .dot { background: var(--green-text); box-shadow: 0 0 8px var(--green-text); }
        .paused .dot { background: var(--red-text); }

        /* ═══ Main Layout ═══ */
        .layout {
            max-width: 1200px; margin: 0 auto; padding: 32px 24px;
            display: grid; grid-template-columns: 240px 1fr; gap: 32px;
        }
        @media (max-width: 860px) {
            .layout { grid-template-columns: 1fr; }
        }

        /* ═══ Sidebar Nav ═══ */
        .sidebar { display: flex; flex-direction: column; gap: 8px; position: sticky; top: 104px; }
        .nav-item {
            padding: 10px 16px; border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 500; color: var(--text-muted);
            cursor: pointer; transition: all 0.2s ease;
            display: flex; align-items: center; gap: 12px;
            border: 1px solid transparent; background: transparent;
            text-align: left; font-family: inherit; width: 100%;
        }
        .nav-item:hover { color: var(--text-main); background: var(--bg-surface-hover); }
        .nav-item.on {
            color: var(--primary); background: var(--bg-surface);
            border-color: var(--border); box-shadow: var(--shadow-sm);
            font-weight: 600;
        }
        .nav-icon { font-size: 16px; }

        /* ═══ Main Content Area ═══ */
        .content { display: flex; flex-direction: column; gap: 24px; }
        .panel { display: none; animation: fadeIn 0.3s ease; }
        .panel.on { display: block; }
        @keyframes fadeIn { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform: translateY(0); } }

        /* ═══ Stats Header ═══ */
        .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 32px; }
        .stat-card {
            background: var(--bg-surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 20px;
            box-shadow: var(--shadow-card);
            display: flex; flex-direction: column; gap: 4px;
        }
        .stat-val { font-size: 28px; font-weight: 700; color: var(--text-main); letter-spacing: -0.5px; }
        .stat-lbl { font-size: 12px; font-weight: 500; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* ═══ Cards ═══ */
        .card {
            background: var(--bg-surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 24px;
            box-shadow: var(--shadow-card);
            margin-bottom: 24px;
        }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .card-title { font-size: 16px; font-weight: 600; color: var(--text-main); }
        .card-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.6; }

        /* ═══ Form Elements ═══ */
        .fg { margin-bottom: 20px; }
        .fl { display: block; font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 8px; }
        .fi {
            width: 100%; padding: 10px 14px;
            background: var(--input-bg); border: 1px solid var(--input-border);
            border-radius: var(--radius-sm); color: var(--text-main);
            font-size: 14px; font-family: inherit; transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }
        .fi:focus { outline: none; border-color: var(--input-focus); box-shadow: 0 0 0 3px var(--input-focus-ring); }
        .fi::placeholder { color: var(--text-dim); }

        /* ═══ Chips ═══ */
        .chips, .radios { display: flex; flex-wrap: wrap; gap: 8px; }
        .chip, .radio {
            padding: 8px 16px; border-radius: var(--radius-full);
            font-size: 13px; font-weight: 500; cursor: pointer;
            border: 1px solid var(--border); background: var(--bg-base);
            color: var(--text-muted); transition: all 0.2s ease; user-select: none;
        }
        .chip:hover, .radio:hover { border-color: var(--border-hover); color: var(--text-main); background: var(--bg-surface-hover); }
        .chip.sel, .radio.sel {
            background: var(--primary-glow); border-color: var(--primary);
            color: var(--primary); font-weight: 600;
        }

        /* ═══ Upload ═══ */
        .upload {
            border: 2px dashed var(--border); border-radius: var(--radius);
            padding: 40px 20px; text-align: center; cursor: pointer;
            transition: all 0.2s ease; background: var(--bg-base); position: relative;
        }
        .upload:hover, .upload.over { border-color: var(--primary); background: var(--primary-glow); }
        .upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
        .upload-icon { font-size: 32px; margin-bottom: 12px; }
        .upload-text { font-size: 14px; font-weight: 500; color: var(--text-main); }
        .upload-hint { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

        /* ═══ History Items ═══ */
        .hist-list { display: flex; flex-direction: column; gap: 12px; }
        .hist {
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px; border-radius: var(--radius-sm);
            border: 1px solid var(--border); background: var(--bg-base);
            transition: all 0.2s ease;
        }
        .hist:hover { border-color: var(--border-hover); transform: translateX(2px); }
        .hist-date { font-weight: 600; font-size: 14px; color: var(--text-main); }
        .hist-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
        .badge { padding: 4px 12px; border-radius: var(--radius-full); font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }
        .badge-ok { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
        .badge-wait { background: var(--orange-bg); color: var(--orange-text); border: 1px solid var(--orange-border); }

        /* ═══ Schedule Cards ═══ */
        .sched-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
        .sched {
            background: var(--bg-base); border: 1px solid var(--border);
            border-radius: var(--radius-sm); padding: 20px; text-align: center;
        }
        .sched-time { font-size: 24px; font-weight: 700; color: var(--text-main); margin: 8px 0 4px; }
        .sched-lbl { font-size: 12px; font-weight: 500; color: var(--text-muted); }

        /* ═══ Action Cards ═══ */
        .action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
        .action-card {
            background: var(--bg-surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 20px; text-align: left;
            cursor: pointer; transition: all 0.2s ease; box-shadow: var(--shadow-sm);
        }
        .action-card:hover { border-color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow-md); }
        .action-icon { font-size: 24px; margin-bottom: 12px; }
        .action-title { font-size: 14px; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }
        .action-desc { font-size: 12px; color: var(--text-muted); line-height: 1.5; }

        /* ═══ Misc ═══ */
        .toast {
            position: fixed; bottom: 24px; right: 24px; z-index: 9999;
            padding: 14px 20px; border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 500;
            animation: toastIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-lg); color: white;
        }
        .toast-ok { background: #10b981; }
        .toast-err { background: #ef4444; }
        @keyframes toastIn { from { opacity:0; transform: translateY(20px) scale(0.95); } to { opacity:1; transform: translateY(0) scale(1); } }
        
        .spin {
            width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3);
            border-top-color: currentColor; border-radius: 50%;
            animation: sp 0.6s linear infinite; display: inline-block; vertical-align: middle;
        }
        @keyframes sp { to { transform: rotate(360deg); } }
        
        .last-updated { font-size: 12px; color: var(--text-muted); text-align: right; margin-top: -20px; margin-bottom: 20px; }
    </style>
</head>
<body>

<!-- Header -->
<header class="header">
    <div class="header-content">
        <div class="brand-section">
            <img src="/static/weblogo.png" alt="JS" class="logo" onerror="this.style.display='none'">
            <div class="brand-text">
                <h1>JobScout</h1>
                <span class="version">Command Center</span>
            </div>
        </div>
        <div class="header-actions">
            <button id="themeToggle" class="icon-btn" onclick="toggleTheme()" title="Toggle Theme">
                <span id="themeIcon">🌙</span>
            </button>
            <div id="pill" class="status-pill active" onclick="toggleStatus()">
                <span class="dot"></span><span id="pillTxt">Active</span>
            </div>
            <button class="btn btn-primary" id="btnReport" onclick="sendReport(this)">
                <span class="icon">📧</span> <span class="btn-label">Send PDF Report</span>
            </button>
        </div>
    </div>
</header>

<!-- Main Layout -->
<main class="layout">
    
    <!-- Sidebar -->
    <aside class="sidebar">
        <button class="nav-item on" onclick="tab('profile',this)">
            <span class="nav-icon">👤</span> Profile
        </button>
        <button class="nav-item" onclick="tab('schedule',this)">
            <span class="nav-icon">📅</span> Schedule
        </button>
        <button class="nav-item" onclick="tab('resume',this)">
            <span class="nav-icon">📄</span> Resume
        </button>
        <button class="nav-item" onclick="tab('history',this)">
            <span class="nav-icon">📬</span> History
        </button>
        <button class="nav-item" onclick="tab('actions',this)">
            <span class="nav-icon">⚡</span> Actions
        </button>
    </aside>

    <!-- Content -->
    <div class="content">
        
        <!-- Stats Row -->
        <div class="stats-row">
            <div class="stat-card"><span class="stat-lbl">Pending Today</span><span class="stat-val" id="sP">—</span></div>
            <div class="stat-card"><span class="stat-lbl">Total Scraped</span><span class="stat-val" id="sT">—</span></div>
            <div class="stat-card"><span class="stat-lbl">Digests Sent</span><span class="stat-val" id="sD">—</span></div>
            <div class="stat-card"><span class="stat-lbl">Job Sources</span><span class="stat-val" id="sS">4</span></div>
        </div>
        <div class="last-updated" id="lastUpdated"></div>

        <!-- ═══ Profile Panel ═══ -->
        <div id="p-profile" class="panel on">
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">📧</span><h2 class="card-title">Identity</h2>
                </div>
                <div class="fg">
                    <label class="fl">Email Address</label>
                    <input class="fi" id="iEmail" type="email" placeholder="your@email.com">
                </div>
                <div class="fg">
                    <label class="fl">Qualification / Degree</label>
                    <input class="fi" id="iQual" placeholder="e.g., B.Tech, BSc, BCA, Law, MBA">
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">🎯</span><h2 class="card-title">Job Sectors</h2>
                </div>
                <p class="card-desc">Select the government sectors you're interested in.</p>
                <div class="chips" id="chipBox"></div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">💼</span><h2 class="card-title">Experience Level</h2>
                </div>
                <div class="radios" id="expBox"></div>
            </div>
            
            <div style="margin-top: 16px;">
                <button class="btn btn-primary" onclick="saveProfile()" id="btnSave">💾 Save Profile</button>
            </div>
        </div>

        <!-- ═══ Schedule Panel ═══ -->
        <div id="p-schedule" class="panel">
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">📅</span><h2 class="card-title">Digest Schedule</h2>
                </div>
                <p class="card-desc">You receive <strong>two professional PDF digests</strong> daily with all matched government jobs, delivered right to your inbox.</p>
                <div class="sched-grid">
                    <div class="sched">
                        <div style="font-size:32px;">🌅</div>
                        <div class="sched-time">10:00 AM</div>
                        <div class="sched-lbl">Morning Digest</div>
                    </div>
                    <div class="sched">
                        <div style="font-size:32px;">🌇</div>
                        <div class="sched-time">6:00 PM</div>
                        <div class="sched-lbl">Evening Digest</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">🔔</span><h2 class="card-title">Deadline Reminders</h2>
                </div>
                <p class="card-desc" style="margin-bottom:0;">Automatic reminders are sent at <strong>3 days</strong>, <strong>1 day</strong>, and the <strong>last day</strong> of application deadlines.</p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">⚙️</span><h2 class="card-title">System Status</h2>
                </div>
                <div id="schedStatus" style="font-size:14px;color:var(--text-main);">Checking...</div>
            </div>
        </div>

        <!-- ═══ Resume Panel ═══ -->
        <div id="p-resume" class="panel">
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">📄</span><h2 class="card-title">Upload Resume</h2>
                </div>
                <p class="card-desc">Upload your resume and our AI extracts your skills, qualifications, and experience to improve job matching accuracy.</p>
                <div class="upload" id="upZone">
                    <input type="file" id="upFile" accept=".pdf,.doc,.docx,.txt" onchange="uploadResume(event)">
                    <div class="upload-icon">📎</div>
                    <div class="upload-text">Drag & drop your resume or click to browse</div>
                    <div class="upload-hint">PDF, DOC, DOCX, TXT — Max 5MB</div>
                </div>
                <div id="upStatus" style="margin-top:16px;display:none;font-size:14px;"></div>
            </div>
            <div class="card" id="resumeCard" style="display:none;">
                <div class="card-header">
                    <span class="nav-icon">✅</span><h2 class="card-title">Resume on File</h2>
                </div>
                <div id="resumeInfo" style="font-size:14px;color:var(--text-main);line-height:1.6;"></div>
            </div>
        </div>

        <!-- ═══ History Panel ═══ -->
        <div id="p-history" class="panel">
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">📬</span><h2 class="card-title">Digest History</h2>
                </div>
                <div id="histList" class="hist-list">
                    <p style="color:var(--text-muted);text-align:center;padding:30px;">Loading...</p>
                </div>
            </div>
        </div>

        <!-- ═══ Actions Panel ═══ -->
        <div id="p-actions" class="panel">
            <div class="action-grid">
                <div class="action-card" onclick="testEmail(this)">
                    <div class="action-icon">📧</div>
                    <div class="action-title" id="actTest">Test Email Service</div>
                    <div class="action-desc">Send a test email to verify integration is working</div>
                </div>
                <div class="action-card" onclick="triggerDigest(this)">
                    <div class="action-icon">📄</div>
                    <div class="action-title" id="actDigest">Send Digest Now</div>
                    <div class="action-desc">Manually trigger PDF digest for pending jobs</div>
                </div>
                <div class="action-card" onclick="triggerScrape(this)">
                    <div class="action-icon">🔍</div>
                    <div class="action-title" id="actScrape">Run Scraper</div>
                    <div class="action-desc">Trigger immediate scrape of all job portals</div>
                </div>
                <div class="action-card" onclick="toggleStatus()">
                    <div class="action-icon" id="actToggleIcon">⏸️</div>
                    <div class="action-title" id="actToggle">Pause Notifications</div>
                    <div class="action-desc">Toggle notification delivery on or off</div>
                </div>
            </div>
            
            <div class="card" style="margin-top:24px;">
                <div class="card-header">
                    <span class="nav-icon">📬</span><h2 class="card-title">Brevo Email Status</h2>
                </div>
                <div id="brevoStatus" style="font-size:14px;color:var(--text-main);margin-bottom:16px;">Click to check...</div>
                <button class="btn btn-outline" onclick="verifyBrevo()">🔍 Check Connection</button>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="nav-icon">🔗</span><h2 class="card-title">Quick Links</h2>
                </div>
                <div style="display:flex;flex-direction:column;gap:12px;">
                    <a href="/health" target="_blank" style="color:var(--primary);text-decoration:none;font-weight:500;font-size:14px;">🩺 Health Check &rarr;</a>
                    <a href="/api/profile" target="_blank" style="color:var(--primary);text-decoration:none;font-weight:500;font-size:14px;">📊 Profile JSON &rarr;</a>
                    <a href="/api/digest-status" target="_blank" style="color:var(--primary);text-decoration:none;font-weight:500;font-size:14px;">📋 Digest Status &rarr;</a>
                    <a href="/api/verify-brevo" target="_blank" style="color:var(--primary);text-decoration:none;font-weight:500;font-size:14px;">📬 Brevo Diagnostics &rarr;</a>
                </div>
            </div>
        </div>
        
    </div>
</main>

<script>
// Theme Initialization
(function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if(icon) {
        icon.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
    }
}

const INTERESTS=[
    {n:"PSU",e:"🏭"},{n:"Banking",e:"🏦"},{n:"Railways",e:"🚂"},{n:"Defence",e:"🎖️"},
    {n:"IT/Software",e:"💻"},{n:"SSC",e:"📊"},{n:"UPSC",e:"🏛️"},{n:"Teaching",e:"📚"},
    {n:"State Govt",e:"🏘️"},{n:"Judiciary",e:"⚖️"},{n:"Medical",e:"🏥"}
];
const EXPS=["Fresher","0-2 yrs","2+ yrs"];
let selInt=[],selExp="Fresher",curSt="active";

document.addEventListener("DOMContentLoaded",()=>{
    updateThemeIcon();
    renderChips();renderExps();loadProfile();loadStats();loadScheduler();updateTimestamp();
});

function tab(id,el){
    document.querySelectorAll(".nav-item").forEach(t=>t.classList.remove("on"));
    document.querySelectorAll(".panel").forEach(p=>p.classList.remove("on"));
    el.classList.add("on");document.getElementById("p-"+id).classList.add("on");
    if(id==="history")loadHistory();if(id==="schedule")loadScheduler();if(id==="actions")verifyBrevo();
}

function renderChips(){
    document.getElementById("chipBox").innerHTML=INTERESTS.map(i=>
        `<div class="chip ${selInt.includes(i.n)?'sel':''}" onclick="togChip('${i.n}',this)">${i.e} ${i.n}</div>`
    ).join("");
}
function togChip(n,el){
    if(selInt.includes(n)){selInt=selInt.filter(x=>x!==n);el.classList.remove("sel");}
    else{selInt.push(n);el.classList.add("sel");}
}
function renderExps(){
    document.getElementById("expBox").innerHTML=EXPS.map(e=>
        `<div class="radio ${selExp===e?'sel':''}" onclick="selE('${e}',this)">${e}</div>`
    ).join("");
}
function selE(e,el){selExp=e;document.querySelectorAll("#expBox .radio").forEach(r=>r.classList.remove("sel"));el.classList.add("sel");}

async function safeJson(r) {
    if (!r.ok) return { _error: true, status: r.status };
    const ct = r.headers.get("content-type");
    if (ct && ct.includes("application/json")) return await r.json();
    return { _error: true, message: "Server returned non-JSON response." };
}

async function loadProfile(){
    try{
        const r=await fetch("/api/profile");
        if(!r.ok){
            if(r.status!==404) toast("Failed to load profile","err");
            return;
        }
        const p=await safeJson(r);
        if(p._error) return;
        document.getElementById("iEmail").value=p.email||"";
        document.getElementById("iQual").value=p.qualification||"";
        selInt=p.interests||[];selExp=p.experience_level||"Fresher";curSt=p.status||"active";
        renderChips();renderExps();updatePill();
        if(p.resume_url){document.getElementById("resumeCard").style.display="block";
            document.getElementById("resumeInfo").innerHTML=`<strong>📎 Resume uploaded</strong><br>Qualification: ${p.qualification||"—"}<br>Experience: ${p.experience_level||"—"}`;}
    }catch(e){console.error(e);}
}
async function loadStats(){
    try{const r=await fetch("/api/stats");if(!r.ok)return;const s=await safeJson(r);if(s._error)return;
        document.getElementById("sP").textContent=s.pending_today??0;
        document.getElementById("sT").textContent=s.total_jobs??"—";
        document.getElementById("sD").textContent=s.digests_sent??0;
        updateTimestamp();
    }catch(e){}
}
function updateTimestamp(){
    const now=new Date();
    const ts=now.toLocaleString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true,day:'2-digit',month:'short'});
    const el=document.getElementById('lastUpdated');
    if(el) el.textContent='Last refreshed: '+ts;
}
async function loadHistory(){
    try{const r=await fetch("/api/digest-history");
        if(!r.ok){document.getElementById("histList").innerHTML="<p style='color:var(--text-muted);text-align:center;padding:30px;'>No history yet.</p>";return;}
        const h=await safeJson(r);if(h._error)throw new Error("Invalid format");
        if(!h.length){document.getElementById("histList").innerHTML="<p style='color:var(--text-muted);text-align:center;padding:30px;'>No digests sent yet. Jobs are collected and emailed at 10 AM & 6 PM IST.</p>";return;}
        document.getElementById("histList").innerHTML=h.map(i=>`
            <div class="hist"><div><div class="hist-date">📧 ${i.date}</div><div class="hist-meta">${i.job_count} jobs • ${i.type||"Digest"}</div></div>
            <span class="badge ${i.sent?'badge-ok':'badge-wait'}">${i.sent?'✅ Sent':'⏳ Pending'}</span></div>`).join("");
    }catch(e){document.getElementById("histList").innerHTML="<p style='color:var(--red-text);text-align:center;'>Could not load history.</p>";}
}
async function loadScheduler(){
    try{const r=await fetch("/api/scheduler-status");const d=await safeJson(r);if(d._error)throw new Error("Format error");
        if(d.running){let html="<div style='color:var(--green-text);font-weight:600;margin-bottom:12px;'>● Running</div>";
            d.jobs.forEach(j=>{html+=`<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px;'><span>${j.name}</span><span style='color:var(--text-muted);'>${j.next_run}</span></div>`;});
            document.getElementById("schedStatus").innerHTML=html;
        }else{document.getElementById("schedStatus").innerHTML="<span style='color:var(--orange-text);'>⚠️ Scheduler not running (serverless mode)</span>";}
    }catch(e){document.getElementById("schedStatus").innerHTML="<span style='color:var(--text-muted);'>Could not fetch status</span>";}
}
async function saveProfile(){
    const e=document.getElementById("iEmail").value.trim(),q=document.getElementById("iQual").value.trim();
    if(!e||!q){toast("Email and Qualification required","err");return;}
    if(!selInt.length){toast("Select at least one interest","err");return;}
    const btn=document.getElementById("btnSave");btn.innerHTML='<span class="spin"></span> Saving...';btn.disabled=true;
    try{const r=await fetch("/api/profile",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email:e,qualification:q,interests:selInt,experience_level:selExp})});
        if(r.ok){toast("Profile saved successfully! ✅","ok");loadStats();}
        else{
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){const d=await r.json();toast(d.error||"Save failed","err");}
            else toast("Save failed (Server error)","err");
        }
    }catch(x){toast("Network error","err");}
    btn.innerHTML="💾 Save Profile";btn.disabled=false;
}
async function toggleStatus(){
    const ns=curSt==="active"?"paused":"active";
    try{const r=await fetch("/api/status",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:ns})});
        if(r.ok){curSt=ns;updatePill();toast(ns==="active"?"Notifications resumed! 🔔":"Notifications paused ⏸️","ok");}
        else toast("Failed to update status","err");
    }catch(e){toast("Failed to update","err");}
}
function updatePill(){
    const p=document.getElementById("pill"),t=document.getElementById("pillTxt");
    const ti=document.getElementById("actToggleIcon"),tt=document.getElementById("actToggle");
    if(curSt==="active"){p.className="status-pill active";t.textContent="Active";if(ti)ti.textContent="⏸️";if(tt)tt.textContent="Pause Notifications";}
    else{p.className="status-pill paused";t.textContent="Paused";if(ti)ti.textContent="▶️";if(tt)tt.textContent="Resume Notifications";}
}
async function testEmail(card){
    const t=document.getElementById("actTest");
    const orig=t.innerHTML;
    const e = document.getElementById("iEmail").value.trim();
    if(!e) { toast("Please enter an email in the Profile section first", "err"); return; }
    t.innerHTML='<span class="spin"></span> Sending...';
    try{const r=await fetch("/api/test-email?email="+encodeURIComponent(e));
        if(r.ok){const d=await safeJson(r); toast(`Test email sent to ${d.email||''}! Check your inbox 📧`,"ok");}
        else{
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){
                const d=await r.json();
                const err=d.error||"Email failed";
                if(err.includes('IP_BLOCKED')) toast('❌ IP blocked by Brevo. Disable IP restriction in Brevo dashboard.','err');
                else if(err.includes('INVALID_API_KEY')) toast('❌ Brevo API key is invalid. Update .env file.','err');
                else if(err.includes('SENDER_NOT_VERIFIED')) toast('❌ Sender email not verified in Brevo.','err');
                else if(err.includes('RATE_LIMITED')) toast('❌ Daily email limit reached (300/day). Try tomorrow.','err');
                else toast(err,'err');
            }
            else toast("Server error sending email","err");
        }
    }catch(e){toast("Network error","err");}
    t.innerHTML=orig;
}
async function verifyBrevo(){
    const el=document.getElementById('brevoStatus');
    el.innerHTML='<span class="spin"></span> Checking Brevo connection...';
    try{
        const r=await fetch('/api/verify-brevo');
        const d=await r.json();
        if(d.status==='ok'){
            el.innerHTML=`<div style='color:var(--green-text);font-weight:600;margin-bottom:8px;'>✅ Connected</div>`
                +`<div style='display:grid;gap:6px;font-size:13px;'>`
                +`<div>📧 Account: <strong>${d.account}</strong></div>`
                +`<div>📋 Plan: <strong>${d.plan}</strong> (${d.credits} emails/day)</div>`
                +`<div>✅ Sender: <strong>${d.sender_email}</strong> (verified)</div>`
                +`</div>`;
        } else {
            const err=d.error||'Unknown error';
            let hint='';
            if(err.includes('IP')) hint='<br><a href="https://app.brevo.com/security/authorised_ips" target="_blank" style="color:var(--primary);">Fix: Disable IP restriction &rarr;</a>';
            else if(err.includes('API KEY')) hint='<br>Fix: Generate new API key at Brevo dashboard';
            else if(err.includes('SENDER')) hint='<br><a href="https://app.brevo.com/senders/list" target="_blank" style="color:var(--primary);">Fix: Verify sender email &rarr;</a>';
            el.innerHTML=`<div style='color:var(--red-text);font-weight:600;margin-bottom:8px;'>❌ Error</div><div style='font-size:13px;color:var(--text-muted);word-break:break-word;'>${err}${hint}</div>`;
        }
    }catch(e){
        el.innerHTML='<span style="color:var(--red-text);">❌ Could not reach server</span>';
    }
}
async function triggerDigest(card){
    const t=document.getElementById("actDigest");
    const orig=t.innerHTML;
    t.innerHTML='<span class="spin"></span> Sending...';
    try{const r=await fetch("/api/trigger-digest");
        if(r.ok){
            const d=await safeJson(r);
            if(d.status==="skipped") toast(d.message||"No pending jobs to digest", "ok");
            else toast(`Digest sent! ${d.jobs||0} jobs emailed to ${d.email||''} 📧`,"ok");
            loadHistory();loadStats();
        }
        else{
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){const d=await r.json();toast(d.error||"Failed","err");}
            else toast("Server error generating digest","err");
        }
    }catch(e){toast("Network error","err");}
    t.innerHTML=orig;
}
async function sendReport(btn){
    btn.disabled = true;
    const origHTML=btn.innerHTML;
    btn.innerHTML='<span class="spin"></span> <span class="btn-label">Sending...</span>';
    try{const r=await fetch("/api/trigger-digest");
        if(r.ok){
            const d=await safeJson(r);
            if(d.status==="skipped"){
                toast(d.message||"No pending jobs — digest queue is empty","ok");
                btn.innerHTML='✅ <span class="btn-label">No Pending Jobs</span>';
            } else {
                toast(`PDF Report sent! ${d.jobs||0} jobs emailed to ${d.email||''} 📧`,"ok");
                btn.innerHTML='✅ <span class="btn-label">Report Sent!</span>';
            }
            loadStats();loadHistory();
        } else {
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){const d=await r.json();toast(d.error||"Send failed","err");}
            else toast("Server error sending report","err");
            btn.innerHTML='❌ <span class="btn-label">Failed</span>';
        }
    }catch(e){toast("Network error","err");btn.innerHTML='❌ <span class="btn-label">Error</span>';}
    setTimeout(()=>{btn.innerHTML=origHTML;btn.disabled=false;},3000);
}
async function triggerScrape(card){
    const t=document.getElementById("actScrape");
    const orig=t.innerHTML;
    t.innerHTML='<span class="spin"></span> Scraping...';
    try{
        const r=await fetch("/api/trigger-scrape");
        if(r.ok){toast("Scraper triggered! Running in background...","ok");loadStats();}
        else if(r.status===429){const d=await safeJson(r); toast(d.error||"Already running","err");}
        else{toast("Error triggering scraper", "err");}
    }catch(e){toast("Network error", "err");}
    setTimeout(()=>{t.innerHTML=orig;},2000);
}
async function uploadResume(ev){
    let files;
    if(ev.target&&ev.target.files) files=ev.target.files;
    else if(ev.dataTransfer&&ev.dataTransfer.files) files=ev.dataTransfer.files;
    const f=files?files[0]:null;
    if(!f)return;
    if(f.size>5*1024*1024){toast("File too large (max 5MB)","err");return;}
    const s=document.getElementById("upStatus");s.style.display="block";s.innerHTML='<span class="spin"></span> Uploading & analyzing...';
    const fd=new FormData();fd.append("file",f);
    try{const r=await fetch("/api/resume",{method:"POST",body:fd});
        if(r.ok){s.innerHTML="<span style='color:var(--green-text);'>✅ Resume uploaded & analyzed!</span>";toast("Resume uploaded! Profile updated.","ok");loadProfile();}
        else{
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){const d=await r.json();s.innerHTML=`<span style='color:var(--red-text);'>❌ ${d.error||'Failed'}</span>`;}
            else s.innerHTML=`<span style='color:var(--red-text);'>❌ Server error</span>`;
        }
    }catch(e){s.innerHTML="<span style='color:var(--red-text);'>❌ Network error</span>";}
}
const z=document.getElementById("upZone");
if(z){
    z.addEventListener("dragover",e=>{e.preventDefault();z.classList.add("over");});
    z.addEventListener("dragleave",()=>z.classList.remove("over"));
    z.addEventListener("drop",e=>{
        e.preventDefault();
        z.classList.remove("over");
        if(e.dataTransfer && e.dataTransfer.files) {
            uploadResume(e);
        }
    });
}

function toast(m,t){
    const old=document.querySelector(".toast");if(old)old.remove();
    const d=document.createElement("div");d.className=`toast toast-${t==='ok'?'ok':'err'}`;d.textContent=m;
    document.body.appendChild(d);setTimeout(()=>d.remove(),4000);
}
</script>
</body>
</html>
"""
