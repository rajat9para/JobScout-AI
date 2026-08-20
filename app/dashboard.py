"""Dashboard HTML — Premium glassmorphism dark-theme web dashboard.

Complete single-page app for managing JobScout:
- Profile management with chip selectors
- Pause/resume notifications
- Resume upload with drag-drop
- Digest history timeline
- Test email, trigger scrape, trigger digest
- Scheduler status monitoring
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobScout — Command Center</title>
    <link rel="icon" type="image/png" href="/static/weblogo.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #080816;
            --bg-glass: rgba(255, 255, 255, 0.03);
            --bg-glass-strong: rgba(12, 12, 30, 0.7);
            --bg-card: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-border-hover: rgba(255, 255, 255, 0.15);
            --glass-glow: rgba(108, 143, 255, 0.2);
            --accent: #6C8FFF;
            --accent-bright: #8BABFF;
            --accent-glow: rgba(108, 143, 255, 0.4);
            --green: #34D399;
            --green-glow: rgba(52, 211, 153, 0.3);
            --red: #F87171;
            --red-glow: rgba(248, 113, 113, 0.3);
            --orange: #FBBF24;
            --purple: #A78BFA;
            --cyan: #22D3EE;
            --text: #F8FAFC;
            --text-dim: #94A3B8;
            --text-muted: #64748B;
            --border: rgba(255, 255, 255, 0.06);
            --radius: 20px;
            --radius-sm: 12px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', -apple-system, system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ═══ Animated Background ═══ */
        .bg-orbs {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 0; overflow: hidden;
        }
        .orb {
            position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.3;
            animation: orbFloat 20s ease-in-out infinite alternate;
        }
        .orb-1 { width: 500px; height: 500px; background: #4f46e5; top: -10%; left: -5%; animation-delay: 0s; }
        .orb-2 { width: 400px; height: 400px; background: #7c3aed; bottom: -10%; right: -5%; animation-delay: -7s; }
        .orb-3 { width: 300px; height: 300px; background: #2563eb; top: 40%; left: 50%; animation-delay: -14s; }
        @keyframes orbFloat {
            0% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -40px) scale(1.1); }
            66% { transform: translate(-20px, 30px) scale(0.95); }
            100% { transform: translate(15px, -15px) scale(1.05); }
        }

        /* ═══ Header ═══ */
        .header {
            position: sticky; top: 0; z-index: 100;
            background: var(--bg-glass-strong);
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-bottom: 1px solid var(--glass-border);
            padding: 14px 28px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .header-left { display: flex; align-items: center; gap: 14px; }
        .logo {
            width: 40px; height: 40px; border-radius: var(--radius-sm);
            object-fit: cover;
            border: 2px solid var(--accent);
            box-shadow: 0 0 20px var(--accent-glow);
            transition: transform 0.3s; 
        }
        .logo:hover { transform: scale(1.1) rotate(5deg); }
        .brand { font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
        .brand span {
            background: linear-gradient(135deg, var(--accent-bright), var(--cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .version { font-size: 10px; color: var(--text-muted); font-weight: 500; letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }
        .header-right { display: flex; gap: 12px; align-items: center; }

        /* ═══ Status Pill ═══ */
        .status-pill {
            display: flex; align-items: center; gap: 8px;
            padding: 8px 18px; border-radius: 50px;
            font-size: 12px; font-weight: 700; letter-spacing: 0.5px;
            cursor: pointer; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
        }
        .status-pill.active {
            background: rgba(52, 211, 153, 0.1);
            border: 1px solid rgba(52, 211, 153, 0.3);
            color: var(--green);
            box-shadow: 0 0 20px var(--green-glow);
        }
        .status-pill.paused {
            background: rgba(248, 113, 113, 0.1);
            border: 1px solid rgba(248, 113, 113, 0.3);
            color: var(--red);
        }
        .status-pill:hover { transform: scale(1.05); }
        .dot { width: 8px; height: 8px; border-radius: 50%; }
        .active .dot { background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 2s infinite; }
        .paused .dot { background: var(--red); }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }

        /* ═══ Main Container ═══ */
        .main { position: relative; z-index: 10; max-width: 1100px; margin: 0 auto; padding: 28px 20px 80px; }

        /* ═══ Stats Row ═══ */
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }
        .stat {
            background: var(--bg-glass);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius);
            padding: 22px 20px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative; overflow: hidden;
        }
        .stat::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            opacity: 0; transition: opacity 0.4s;
        }
        .stat:hover { transform: translateY(-4px); border-color: rgba(108,143,255,0.2); }
        .stat:hover::before { opacity: 1; }
        .stat-val {
            font-size: 36px; font-weight: 900; letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent-bright), var(--cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-lbl { font-size: 11px; color: var(--text-muted); margin-top: 6px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }

        /* ═══ Tab Bar ═══ */
        .tab-bar {
            display: flex; gap: 3px;
            background: var(--bg-glass);
            backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 4px; margin-bottom: 24px;
        }
        .tab-btn {
            flex: 1; padding: 13px 10px; border-radius: 11px;
            text-align: center; font-size: 13px; font-weight: 600;
            color: var(--text-dim); cursor: pointer;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            border: none; background: none; font-family: inherit;
        }
        .tab-btn:hover { color: var(--text); background: rgba(108,143,255,0.06); }
        .tab-btn.on {
            background: linear-gradient(135deg, rgba(108,143,255,0.2), rgba(167,139,250,0.15));
            color: white; border: 1px solid rgba(108,143,255,0.3);
            box-shadow: 0 4px 16px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.05);
        }

        /* ═══ Tab Panels ═══ */
        .panel { display: none; animation: fadeUp 0.4s ease; }
        .panel.on { display: block; }
        @keyframes fadeUp { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: translateY(0); } }

        /* ═══ Glass Card ═══ */
        .glass {
            background: var(--bg-glass);
            backdrop-filter: blur(28px) saturate(180%);
            -webkit-backdrop-filter: blur(28px) saturate(180%);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius);
            padding: 28px;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative; overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        .glass::after {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent 5%, rgba(255,255,255,0.1), transparent 95%);
        }
        .glass:hover { border-color: var(--glass-border-hover); box-shadow: 0 12px 48px rgba(0,0,0,0.4); transform: translateY(-2px); }
        .glass-title {
            font-size: 15px; font-weight: 700; margin-bottom: 20px;
            display: flex; align-items: center; gap: 10px;
            letter-spacing: -0.3px;
        }

        /* ═══ Form Controls ═══ */
        .fg { margin-bottom: 22px; }
        .fl { display: block; font-size: 11px; font-weight: 700; color: var(--text-dim); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .fi {
            width: 100%; padding: 13px 18px;
            background: rgba(255,255,255,0.03);
            border: 1.5px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text); font-size: 14px; font-family: inherit;
            transition: all 0.3s; outline: none;
        }
        .fi:focus { border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-glow); background: rgba(108,143,255,0.03); }
        .fi::placeholder { color: var(--text-muted); }

        /* ═══ Chips ═══ */
        .chips { display: flex; flex-wrap: wrap; gap: 10px; }
        .chip {
            padding: 10px 18px; border-radius: 50px;
            font-size: 13px; font-weight: 500; cursor: pointer;
            border: 1.5px solid var(--border);
            background: rgba(255,255,255,0.02);
            color: var(--text-dim);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
        }
        .chip:hover { border-color: var(--accent); color: var(--text); transform: translateY(-1px); }
        .chip.sel {
            background: linear-gradient(135deg, rgba(108,143,255,0.15), rgba(167,139,250,0.1));
            border-color: var(--accent); color: var(--accent-bright); font-weight: 700;
            box-shadow: 0 0 16px rgba(108,143,255,0.15);
        }

        /* ═══ Radio Options ═══ */
        .radios { display: flex; gap: 10px; flex-wrap: wrap; }
        .radio {
            padding: 11px 22px; border-radius: var(--radius-sm);
            font-size: 13px; font-weight: 500; cursor: pointer;
            border: 1.5px solid var(--border);
            background: rgba(255,255,255,0.02);
            color: var(--text-dim); transition: all 0.3s;
        }
        .radio:hover { border-color: var(--accent); }
        .radio.sel {
            background: rgba(108,143,255,0.12); border-color: var(--accent);
            color: var(--accent-bright); font-weight: 700;
        }

        /* ═══ Buttons ═══ */
        .btn {
            padding: 13px 28px; border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 700; cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none; font-family: inherit;
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            letter-spacing: 0.3px; position: relative; overflow: hidden;
        }
        .btn:active { transform: scale(0.96); }
        .btn::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
            transition: left 0.5s;
        }
        .btn:hover::before { left: 100%; }
        .btn-primary {
            background: linear-gradient(135deg, #5B7FFF, #7C5CFC);
            color: white;
            box-shadow: 0 4px 16px rgba(91,127,255,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(91,127,255,0.4); }
        .btn-primary:active { transform: translateY(0); }
        .btn-green {
            background: linear-gradient(135deg, #059669, #10B981);
            color: white;
            box-shadow: 0 4px 16px rgba(5,150,105,0.3);
        }
        .btn-green:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(5,150,105,0.4); }
        .btn-outline {
            background: transparent;
            color: var(--accent-bright);
            border: 1.5px solid rgba(108,143,255,0.3);
        }
        .btn-outline:hover { background: rgba(108,143,255,0.08); transform: translateY(-2px); }
        .btn-ghost {
            background: rgba(248,113,113,0.08);
            color: var(--red);
            border: 1.5px solid rgba(248,113,113,0.2);
        }
        .btn-ghost:hover { background: rgba(248,113,113,0.15); transform: translateY(-2px); }
        .btn-amber {
            background: linear-gradient(135deg, #D97706, #F59E0B);
            color: #1a1a2e;
            box-shadow: 0 4px 16px rgba(217,119,6,0.3);
        }
        .btn-amber:hover { transform: translateY(-2px); }
        .btn-group { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 20px; }
        .btn-stack { display: flex; flex-direction: column; gap: 12px; }

        /* ═══ Upload Zone ═══ */
        .upload {
            border: 2px dashed rgba(108,143,255,0.2); border-radius: var(--radius);
            padding: 44px 20px; text-align: center; cursor: pointer;
            transition: all 0.4s; position: relative;
            background: rgba(108,143,255,0.02);
        }
        .upload:hover, .upload.over { border-color: var(--accent); background: rgba(108,143,255,0.06); }
        .upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
        .upload-icon { font-size: 44px; margin-bottom: 14px; filter: drop-shadow(0 4px 12px rgba(108,143,255,0.3)); }
        .upload-text { font-size: 14px; color: var(--text-dim); }
        .upload-hint { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

        /* ═══ History Items ═══ */
        .hist {
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 20px; border-radius: 12px;
            border: 1px solid var(--border); margin-bottom: 10px;
            transition: all 0.3s;
            background: rgba(255,255,255,0.01);
        }
        .hist:hover { border-color: rgba(108,143,255,0.2); background: rgba(108,143,255,0.03); transform: translateX(4px); }
        .hist-date { font-weight: 700; font-size: 14px; }
        .hist-meta { font-size: 12px; color: var(--text-dim); margin-top: 4px; }
        .badge { padding: 5px 14px; border-radius: 50px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
        .badge-ok { background: rgba(52,211,153,0.12); color: var(--green); }
        .badge-wait { background: rgba(251,191,36,0.12); color: var(--orange); }

        /* ═══ Schedule Cards ═══ */
        .sched-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 16px; }
        .sched {
            background: linear-gradient(135deg, rgba(108,143,255,0.06), rgba(167,139,250,0.04));
            border: 1px solid rgba(108,143,255,0.15);
            border-radius: 14px; padding: 24px; text-align: center;
            transition: transform 0.3s;
        }
        .sched:hover { transform: scale(1.02); }
        .sched-time {
            font-size: 32px; font-weight: 900; letter-spacing: -1px;
            background: linear-gradient(135deg, var(--accent-bright), var(--cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .sched-lbl { font-size: 11px; color: var(--text-dim); margin-top: 8px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }

        /* ═══ Action Cards ═══ */
        .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .action-card {
            background: var(--bg-glass);
            backdrop-filter: blur(28px) saturate(180%);
            -webkit-backdrop-filter: blur(28px) saturate(180%);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius);
            padding: 24px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .action-card:hover { border-color: var(--accent); transform: translateY(-4px) scale(1.02); box-shadow: 0 16px 40px rgba(0,0,0,0.4); }
        .action-card:active { transform: translateY(0) scale(0.98); }
        .action-icon { font-size: 32px; margin-bottom: 12px; transition: transform 0.3s; }
        .action-card:hover .action-icon { transform: scale(1.1) rotate(5deg); }
        .action-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
        .action-desc { font-size: 12px; color: var(--text-dim); line-height: 1.5; }

        /* ═══ Toast ═══ */
        .toast {
            position: fixed; bottom: 28px; right: 28px; z-index: 9999;
            padding: 16px 26px; border-radius: 14px;
            font-size: 14px; font-weight: 600;
            backdrop-filter: blur(20px);
            animation: toastIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }
        .toast-ok { background: rgba(5,150,105,0.9); color: white; }
        .toast-err { background: rgba(220,38,38,0.9); color: white; }
        @keyframes toastIn { from { opacity:0; transform: translateY(20px) scale(0.95); } to { opacity:1; transform: translateY(0) scale(1); } }

        /* ═══ Spinner ═══ */
        .spin { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,0.2); border-top-color: white; border-radius: 50%; animation: sp 0.5s linear infinite; display: inline-block; vertical-align: middle; }
        @keyframes sp { to { transform: rotate(360deg); } }

        /* ═══ Send PDF Report Button (Header) ═══ */
        .btn-send-report {
            padding: 10px 22px; border-radius: 50px;
            font-size: 13px; font-weight: 700; cursor: pointer;
            border: none; font-family: inherit;
            display: inline-flex; align-items: center; gap: 8px;
            background: linear-gradient(135deg, #10B981, #059669);
            color: white;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.4), 0 4px 16px rgba(5, 150, 105, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: reportGlow 3s ease-in-out infinite alternate;
            letter-spacing: 0.3px;
            position: relative; overflow: hidden;
            white-space: nowrap;
        }
        .btn-send-report:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.6), 0 8px 28px rgba(5, 150, 105, 0.4);
        }
        .btn-send-report:active { transform: translateY(0) scale(0.97); }
        .btn-send-report::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s;
        }
        .btn-send-report:hover::before { left: 100%; }
        .btn-send-report.sending {
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
            animation: none;
            pointer-events: none;
        }
        @keyframes reportGlow {
            0% { box-shadow: 0 0 15px rgba(16, 185, 129, 0.3), 0 4px 16px rgba(5, 150, 105, 0.2); }
            100% { box-shadow: 0 0 25px rgba(16, 185, 129, 0.5), 0 4px 20px rgba(5, 150, 105, 0.35); }
        }

        /* ═══ Last Updated ═══ */
        .last-updated {
            text-align: center; font-size: 11px; color: var(--text-muted);
            margin-bottom: 16px; letter-spacing: 0.5px;
        }

        /* ═══ Responsive ═══ */
        @media (max-width: 768px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            .tab-bar { flex-wrap: wrap; }
            .sched-grid, .action-grid { grid-template-columns: 1fr; }
            .header { padding: 12px 16px; flex-wrap: wrap; gap: 10px; }
            .main { padding: 16px 12px 60px; }
            .btn-send-report { font-size: 12px; padding: 8px 16px; }
        }
        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr 1fr; }
            .stat-val { font-size: 28px; }
            .btn-send-report span.btn-label { display: none; }
        }
    </style>
</head>
<body>
<div class="bg-orbs"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>

<!-- Header -->
<header class="header">
    <div class="header-left">
        <img src="/static/weblogo.png" alt="JS" class="logo" onerror="this.style.display='none'">
        <div><div class="brand"><span>JobScout</span></div><div class="version">v2.2 • Command Center</div></div>
    </div>
    <div class="header-right">
        <button class="btn-send-report" id="btnReport" onclick="sendReport(this)">
            📧 <span class="btn-label">Send PDF Report</span>
        </button>
        <div id="pill" class="status-pill active" onclick="toggleStatus()"><span class="dot"></span><span id="pillTxt">Active</span></div>
    </div>
</header>

<!-- Main -->
<main class="main">
    <!-- Stats -->
    <div class="stats">
        <div class="stat"><div class="stat-val" id="sP">—</div><div class="stat-lbl">Pending Today</div></div>
        <div class="stat"><div class="stat-val" id="sT">—</div><div class="stat-lbl">Total Scraped</div></div>
        <div class="stat"><div class="stat-val" id="sD">—</div><div class="stat-lbl">Digests Sent</div></div>
        <div class="stat"><div class="stat-val" id="sS">4</div><div class="stat-lbl">Job Sources</div></div>
    </div>
    <div class="last-updated" id="lastUpdated"></div>

    <!-- Tabs -->
    <div class="tab-bar">
        <button class="tab-btn on" onclick="tab('profile',this)">👤 Profile</button>
        <button class="tab-btn" onclick="tab('schedule',this)">📅 Schedule</button>
        <button class="tab-btn" onclick="tab('resume',this)">📄 Resume</button>
        <button class="tab-btn" onclick="tab('history',this)">📬 History</button>
        <button class="tab-btn" onclick="tab('actions',this)">⚡ Actions</button>
    </div>

    <!-- ═══ Profile Panel ═══ -->
    <div id="p-profile" class="panel on">
        <div class="glass">
            <div class="glass-title">📧 Identity</div>
            <div class="fg"><label class="fl">Email Address</label><input class="fi" id="iEmail" type="email" placeholder="your@email.com"></div>
            <div class="fg"><label class="fl">Qualification / Degree</label><input class="fi" id="iQual" placeholder="e.g., B.Tech, BSc, BCA, Law, MBA"></div>
        </div>
        <div class="glass">
            <div class="glass-title">🎯 Job Sectors</div>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:14px;">Select sectors you're interested in</p>
            <div class="chips" id="chipBox"></div>
        </div>
        <div class="glass">
            <div class="glass-title">💼 Experience</div>
            <div class="radios" id="expBox"></div>
        </div>
        <div class="btn-group">
            <button class="btn btn-primary" onclick="saveProfile()" id="btnSave">💾 Save Profile</button>
        </div>
    </div>

    <!-- ═══ Schedule Panel ═══ -->
    <div id="p-schedule" class="panel">
        <div class="glass">
            <div class="glass-title">📅 Digest Schedule</div>
            <p style="color:var(--text-dim);font-size:14px;line-height:1.7;margin-bottom:8px;">You receive <strong>two professional PDF digests</strong> daily with all matched government jobs, delivered right to your inbox.</p>
            <div class="sched-grid">
                <div class="sched"><div style="font-size:28px;margin-bottom:8px;">🌅</div><div class="sched-time">10:00 AM</div><div class="sched-lbl">Morning Digest</div></div>
                <div class="sched"><div style="font-size:28px;margin-bottom:8px;">🌇</div><div class="sched-time">6:00 PM</div><div class="sched-lbl">Evening Digest</div></div>
            </div>
        </div>
        <div class="glass">
            <div class="glass-title">🔔 Deadline Reminders</div>
            <p style="color:var(--text-dim);font-size:14px;line-height:1.7;">Automatic reminders at <strong>3 days</strong>, <strong>1 day</strong>, and <strong>last day</strong> of application deadlines.</p>
        </div>
        <div class="glass">
            <div class="glass-title">💓 Database Keep-Alive</div>
            <p style="color:var(--text-dim);font-size:14px;line-height:1.7;">Supabase free-tier databases sleep after 7 days of inactivity. JobScout automatically <strong>pings all 3 tables every 8 hours</strong> (3× daily) to keep your database alive 24/7.</p>
        </div>
        <div class="glass">
            <div class="glass-title">⚙️ Scheduler Status</div>
            <div id="schedStatus" style="font-size:13px;color:var(--text-dim);">Checking...</div>
        </div>
    </div>

    <!-- ═══ Resume Panel ═══ -->
    <div id="p-resume" class="panel">
        <div class="glass">
            <div class="glass-title">📄 Upload Resume</div>
            <p style="color:var(--text-dim);font-size:14px;margin-bottom:20px;line-height:1.6;">Upload your resume and our AI extracts your skills, qualifications, and experience to improve job matching accuracy.</p>
            <div class="upload" id="upZone">
                <input type="file" id="upFile" accept=".pdf,.doc,.docx,.txt" onchange="uploadResume(event)">
                <div class="upload-icon">📎</div>
                <div class="upload-text">Drag & drop your resume or click to browse</div>
                <div class="upload-hint">PDF, DOC, DOCX, TXT — Max 5MB</div>
            </div>
            <div id="upStatus" style="margin-top:16px;display:none;"></div>
        </div>
        <div class="glass" id="resumeCard" style="display:none;">
            <div class="glass-title">✅ Resume on File</div>
            <div id="resumeInfo" style="font-size:14px;color:var(--text-dim);line-height:1.8;"></div>
        </div>
    </div>

    <!-- ═══ History Panel ═══ -->
    <div id="p-history" class="panel">
        <div class="glass">
            <div class="glass-title">📬 Digest History</div>
            <div id="histList"><p style="color:var(--text-muted);text-align:center;padding:30px;">Loading...</p></div>
        </div>
    </div>

    <!-- ═══ Actions Panel ═══ -->
    <div id="p-actions" class="panel">
        <div class="action-grid">
            <div class="action-card" onclick="testEmail(this)">
                <div class="action-icon">📧</div>
                <div class="action-title" id="actTest">Test Email Service</div>
                <div class="action-desc">Send a test email to verify Brevo integration is working</div>
            </div>
            <div class="action-card" onclick="triggerDigest(this)">
                <div class="action-icon">📄</div>
                <div class="action-title" id="actDigest">Send Digest Now</div>
                <div class="action-desc">Manually trigger PDF digest for all pending jobs</div>
            </div>
            <div class="action-card" onclick="triggerScrape(this)">
                <div class="action-icon">🔍</div>
                <div class="action-title" id="actScrape">Run Scraper</div>
                <div class="action-desc">Trigger immediate scrape of all 4 job portals</div>
            </div>
            <div class="action-card" onclick="toggleStatus()">
                <div class="action-icon" id="actToggleIcon">⏸️</div>
                <div class="action-title" id="actToggle">Pause Notifications</div>
                <div class="action-desc">Toggle notification delivery on/off</div>
            </div>
        </div>
        <div class="glass" style="margin-top:18px;">
            <div class="glass-title">📬 Brevo Email Status</div>
            <div id="brevoStatus" style="font-size:13px;color:var(--text-dim);">Click to check...</div>
            <button class="btn btn-outline" style="margin-top:14px;" onclick="verifyBrevo()">🔍 Check Brevo Connection</button>
        </div>
        <div class="glass" style="margin-top:18px;">
            <div class="glass-title">🔗 Quick Links</div>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <a href="/health" target="_blank" style="color:var(--accent-bright);text-decoration:none;font-size:14px;transition:color 0.2s;">🩺 Health Check →</a>
                <a href="/api/profile" target="_blank" style="color:var(--accent-bright);text-decoration:none;font-size:14px;">📊 Profile JSON →</a>
                <a href="/api/digest-status" target="_blank" style="color:var(--accent-bright);text-decoration:none;font-size:14px;">📋 Digest Status →</a>
                <a href="/api/verify-brevo" target="_blank" style="color:var(--accent-bright);text-decoration:none;font-size:14px;">📬 Brevo Diagnostics →</a>
                <a href="/api/scheduler-status" target="_blank" style="color:var(--accent-bright);text-decoration:none;font-size:14px;">⚙️ Scheduler Status →</a>
            </div>
        </div>
    </div>
</main>

<script>
const INTERESTS=[
    {n:"PSU",e:"🏭"},{n:"Banking",e:"🏦"},{n:"Railways",e:"🚂"},{n:"Defence",e:"🎖️"},
    {n:"IT/Software",e:"💻"},{n:"SSC",e:"📊"},{n:"UPSC",e:"🏛️"},{n:"Teaching",e:"📚"},
    {n:"State Govt",e:"🏘️"},{n:"Judiciary",e:"⚖️"},{n:"Medical",e:"🏥"}
];
const EXPS=["Fresher","0-2 yrs","2+ yrs"];
let selInt=[],selExp="Fresher",curSt="active";

document.addEventListener("DOMContentLoaded",()=>{renderChips();renderExps();loadProfile();loadStats();loadScheduler();updateTimestamp();});

function tab(id,el){
    document.querySelectorAll(".tab-btn").forEach(t=>t.classList.remove("on"));
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
    }catch(e){document.getElementById("histList").innerHTML="<p style='color:var(--text-muted);text-align:center;'>Could not load history.</p>";}
}
async function loadScheduler(){
    try{const r=await fetch("/api/scheduler-status");const d=await safeJson(r);if(d._error)throw new Error("Format error");
        if(d.running){let html="<div style='color:var(--green);font-weight:600;margin-bottom:12px;'>● Running</div>";
            d.jobs.forEach(j=>{html+=`<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px;'><span>${j.name}</span><span style='color:var(--text-muted);'>${j.next_run}</span></div>`;});
            document.getElementById("schedStatus").innerHTML=html;
        }else{document.getElementById("schedStatus").innerHTML="<span style='color:var(--orange);'>⚠️ Scheduler not running (serverless mode on Vercel)</span>";}
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
                // Show user-friendly error based on error type
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
            el.innerHTML=`<div style='color:var(--green);font-weight:600;margin-bottom:8px;'>✅ Connected</div>`
                +`<div style='display:grid;gap:6px;font-size:12px;'>`
                +`<div>📧 Account: <strong>${d.account}</strong></div>`
                +`<div>📋 Plan: <strong>${d.plan}</strong> (${d.credits} emails/day)</div>`
                +`<div>✅ Sender: <strong>${d.sender_email}</strong> (verified)</div>`
                +`</div>`;
        } else {
            const err=d.error||'Unknown error';
            let hint='';
            if(err.includes('IP')) hint='<br><a href="https://app.brevo.com/security/authorised_ips" target="_blank" style="color:var(--accent-bright);">Fix: Disable IP restriction →</a>';
            else if(err.includes('API KEY')) hint='<br>Fix: Generate new API key at Brevo dashboard';
            else if(err.includes('SENDER')) hint='<br><a href="https://app.brevo.com/senders/list" target="_blank" style="color:var(--accent-bright);">Fix: Verify sender email →</a>';
            el.innerHTML=`<div style='color:var(--red);font-weight:600;margin-bottom:8px;'>❌ Error</div><div style='font-size:12px;color:var(--text-dim);word-break:break-word;'>${err}${hint}</div>`;
        }
    }catch(e){
        el.innerHTML='<span style="color:var(--red);">❌ Could not reach server</span>';
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
    btn.classList.add('sending');
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
    setTimeout(()=>{btn.innerHTML=origHTML;btn.classList.remove('sending');},3000);
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
        if(r.ok){s.innerHTML="<span style='color:var(--green);'>✅ Resume uploaded & analyzed!</span>";toast("Resume uploaded! Profile updated.","ok");loadProfile();}
        else{
            const ct=r.headers.get("content-type");
            if(ct&&ct.includes("application/json")){const d=await r.json();s.innerHTML=`<span style='color:var(--red);'>❌ ${d.error||'Failed'}</span>`;}
            else s.innerHTML=`<span style='color:var(--red);'>❌ Server error</span>`;
        }
    }catch(e){s.innerHTML="<span style='color:var(--red);'>❌ Network error</span>";}
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
