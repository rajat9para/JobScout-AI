"""Dashboard HTML — Ultra-Premium Glassmorphism Web Dashboard with Running Train Ticker & AI Job Intelligence.

Features:
- Animated Running Train Ticker (gliding smoothly from right to left with live sarkari updates)
- Interactive Ranked Sector Preferences (drag/re-order 1> Defence, 2> State PSC, 3> Banking...)
- Groq Agent #1 & Agent #2 AI Job Intelligence & Reality Check subsystem
- Deep Evidence-based Reality Scores, Interview Intelligence, and Transparent Source Citations
- Crystal-clear glassmorphism aesthetic with backdrop-filter blur + neon glow borders
- Animated stat counters, floating particles, detail modals, and fluid transitions
"""

DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobScout-AI — Government Job Intelligence & Reality Command Center</title>
    <meta name="description" content="JobScout-AI: Autonomous Sarkari Naukri Intelligence & Workplace Reality Engine powered by Groq LPU AI">
    <link rel="icon" type="image/png" href="/static/weblogo.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        /* ═══════════════════════════════════════════════
           DESIGN TOKENS & PALETTE
           ═══════════════════════════════════════════════ */
        :root {
            --font-heading: 'Outfit', 'Inter', sans-serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --radius: 18px;
            --radius-sm: 12px;
            --radius-xs: 8px;
            --radius-full: 9999px;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --spring: 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        [data-theme="dark"] {
            --bg-base: #060814;
            --bg-mesh-1: #0b0f29;
            --bg-mesh-2: #190a36;
            --bg-mesh-3: #081a2f;
            --bg-surface: rgba(255, 255, 255, 0.03);
            --bg-surface-hover: rgba(255, 255, 255, 0.07);
            --bg-glass: rgba(13, 17, 38, 0.7);
            --bg-glass-strong: rgba(13, 17, 38, 0.9);

            --border-glass: rgba(255, 255, 255, 0.08);
            --border-glass-hover: rgba(139, 92, 246, 0.35);
            --border-glow: rgba(139, 92, 246, 0.4);

            --text-main: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --text-dim: #475569;

            --primary: #8b5cf6;
            --primary-hover: #a78bfa;
            --primary-glow: rgba(139, 92, 246, 0.45);
            --primary-soft: rgba(139, 92, 246, 0.12);

            --cyan: #06b6d4;
            --cyan-glow: rgba(6, 182, 212, 0.35);
            --cyan-soft: rgba(6, 182, 212, 0.1);

            --green: #10b981;
            --green-glow: rgba(16, 185, 129, 0.35);
            --green-soft: rgba(16, 185, 129, 0.12);

            --red: #f43f5e;
            --red-soft: rgba(244, 63, 94, 0.12);

            --amber: #f59e0b;
            --amber-soft: rgba(245, 158, 11, 0.12);

            --shadow-glass: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            --shadow-glow: 0 0 50px rgba(139, 92, 246, 0.18);
            --shadow-btn: 0 4px 20px rgba(139, 92, 246, 0.35);

            --input-bg: rgba(255, 255, 255, 0.04);
            --input-border: rgba(255, 255, 255, 0.1);
        }

        [data-theme="light"] {
            --bg-base: #f1f5f9;
            --bg-mesh-1: #e2e8f0;
            --bg-mesh-2: #ede9fe;
            --bg-mesh-3: #e0f2fe;
            --bg-surface: rgba(255, 255, 255, 0.7);
            --bg-surface-hover: rgba(255, 255, 255, 0.9);
            --bg-glass: rgba(255, 255, 255, 0.75);
            --bg-glass-strong: rgba(255, 255, 255, 0.95);

            --border-glass: rgba(0, 0, 0, 0.08);
            --border-glass-hover: rgba(124, 58, 237, 0.3);
            --border-glow: rgba(124, 58, 237, 0.25);

            --text-main: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-dim: #94a3b8;

            --primary: #7c3aed;
            --primary-hover: #6d28d9;
            --primary-glow: rgba(124, 58, 237, 0.3);
            --primary-soft: rgba(124, 58, 237, 0.08);

            --cyan: #0891b2;
            --cyan-glow: rgba(8, 145, 178, 0.25);
            --cyan-soft: rgba(8, 145, 178, 0.08);

            --green: #059669;
            --green-glow: rgba(5, 150, 105, 0.25);
            --green-soft: rgba(5, 150, 105, 0.08);

            --red: #dc2626;
            --red-soft: rgba(220, 38, 38, 0.08);

            --amber: #d97706;
            --amber-soft: rgba(217, 119, 6, 0.08);

            --shadow-glass: 0 10px 40px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8);
            --shadow-glow: 0 0 40px rgba(124, 58, 237, 0.1);
            --shadow-btn: 0 4px 20px rgba(124, 58, 237, 0.25);

            --input-bg: rgba(255, 255, 255, 0.9);
            --input-border: rgba(0, 0, 0, 0.12);
        }

        * { margin:0; padding:0; box-sizing:border-box; }

        body {
            font-family: var(--font-body);
            background: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            transition: background var(--transition), color var(--transition);
        }

        .mesh-bg {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }
        .mesh-orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.6;
            animation: orbFloat 25s ease-in-out infinite alternate;
        }
        .orb-1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%); top: -100px; left: -100px; }
        .orb-2 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%); bottom: -150px; right: -150px; animation-delay: -7s; }
        .orb-3 { width: 450px; height: 450px; background: radial-gradient(circle, rgba(244,63,94,0.15) 0%, transparent 70%); top: 40%; left: 40%; animation-delay: -14s; }

        @keyframes orbFloat {
            0% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(60px, -40px) scale(1.1); }
            100% { transform: translate(-40px, 60px) scale(0.95); }
        }

        /* ═══════════════════════════════════════════════
           RUNNING TRAIN TICKER (RIGHT TO LEFT)
           ═══════════════════════════════════════════════ */
        .train-ticker-wrap {
            position: relative;
            z-index: 10;
            background: linear-gradient(90deg, rgba(13,17,38,0.95), rgba(25,10,54,0.95), rgba(13,17,38,0.95));
            border-bottom: 1px solid var(--border-glass);
            padding: 8px 0;
            overflow: hidden;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .train-badge {
            background: var(--primary);
            color: #fff;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 12px;
            border-radius: var(--radius-full);
            margin: 0 16px;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 0 15px var(--primary-glow);
            z-index: 2;
        }
        .train-track {
            display: flex;
            width: 100%;
            overflow: hidden;
            position: relative;
        }
        .train-content {
            display: flex;
            align-items: center;
            gap: 40px;
            white-space: nowrap;
            animation: trainGlide 30s linear infinite;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
        }
        .train-content:hover { animation-play-state: paused; }
        .train-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .train-item strong { color: var(--cyan); }
        .train-item span.hot {
            background: rgba(244,63,94,0.2);
            color: var(--red);
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
        }

        @keyframes trainGlide {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        /* ═══════════════════════════════════════════════
           LAYOUT & HEADER
           ═══════════════════════════════════════════════ */
        .wrapper {
            position: relative;
            z-index: 5;
            max-width: 1240px;
            margin: 0 auto;
            padding: 24px 20px 60px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 16px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .brand-logo {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--primary), var(--cyan));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 0 25px var(--primary-glow);
        }
        .brand-title {
            font-family: var(--font-heading);
            font-size: 24px;
            font-weight: 900;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, var(--text-main) 30%, var(--primary-hover) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .groq-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            padding: 6px 14px;
            border-radius: var(--radius-full);
            font-size: 12px;
            font-weight: 600;
            color: var(--primary-hover);
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 10px var(--green);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        .btn-icon {
            width: 40px;
            height: 40px;
            border-radius: var(--radius-sm);
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            backdrop-filter: blur(16px);
            transition: all var(--transition);
        }
        .btn-icon:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        /* ═══════════════════════════════════════════════
           GLASS CARDS & STATS
           ═══════════════════════════════════════════════ */
        .glass {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius);
            box-shadow: var(--shadow-glass);
            transition: all var(--transition);
        }
        .glass:hover {
            border-color: var(--border-glass-hover);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }
        .stat-card {
            padding: 22px 24px;
            position: relative;
            overflow: hidden;
        }
        .stat-card::after {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 80px; height: 80px;
            background: radial-gradient(circle, var(--primary-soft), transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .stat-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
        }
        .stat-icon { font-size: 20px; }
        .stat-val {
            font-family: var(--font-heading);
            font-size: 36px;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -1px;
        }
        .stat-sub { font-size: 11px; color: var(--text-dim); margin-top: 4px; }

        /* ═══════════════════════════════════════════════
           NAV TABS
           ═══════════════════════════════════════════════ */
        .nav-tabs {
            display: flex;
            gap: 8px;
            background: var(--bg-surface);
            padding: 6px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-glass);
            margin-bottom: 24px;
            overflow-x: auto;
        }
        .tab-btn {
            padding: 10px 18px;
            border-radius: var(--radius-xs);
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-family: var(--font-body);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all var(--transition);
            white-space: nowrap;
        }
        .tab-btn:hover { color: var(--text-main); background: var(--bg-surface-hover); }
        .tab-btn.active {
            background: var(--primary);
            color: #fff;
            box-shadow: 0 2px 12px var(--primary-glow);
        }

        .panel { display: none; }
        .panel.active { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        /* ═══════════════════════════════════════════════
           AI JOB INTELLIGENCE & REALITY STYLING
           ═══════════════════════════════════════════════ */
        .intel-hero {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            border-left: 4px solid var(--cyan);
        }
        .intel-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .intel-card {
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 16px;
            position: relative;
            transition: all var(--transition);
        }
        .intel-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-glow);
            box-shadow: 0 12px 35px rgba(0,0,0,0.4);
        }
        .intel-card-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
        }
        .score-pill-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .score-badge {
            font-size: 11px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: var(--radius-full);
            color: #fff;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .score-match { background: linear-gradient(135deg, #2563eb, #3b82f6); }
        .score-reality { background: linear-gradient(135deg, #059669, #10b981); }
        .score-rec { background: rgba(139, 92, 246, 0.2); color: var(--primary-hover); border: 1px solid rgba(139, 92, 246, 0.4); }

        .progress-bar-wrap {
            margin-top: 6px;
            margin-bottom: 12px;
        }
        .bar-label {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }
        .bar-bg {
            height: 6px;
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--cyan), var(--primary));
            transition: width 0.6s ease;
        }

        /* ── Intelligence Modal ── */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.75);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; animation: fadeIn 0.25s ease; }
        .modal-content {
            background: var(--bg-base);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius);
            max-width: 800px;
            width: 100%;
            max-height: 88vh;
            overflow-y: auto;
            padding: 32px;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        }
        .modal-close {
            position: absolute;
            top: 20px; right: 20px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border-glass);
            color: var(--text-muted);
            border-radius: 50%;
            width: 32px; height: 32px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 14px;
        }
        .modal-close:hover { color: #fff; background: var(--red); }

        /* ── Progress / Loading State ── */
        .loading-box {
            display: none;
            padding: 30px;
            text-align: center;
            border: 1px dashed var(--cyan);
            border-radius: var(--radius);
            margin-bottom: 24px;
            background: rgba(6, 182, 212, 0.05);
        }
        .spinner {
            width: 40px; height: 40px;
            border: 4px solid rgba(6,182,212,0.2);
            border-top: 4px solid var(--cyan);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* ═══════════════════════════════════════════════
           BUTTONS & CHIPS
           ═══════════════════════════════════════════════ */
        .btn {
            padding: 12px 24px;
            border-radius: var(--radius-sm);
            font-family: var(--font-body);
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all var(--transition);
            border: none;
            text-decoration: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), #6366f1);
            color: #fff;
            box-shadow: var(--shadow-btn);
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(139,92,246,0.5); }
        .btn-cyan {
            background: linear-gradient(135deg, #0891b2, #06b6d4);
            color: #fff;
            box-shadow: 0 4px 15px var(--cyan-glow);
        }
        .btn-cyan:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(6,182,212,0.5); }
        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-glass);
            color: var(--text-main);
        }
        .btn-outline:hover { border-color: var(--primary); background: var(--bg-surface-hover); }

        .chip {
            padding: 8px 14px;
            border-radius: var(--radius-full);
            background: var(--bg-surface);
            border: 1px solid var(--border-glass);
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all var(--transition);
        }
        .chip:hover { border-color: var(--primary); background: var(--bg-surface-hover); transform: translateY(-1px); }
        .chip.selected { background: var(--primary-soft); border-color: var(--primary); color: var(--primary-hover); font-weight: 700; }

        /* ── Ranked Sector List ── */
        .ranked-item {
            display: flex; align-items: center; justify-content: space-between;
            background: var(--bg-surface); border: 1px solid var(--border-glass);
            padding: 12px 16px; border-radius: var(--radius-sm); margin-bottom: 8px;
        }
        .rank-num {
            width: 26px; height: 26px; border-radius: 50%;
            background: var(--primary-soft); color: var(--primary-hover);
            border: 1px solid rgba(139,92,246,0.3);
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 800;
        }
        .btn-arrow {
            background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass);
            color: var(--text-muted); border-radius: 6px; width: 28px; height: 28px;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
        }
        .btn-arrow:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

        /* ── Toast ── */
        .toast-wrap { position: fixed; bottom: 24px; right: 24px; z-index: 1000; display: flex; flex-direction: column; gap: 10px; }
        .toast {
            padding: 14px 20px; border-radius: var(--radius-sm);
            background: var(--bg-glass-strong); backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass); color: var(--text-main);
            font-size: 13px; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex; align-items: center; gap: 10px;
        }
        .toast.success { border-color: var(--green); color: var(--green); }
        .toast.error { border-color: var(--red); color: var(--red); }
    </style>
</head>
<body>

    <!-- Ambient Mesh Background -->
    <div class="mesh-bg">
        <div class="mesh-orb orb-1"></div>
        <div class="mesh-orb orb-2"></div>
        <div class="mesh-orb orb-3"></div>
    </div>

    <!-- ═══ Running Train Ticker (Right to Left) ═══ -->
    <div class="train-ticker-wrap">
        <div class="train-badge">🚄 LIVE ALERTS</div>
        <div class="train-track">
            <div class="train-content" id="trainContent">
                <div class="train-item"><span>🚆</span> <strong>UPSC CSE 2026:</strong> 1056 Vacancies Open &bull; Apply before 05 Mar <span class="hot">HOT</span></div>
                <div class="train-item"><span>🚄</span> <strong>RRB Junior Engineer:</strong> 4500 Posts Across All Zones &bull; Level-6 CPC</div>
                <div class="train-item"><span>🚆</span> <strong>SBI PO Recruitment:</strong> 2000 Probationary Officers &bull; Any Graduate</div>
                <div class="train-item"><span>🚄</span> <strong>DRDO Scientist 'B':</strong> 180 Direct Entry Positions via GATE 2026 <span class="hot">NEW</span></div>
                <div class="train-item"><span>🚆</span> <strong>SSC CGL 2026:</strong> Group B & C Vacancies &bull; Tier-1 Dates Announced</div>
                <div class="train-item"><span>🚄</span> <strong>Indian Army Technical Entry:</strong> 10+2 TES Scheme &bull; Permanent Commission</div>
                <div class="train-item"><span>🚆</span> <strong>State PSC Assistant Engineer:</strong> 340 Posts in PWD & Irrigation</div>
            </div>
        </div>
    </div>

    <!-- ═══ Main Wrapper ═══ -->
    <div class="wrapper">
        
        <!-- Header -->
        <header>
            <div class="brand">
                <div class="brand-logo">⚡</div>
                <div>
                    <h1 class="brand-title">JobScout-AI</h1>
                    <div class="brand-subtitle">
                        <span>Autonomous Sarkari Intelligence & Reality Check</span>
                        <span>&bull;</span>
                        <span id="activeStatusPill" style="color:var(--green);">🟢 Active 24/7</span>
                    </div>
                </div>
            </div>

            <div class="header-actions">
                <div class="groq-pill" onclick="diagnosePipeline()" style="cursor:pointer;" title="Click for live Groq AI benchmark">
                    <span class="pulse-dot"></span>
                    <span>Groq LPU: <strong id="groqModelLabel">Dual Agents Online</strong></span>
                </div>
                <button class="btn-icon" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                    <span id="themeIcon">☀️</span>
                </button>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card glass">
                <div class="stat-header"><span class="stat-label">Active Openings</span><span class="stat-icon">📋</span></div>
                <div class="stat-val" id="statPending">0</div>
                <div class="stat-sub">Strictly verified non-expired jobs</div>
            </div>
            <div class="stat-card glass">
                <div class="stat-header"><span class="stat-label">Total Jobs Indexed</span><span class="stat-icon">🏛️</span></div>
                <div class="stat-val" id="statTotal">32</div>
                <div class="stat-sub">15-day rolling cloud retention</div>
            </div>
            <div class="stat-card glass">
                <div class="stat-header"><span class="stat-label">PDF Digests Sent</span><span class="stat-icon">📬</span></div>
                <div class="stat-val" id="statSent">0</div>
                <div class="stat-sub">Delivered via Brevo Email API</div>
            </div>
            <div class="stat-card glass">
                <div class="stat-header"><span class="stat-label">Monitored Portals</span><span class="stat-icon">🌐</span></div>
                <div class="stat-val">4</div>
                <div class="stat-sub">SarkariResult &bull; FreeJobAlert &bull; Exam &bull; Rojgar</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('intelligence', this)">🧠 AI Job Intelligence & Reality</button>
            <button class="tab-btn" onclick="switchTab('profile', this)">👤 Profile & Preferences</button>
            <button class="tab-btn" onclick="switchTab('actions', this)">⚡ Quick Actions</button>
            <button class="tab-btn" onclick="switchTab('resume', this)">📄 Resume AI Parser</button>
            <button class="tab-btn" onclick="switchTab('history', this)">📬 Digest History</button>
            <button class="tab-btn" onclick="switchTab('diagnostics', this)">🔬 System Diagnostics</button>
        </div>

        <!-- ═══ Panel 1: AI Job Intelligence & Reality (PRIMARY NEW FEATURE) ═══ -->
        <div id="panel-intelligence" class="panel active">
            
            <!-- Hero Card -->
            <div class="glass intel-hero">
                <div>
                    <h2 style="font-size:20px; font-weight:800; font-family:var(--font-heading); margin-bottom:4px;">
                        🔍 AI Job Intelligence & Workplace Reality Engine
                    </h2>
                    <div style="font-size:13px; color:var(--text-muted); max-width:680px; line-height:1.5;">
                        JobScout doesn't just find jobs. It uses <strong>Dual Groq LPU Agents</strong> to investigate each role, compute deterministic 6-factor match scores, and synthesize verified public workplace evidence before recommending you apply.
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn btn-cyan" onclick="runJobIntelligence()">⚡ Run Intelligence & Reality Check</button>
                    <a href="/api/intelligence/download-pdf" target="_blank" class="btn btn-outline">📄 Download Reality PDF</a>
                </div>
            </div>

            <!-- Loading State -->
            <div id="intelLoading" class="loading-box">
                <div class="spinner"></div>
                <div style="font-size:16px; font-weight:700; color:var(--cyan);" id="intelLoadingStep">
                    Step 1/4: Analyzing structured job requirements with Groq Agent #1...
                </div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:6px;">
                    Researching public employee signals, interview difficulty, and calculating deterministic compatibility...
                </div>
            </div>

            <!-- Intelligence Cards Grid -->
            <div class="intel-grid" id="intelGrid">
                <!-- Dynamically populated -->
            </div>
        </div>

        <!-- ═══ Panel 2: Profile & Preferences ═══ -->
        <div id="panel-profile" class="panel">
            <div class="glass" style="padding: 28px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <h2 style="font-size:18px; font-weight:800; font-family:var(--font-heading);">Personal Career Profile</h2>
                        <div style="font-size:12px; color:var(--text-muted);">Set your qualification and rank your sector preferences to customize match scoring.</div>
                    </div>
                    <button class="btn btn-primary" onclick="saveProfile()">💾 Save Preferences</button>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top:20px;">
                    <div>
                        <label style="display:block; font-size:12px; font-weight:700; color:var(--text-muted); margin-bottom:8px;">Alert Email Address</label>
                        <input type="email" id="inputEmail" style="width:100%; padding:12px 16px; border-radius:var(--radius-sm); background:var(--input-bg); border:1px solid var(--input-border); color:var(--text-main);" placeholder="your.email@example.com">
                    </div>
                    <div>
                        <label style="display:block; font-size:12px; font-weight:700; color:var(--text-muted); margin-bottom:8px;">Highest Qualification / Degree</label>
                        <input type="text" id="inputQual" style="width:100%; padding:12px 16px; border-radius:var(--radius-sm); background:var(--input-bg); border:1px solid var(--input-border); color:var(--text-main);" placeholder="e.g. B.Tech (Civil), BSc, Law, MBA, 12th Pass">
                    </div>
                </div>

                <div style="margin-top:20px;">
                    <label style="display:block; font-size:12px; font-weight:700; color:var(--text-muted); margin-bottom:8px;">Experience Level</label>
                    <div style="display:flex; gap:10px; flex-wrap:wrap;" id="expButtons">
                        <div class="chip selected" onclick="setExp('Fresher', this)">🌱 Fresher (0-1 yr)</div>
                        <div class="chip" onclick="setExp('0-2 yrs', this)">💼 Junior (1-2 yrs)</div>
                        <div class="chip" onclick="setExp('2+ yrs', this)">⭐ Experienced (2+ yrs)</div>
                    </div>
                </div>

                <div style="margin-top:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <label style="font-size:12px; font-weight:700; color:var(--text-muted);">🎯 Ranked Sector Preferences (Priority Hierarchy)</label>
                        <span style="font-size:12px; color:var(--text-muted);">1st priority receives 35% match weight</span>
                    </div>
                    <div id="rankedList"></div>
                    <label style="display:block; font-size:12px; font-weight:700; color:var(--text-muted); margin-top:14px; margin-bottom:8px;">Add More Sectors to Priority Hierarchy:</label>
                    <div style="display:flex; flex-wrap:wrap; gap:8px;" id="sectorPool"></div>
                </div>
            </div>
        </div>

        <!-- ═══ Panel 3: Quick Actions ═══ -->
        <div id="panel-actions" class="panel">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px;">
                <div class="glass" style="padding:24px; cursor:pointer;" onclick="triggerScrape()">
                    <div style="font-size:28px; margin-bottom:4px;">🔍</div>
                    <div style="font-size:16px; font-weight:700; color:var(--text-main);">Run Scraper Now</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Scrape all 4 government portals immediately and extract jobs via Groq AI.</div>
                </div>
                <div class="glass" style="padding:24px; cursor:pointer;" onclick="triggerDigest()">
                    <div style="font-size:28px; margin-bottom:4px;">📄</div>
                    <div style="font-size:16px; font-weight:700; color:var(--text-main);">Send PDF Digest Now</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Compile current non-expired job queue into a branded PDF and email it immediately.</div>
                </div>
                <div class="glass" style="padding:24px; cursor:pointer;" onclick="testEmail()">
                    <div style="font-size:28px; margin-bottom:4px;">📧</div>
                    <div style="font-size:16px; font-weight:700; color:var(--text-main);">Send Test Email</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Verify Brevo transactional email delivery to your inbox.</div>
                </div>
                <div class="glass" style="padding:24px; cursor:pointer;" onclick="toggleStatus()">
                    <div style="font-size:28px; margin-bottom:4px;" id="toggleIcon">⏸️</div>
                    <div style="font-size:16px; font-weight:700; color:var(--text-main);" id="toggleTitle">Pause Alerts</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Temporarily pause scheduled emails or resume automatic monitoring.</div>
                </div>
            </div>
        </div>

        <!-- ═══ Panel 4: Resume Parser ═══ -->
        <div id="panel-resume" class="panel">
            <div class="glass" style="padding: 28px;">
                <h2 style="font-size:18px; font-weight:800; font-family:var(--font-heading); margin-bottom:8px;">AI Resume Analyzer</h2>
                <p style="font-size:13px; color:var(--text-muted); margin-bottom:20px;">Upload your resume (PDF, DOCX, TXT) and Groq AI will automatically extract your qualification, specialization, and optimal sector matches.</p>
                <div style="border: 2px dashed var(--border-glass); border-radius: var(--radius); padding: 40px 20px; text-align:center; cursor:pointer;" onclick="document.getElementById('resumeFileInput').click()">
                    <input type="file" id="resumeFileInput" accept=".pdf,.docx,.txt" style="display:none;" onchange="uploadResume(event)">
                    <div style="font-size:40px; margin-bottom:12px;">📄</div>
                    <div style="font-size:15px; font-weight:700; color:var(--text-main);">Click or Drag & Drop Resume Here</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Supported: PDF, DOCX, TXT (Max 5MB)</div>
                </div>
                <div id="resumeResultBox" style="display:none; margin-top:20px; padding:16px; border-radius:var(--radius-sm); background:var(--bg-surface); border:1px solid var(--border-glass);">
                    <div style="font-weight:700; color:var(--green); margin-bottom:6px;">✅ Resume Parsed Successfully</div>
                    <div id="resumeResultText" style="font-size:13px; color:var(--text-secondary); line-height:1.6;"></div>
                </div>
            </div>
        </div>

        <!-- ═══ Panel 5: History ═══ -->
        <div id="panel-history" class="panel">
            <div class="glass" style="padding: 28px;">
                <h2 style="font-size:18px; font-weight:800; font-family:var(--font-heading); margin-bottom:16px;">PDF Digest Delivery Log</h2>
                <div id="historyList"><p style="color:var(--text-muted); text-align:center; padding:30px;">Loading history log...</p></div>
            </div>
        </div>

        <!-- ═══ Panel 6: System Diagnostics ═══ -->
        <div id="panel-diagnostics" class="panel">
            <div class="glass" style="padding: 28px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <div>
                        <h2 style="font-size:18px; font-weight:800; font-family:var(--font-heading);">End-to-End Pipeline Diagnostic</h2>
                        <div style="font-size:12px; color:var(--text-muted);">Live health check of Dual Groq AI engines, Supabase DB, Brevo Email, and APScheduler.</div>
                    </div>
                    <button class="btn btn-primary" onclick="diagnosePipeline()">🔬 Run Full Benchmark</button>
                </div>
                <div style="background:rgba(0,0,0,0.4); border:1px solid var(--border-glass); border-radius:var(--radius-sm); padding:16px; font-family:var(--font-mono); font-size:12px; color:var(--cyan); max-height:300px; overflow-y:auto; white-space:pre-wrap; line-height:1.6;" id="diagOutput">Click 'Run Full Benchmark' to test all system components...</div>
            </div>
        </div>

    </div>

    <!-- ═══ Deep Job Intelligence Modal ═══ -->
    <div class="modal-overlay" id="intelModal" onclick="if(event.target===this)closeModal()">
        <div class="modal-content glass">
            <button class="modal-close" onclick="closeModal()">✕</button>
            <div id="modalBody">
                <!-- Loaded dynamically -->
            </div>
        </div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-wrap" id="toastWrap"></div>

    <script>
        /* ═══════════════════════════════════════════════
           STATE & CONFIGURATION
           ═══════════════════════════════════════════════ */
        const ALL_SECTORS = ["Defence", "PSU", "Railways", "Banking", "IT/Software", "UPSC", "SSC", "State Govt", "Teaching", "Judiciary", "Medical"];
        let rankedSectors = ["Defence", "State Govt", "PSU", "Railways", "Banking"];
        let userExp = "Fresher";
        let userStatus = "active";
        let cachedIntelJobs = [];

        document.addEventListener("DOMContentLoaded", () => {
            initTheme();
            renderRankedList();
            renderSectorPool();
            loadProfile();
            loadStats();
            loadIntelligenceJobs();
        });

        function initTheme() {
            const saved = localStorage.getItem("theme") || "dark";
            document.documentElement.setAttribute("data-theme", saved);
            document.getElementById("themeIcon").textContent = saved === "dark" ? "☀️" : "🌙";
        }
        function toggleTheme() {
            const cur = document.documentElement.getAttribute("data-theme");
            const next = cur === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
            document.getElementById("themeIcon").textContent = next === "dark" ? "☀️" : "🌙";
        }

        function switchTab(tabId, btn) {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById("panel-" + tabId).classList.add("active");
            if (tabId === "history") loadHistory();
            if (tabId === "diagnostics") diagnosePipeline();
            if (tabId === "intelligence") loadIntelligenceJobs();
        }

        /* ═══════════════════════════════════════════════
           AI JOB INTELLIGENCE & REALITY LOGIC
           ═══════════════════════════════════════════════ */
        async function loadIntelligenceJobs() {
            try {
                const res = await fetch("/api/intelligence/jobs");
                if (res.ok) {
                    const data = await res.json();
                    cachedIntelJobs = data.jobs || [];
                    renderIntelligenceCards(cachedIntelJobs);
                }
            } catch (e) { console.error(e); }
        }

        async function runJobIntelligence() {
            const loading = document.getElementById("intelLoading");
            const stepLabel = document.getElementById("intelLoadingStep");
            loading.style.display = "block";

            const steps = [
                "Step 1/4: Analyzing structured job requirements with Groq Agent #1...",
                "Step 2/4: Calculating 6-factor deterministic profile match scores...",
                "Step 3/4: Investigating public employee discussions & workplace signals with Groq Agent #2...",
                "Step 4/4: Formulating evidence claims, confidence ratings, and final recommendations..."
            ];
            let stepIdx = 0;
            const timer = setInterval(() => {
                stepIdx = (stepIdx + 1) % steps.length;
                stepLabel.textContent = steps[stepIdx];
            }, 1200);

            try {
                const res = await fetch("/api/intelligence/run", { method: "POST" });
                clearInterval(timer);
                loading.style.display = "none";

                if (res.ok) {
                    const data = await res.json();
                    cachedIntelJobs = data.jobs || [];
                    renderIntelligenceCards(cachedIntelJobs);
                    showToast(`✅ Analyzed ${cachedIntelJobs.length} active jobs with Reality Check!`, "success");
                } else {
                    const err = await res.json();
                    showToast(err.error || "Intelligence run failed", "error");
                }
            } catch (e) {
                clearInterval(timer);
                loading.style.display = "none";
                showToast("Intelligence request failed", "error");
            }
        }

        function renderIntelligenceCards(jobs) {
            const grid = document.getElementById("intelGrid");
            if (!jobs.length) {
                grid.innerHTML = `
                    <div class="glass" style="grid-column: 1 / -1; padding: 40px; text-align: center;">
                        <div style="font-size: 36px; margin-bottom: 8px;">🧠</div>
                        <div style="font-size: 16px; font-weight: 700; color: var(--text-main);">No active analyzed jobs yet</div>
                        <div style="font-size: 13px; color: var(--text-muted); margin-top: 4px; margin-bottom: 16px;">Click the button below to run Groq Dual Agent Intelligence on active openings.</div>
                        <button class="btn btn-cyan" onclick="runJobIntelligence()">⚡ Run Job Intelligence Now</button>
                    </div>
                `;
                return;
            }

            grid.innerHTML = jobs.map((j, idx) => {
                const matchScore = j.match.match_score || 85;
                const realityScore = j.reality.reality_score || 75;
                const rec = j.overall_recommendation || "APPLY";
                const isStrong = rec.includes("STRONG");
                const badgeRecClass = isStrong ? "score-reality" : "score-match";

                return `
                    <div class="glass intel-card">
                        <div>
                            <div class="intel-card-head">
                                <div>
                                    <div style="font-size:16px; font-weight:800; font-family:var(--font-heading); color:var(--text-main); line-height:1.3;">
                                        ${idx + 1}. ${escapeHtml(j.title)}
                                    </div>
                                    <div style="font-size:13px; color:var(--cyan); font-weight:600; margin-top:2px;">
                                        🏛️ ${escapeHtml(j.company)}
                                    </div>
                                </div>
                            </div>

                            <div class="score-pill-row" style="margin-top:12px;">
                                <span class="score-badge score-match">🎯 ${matchScore}% Match</span>
                                <span class="score-badge score-reality">🏛️ Reality: ${realityScore}/100</span>
                                <span class="score-badge score-rec">${rec}</span>
                            </div>

                            <div style="margin-top:14px;">
                                <div class="bar-label"><span>Skill & Qualification Fit</span><span>${j.match.category_scores.skill_match}%</span></div>
                                <div class="bar-bg"><div class="bar-fill" style="width:${j.match.category_scores.skill_match}%;"></div></div>
                            </div>

                            <div style="font-size:12px; color:var(--text-secondary); margin-top:10px; line-height:1.5;">
                                <strong>💡 Workplace Signal:</strong> ${j.reality.positive_signals && j.reality.positive_signals[0] ? escapeHtml(j.reality.positive_signals[0]) : 'Strong job security & central benefits.'}
                            </div>
                        </div>

                        <div style="display:flex; gap:8px; margin-top:10px;">
                            <button class="btn btn-primary" style="flex:1; padding:8px 14px; font-size:12px;" onclick="openJobDetailModal('${j.job_id}')">🔍 Deep Intelligence</button>
                            <button class="btn btn-outline" style="padding:8px 12px; font-size:12px;" onclick="refreshJobReality('${j.job_id}')" title="Refresh Reality Research">🔄</button>
                        </div>
                    </div>
                `;
            }).join("");
        }

        async function openJobDetailModal(jobId) {
            const job = cachedIntelJobs.find(j => j.job_id === jobId);
            if (!job) return;

            const modal = document.getElementById("intelModal");
            const body = document.getElementById("modalBody");

            const cats = job.match.category_scores;
            const real = job.reality;

            body.innerHTML = `
                <div style="margin-bottom:20px;">
                    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:6px;">
                        <span class="score-badge score-match">🎯 ${job.match.match_score}% Profile Match</span>
                        <span class="score-badge score-reality">🏛️ Reality Score: ${real.reality_score}/100</span>
                        <span class="score-badge score-rec">⭐ ${job.overall_recommendation}</span>
                        <span style="font-size:11px; color:var(--text-muted);">Confidence: <strong>${real.confidence}</strong></span>
                    </div>
                    <h2 style="font-size:22px; font-weight:900; font-family:var(--font-heading); color:var(--text-main);">${escapeHtml(job.title)}</h2>
                    <div style="font-size:14px; color:var(--cyan); font-weight:700;">🏛️ ${escapeHtml(job.company)} &bull; 📍 ${escapeHtml(job.location || 'India')}</div>
                </div>

                <!-- Category Scores -->
                <div style="background:var(--bg-surface); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-glass); margin-bottom:16px;">
                    <div style="font-size:13px; font-weight:800; color:var(--text-main); margin-bottom:10px;">📊 6-Factor Deterministic Match Breakdown</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        <div>
                            <div class="bar-label"><span>Skill & Degree (35%)</span><span>${cats.skill_match}%</span></div>
                            <div class="bar-bg"><div class="bar-fill" style="width:${cats.skill_match}%;"></div></div>
                        </div>
                        <div>
                            <div class="bar-label"><span>Experience (20%)</span><span>${cats.experience_match}%</span></div>
                            <div class="bar-bg"><div class="bar-fill" style="width:${cats.experience_match}%;"></div></div>
                        </div>
                        <div>
                            <div class="bar-label"><span>Sector Priority (20%)</span><span>${cats.role_match}%</span></div>
                            <div class="bar-bg"><div class="bar-fill" style="width:${cats.role_match}%;"></div></div>
                        </div>
                        <div>
                            <div class="bar-label"><span>Compensation (10%)</span><span>${cats.salary_match}%</span></div>
                            <div class="bar-bg"><div class="bar-fill" style="width:${cats.salary_match}%;"></div></div>
                        </div>
                    </div>
                </div>

                <!-- Workplace Reality -->
                <div style="background:var(--bg-surface); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-glass); margin-bottom:16px;">
                    <div style="font-size:13px; font-weight:800; color:var(--text-main); margin-bottom:10px;">🏛️ Employee Reality Check (/5.0 Scale)</div>
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center;">
                        <div style="padding:8px; background:rgba(255,255,255,0.03); border-radius:8px;">
                            <div style="font-size:18px; font-weight:900; color:var(--cyan);">${real.employee_sentiment}/5</div>
                            <div style="font-size:10px; color:var(--text-muted);">Employee Sentiment</div>
                        </div>
                        <div style="padding:8px; background:rgba(255,255,255,0.03); border-radius:8px;">
                            <div style="font-size:18px; font-weight:900; color:var(--green);">${real.work_life_balance}/5</div>
                            <div style="font-size:10px; color:var(--text-muted);">Work-Life Balance</div>
                        </div>
                        <div style="padding:8px; background:rgba(255,255,255,0.03); border-radius:8px;">
                            <div style="font-size:18px; font-weight:900; color:var(--primary);">${real.learning_growth}/5</div>
                            <div style="font-size:10px; color:var(--text-muted);">Learning / Growth</div>
                        </div>
                        <div style="padding:8px; background:rgba(255,255,255,0.03); border-radius:8px;">
                            <div style="font-size:18px; font-weight:900; color:var(--amber);">${real.interview_difficulty}/5</div>
                            <div style="font-size:10px; color:var(--text-muted);">Interview Difficulty</div>
                        </div>
                    </div>
                </div>

                <!-- Signals & Concerns -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
                    <div style="padding:14px; background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); border-radius:var(--radius-sm);">
                        <div style="font-weight:700; color:var(--green); font-size:12px; margin-bottom:6px;">✅ Verified Positive Signals</div>
                        <ul style="font-size:12px; color:var(--text-secondary); padding-left:16px; line-height:1.5;">
                            ${(real.positive_signals || []).map(p => `<li>${escapeHtml(p)}</li>`).join("")}
                        </ul>
                    </div>
                    <div style="padding:14px; background:rgba(244,63,94,0.06); border:1px solid rgba(244,63,94,0.2); border-radius:var(--radius-sm);">
                        <div style="font-weight:700; color:var(--red); font-size:12px; margin-bottom:6px;">⚠️ Potential Concerns & Workload</div>
                        <ul style="font-size:12px; color:var(--text-secondary); padding-left:16px; line-height:1.5;">
                            ${(real.potential_concerns || []).map(c => `<li>${escapeHtml(c)}</li>`).join("")}
                        </ul>
                    </div>
                </div>

                <!-- Interview Intel -->
                ${real.interview ? `
                <div style="background:var(--bg-surface); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-glass); margin-bottom:16px;">
                    <div style="font-size:13px; font-weight:800; color:var(--text-main); margin-bottom:6px;">📝 Interview & Exam Intelligence</div>
                    <div style="font-size:12px; color:var(--text-secondary); line-height:1.6;">
                        <strong>Selection Process:</strong> ${escapeHtml(real.interview.rounds_count || 'Written Exam + Interview')}<br/>
                        <strong>Key Preparation Topics:</strong> ${(real.interview.common_topics || []).join(", ") || 'General Aptitude, Technical domain'}<br/>
                        ${real.interview.candidate_tips ? `<strong>Candidate Tip:</strong> <i>${escapeHtml(real.interview.candidate_tips)}</i>` : ''}
                    </div>
                </div>` : ''}

                <!-- Action Links -->
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:20px;">
                    <div>
                        ${job.apply_link ? `<a href="${job.apply_link}" target="_blank" class="btn btn-primary" style="padding:10px 18px;">✍️ Apply Online</a>` : ''}
                        ${job.notification_link ? `<a href="${job.notification_link}" target="_blank" class="btn btn-outline" style="padding:10px 18px; margin-left:8px;">📄 Official Notice</a>` : ''}
                    </div>
                    <button class="btn btn-cyan" onclick="refreshJobReality('${job.job_id}')">🔄 Refresh Reality Check</button>
                </div>
            `;

            modal.classList.add("active");
        }

        function closeModal() {
            document.getElementById("intelModal").classList.remove("active");
        }

        async function refreshJobReality(jobId) {
            showToast("Re-running Groq Agent #2 reality research...", "success");
            try {
                const res = await fetch(`/api/intelligence/job/${jobId}/refresh`, { method: "POST" });
                if (res.ok) {
                    const data = await res.json();
                    showToast("Reality check updated! ✅", "success");
                    loadIntelligenceJobs();
                    if (document.getElementById("intelModal").classList.contains("active")) {
                        openJobDetailModal(jobId);
                    }
                } else {
                    showToast("Refresh failed", "error");
                }
            } catch (e) { showToast("Network error", "error"); }
        }

        /* ═══════════════════════════════════════════════
           PROFILE & RANKED SECTOR LOGIC
           ═══════════════════════════════════════════════ */
        function renderRankedList() {
            const container = document.getElementById("rankedList");
            if (!rankedSectors.length) {
                container.innerHTML = '<div style="color:var(--text-muted); font-size:13px; padding:10px;">No sector preferences selected yet. Click sectors below to rank them!</div>';
                return;
            }
            container.innerHTML = rankedSectors.map((s, idx) => `
                <div class="ranked-item">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div class="rank-num">#${idx + 1}</div>
                        <div style="font-size:14px; font-weight:600; color:var(--text-main);">${getSectorEmoji(s)} ${s}</div>
                    </div>
                    <div style="display:flex; gap:6px;">
                        ${idx > 0 ? `<button class="btn-arrow" onclick="moveRank(${idx}, -1)">▲</button>` : ''}
                        ${idx < rankedSectors.length - 1 ? `<button class="btn-arrow" onclick="moveRank(${idx}, 1)">▼</button>` : ''}
                        <button class="btn-arrow" onclick="removeRank('${s}')" style="color:var(--red);">✕</button>
                    </div>
                </div>
            `).join("");
        }

        function renderSectorPool() {
            const container = document.getElementById("sectorPool");
            const available = ALL_SECTORS.filter(s => !rankedSectors.includes(s));
            container.innerHTML = available.map(s => `
                <div class="chip" onclick="addRank('${s}')">+ ${getSectorEmoji(s)} ${s}</div>
            `).join("");
        }

        function getSectorEmoji(s) {
            const map = { "Defence": "🎖️", "PSU": "🏭", "Railways": "🚂", "Banking": "🏦", "IT/Software": "💻", "UPSC": "🏛️", "SSC": "📊", "State Govt": "🏘️", "Teaching": "📚", "Judiciary": "⚖️", "Medical": "🏥" };
            return map[s] || "💼";
        }

        function moveRank(idx, dir) {
            const target = idx + dir;
            if (target < 0 || target >= rankedSectors.length) return;
            const temp = rankedSectors[idx];
            rankedSectors[idx] = rankedSectors[target];
            rankedSectors[target] = temp;
            renderRankedList(); renderSectorPool();
        }

        function addRank(s) {
            if (!rankedSectors.includes(s)) {
                rankedSectors.push(s);
                renderRankedList(); renderSectorPool();
            }
        }

        function removeRank(s) {
            rankedSectors = rankedSectors.filter(x => x !== s);
            renderRankedList(); renderSectorPool();
        }

        function setExp(exp, el) {
            userExp = exp;
            document.querySelectorAll("#expButtons .chip").forEach(c => c.classList.remove("selected"));
            el.classList.add("selected");
        }

        async function loadProfile() {
            try {
                const res = await fetch("/api/profile");
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById("inputEmail").value = data.email || "";
                    document.getElementById("inputQual").value = data.qualification || "";
                    if (data.interests && Array.isArray(data.interests) && data.interests.length) {
                        rankedSectors = data.interests;
                        renderRankedList(); renderSectorPool();
                    }
                    if (data.experience_level) {
                        userExp = data.experience_level;
                        document.querySelectorAll("#expButtons .chip").forEach(c => {
                            if (c.textContent.includes(userExp)) c.classList.add("selected");
                            else c.classList.remove("selected");
                        });
                    }
                    userStatus = data.status || "active";
                    updateStatusUI();
                }
            } catch (e) { console.error(e); }
        }

        async function saveProfile() {
            const email = document.getElementById("inputEmail").value.trim();
            const qual = document.getElementById("inputQual").value.trim();
            if (!email || !qual) {
                showToast("Email and Qualification are required", "error");
                return;
            }
            try {
                const res = await fetch("/api/profile", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email, qualification: qual, interests: rankedSectors, experience_level: userExp })
                });
                if (res.ok) {
                    showToast("Profile & ranked preferences saved! ✅", "success");
                    loadIntelligenceJobs();
                } else {
                    showToast("Failed to save profile", "error");
                }
            } catch (e) { showToast("Network error saving profile", "error"); }
        }

        async function loadStats() {
            try {
                const res = await fetch("/api/stats");
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById("statPending").textContent = data.pending_today || 0;
                    document.getElementById("statTotal").textContent = data.total_jobs || 0;
                    document.getElementById("statSent").textContent = data.digests_sent || 0;
                }
            } catch (e) {}
        }

        /* ── Triggers ── */
        async function triggerScrape() {
            showToast("Starting live scrape across 4 government portals...", "success");
            try {
                const res = await fetch("/api/trigger-scrape");
                showToast("Scraper running in background with Groq AI 🚀", "success");
                setTimeout(loadStats, 3000);
            } catch (e) { showToast("Scraper launch failed", "error"); }
        }

        async function triggerDigest() {
            showToast("Generating executive PDF digest...", "success");
            try {
                const res = await fetch("/api/trigger-digest");
                const data = await res.json();
                if (res.ok) {
                    showToast(`✅ Digest sent (${data.jobs} jobs) to ${data.email}`, "success");
                    loadStats();
                } else { showToast(data.error || "Failed to send digest", "error"); }
            } catch (e) { showToast("Digest trigger failed", "error"); }
        }

        async function testEmail() {
            showToast("Sending test email via Brevo...", "success");
            try {
                const res = await fetch("/api/test-email");
                const data = await res.json();
                if (res.ok) { showToast(`✅ Test email sent to ${data.email}!`, "success"); }
                else { showToast(data.error || "Brevo email failed", "error"); }
            } catch (e) { showToast("Email test failed", "error"); }
        }

        async function toggleStatus() {
            const nextStatus = userStatus === "active" ? "paused" : "active";
            try {
                const res = await fetch("/api/status", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: nextStatus })
                });
                if (res.ok) {
                    userStatus = nextStatus;
                    updateStatusUI();
                    showToast(`Monitoring status: ${userStatus.toUpperCase()}`, "success");
                }
            } catch (e) { showToast("Failed to toggle status", "error"); }
        }

        function updateStatusUI() {
            const pill = document.getElementById("activeStatusPill");
            const tTitle = document.getElementById("toggleTitle");
            const tIcon = document.getElementById("toggleIcon");
            if (userStatus === "active") {
                pill.textContent = "🟢 Active 24/7";
                pill.style.color = "var(--green)";
                tTitle.textContent = "Pause Alerts";
                tIcon.textContent = "⏸️";
            } else {
                pill.textContent = "⏸️ Paused";
                pill.style.color = "var(--amber)";
                tTitle.textContent = "Resume Alerts";
                tIcon.textContent = "▶️";
            }
        }

        async function uploadResume(event) {
            const file = event.target.files[0];
            if (!file) return;
            showToast("Uploading & parsing resume with Groq AI...", "success");
            const formData = new FormData();
            formData.append("file", file);
            try {
                const res = await fetch("/api/resume", { method: "POST", body: formData });
                const data = await res.json();
                if (res.ok) {
                    showToast("Resume parsed & profile updated! 🎯", "success");
                    document.getElementById("resumeResultBox").style.display = "block";
                    document.getElementById("resumeResultText").innerHTML = `
                        <strong>Qualification:</strong> ${data.parsed.qualification || 'Extracted'}<br>
                        <strong>Specialization:</strong> ${data.parsed.degree || 'General'}<br>
                        <strong>Skills:</strong> ${(data.parsed.skills || []).join(', ') || 'N/A'}<br>
                        <strong>Suggested Sectors:</strong> ${(data.parsed.preferred_sectors || []).join(', ') || 'N/A'}
                    `;
                    loadProfile();
                } else { showToast(data.error || "Resume upload failed", "error"); }
            } catch (e) { showToast("Upload failed", "error"); }
        }

        async function loadHistory() {
            try {
                const res = await fetch("/api/digest-history");
                const data = await res.json();
                const container = document.getElementById("historyList");
                if (!data.length) {
                    container.innerHTML = '<p style="color:var(--text-muted); text-align:center; padding:30px;">No digests recorded yet.</p>';
                    return;
                }
                container.innerHTML = data.map(h => `
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:var(--bg-surface); border:1px solid var(--border-glass); border-radius:var(--radius-sm); margin-bottom:8px;">
                        <div>
                            <div style="font-weight:700; color:var(--text-main);">📧 ${h.date}</div>
                            <div style="font-size:12px; color:var(--text-muted);">${h.job_count} jobs &bull; Type: ${h.type}</div>
                        </div>
                        <span style="font-size:12px; font-weight:700; color:${h.sent ? 'var(--green)' : 'var(--amber)'};">${h.sent ? '✅ Delivered' : '⏳ Pending'}</span>
                    </div>
                `).join("");
            } catch (e) {}
        }

        async function diagnosePipeline() {
            const out = document.getElementById("diagOutput");
            out.textContent = "Testing pipeline connections: Groq Dual Agents, Supabase DB, Scheduler, Profile...";
            try {
                const res = await fetch("/api/debug");
                const data = await res.json();
                out.textContent = JSON.stringify(data, null, 2);
            } catch (e) { out.textContent = "Diagnostic error: " + e.message; }
        }

        function showToast(msg, type = "success") {
            const wrap = document.getElementById("toastWrap");
            const toast = document.createElement("div");
            toast.className = `toast ${type}`;
            toast.textContent = msg;
            wrap.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        }

        function escapeHtml(text) {
            if (!text) return "";
            return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
'''
