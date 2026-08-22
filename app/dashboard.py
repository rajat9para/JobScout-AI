"""Dashboard HTML — Premium Glassmorphism Web Dashboard.

Crystal-clear frosted glass aesthetic with:
- Animated gradient mesh background with floating orbs
- Glass panels with backdrop-filter blur + glow borders
- Premium gradient buttons with hover/pulse animations
- Google Fonts: Outfit (headings) + Inter (body)
- Neon-glow navigation, chips, and stats
- Animated stat counters and floating particles
- Full dark/light theme support

All API integrations preserved:
- Profile CRUD, pause/resume
- Resume upload with drag-drop
- Digest history, test email, trigger scrape/digest
- Scheduler status, Brevo diagnostics
"""

DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobScout-AI — Command Center</title>
    <meta name="description" content="JobScout-AI: Personal Government Job Alert Bot with AI-powered matching">
    <link rel="icon" type="image/png" href="/static/weblogo.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        /* ═══════════════════════════════════════════════
           DESIGN TOKENS
           ═══════════════════════════════════════════════ */
        :root {
            --font-heading: 'Outfit', 'Inter', sans-serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --radius: 16px;
            --radius-sm: 10px;
            --radius-xs: 8px;
            --radius-full: 9999px;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --spring: 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        /* ── Dark Theme (Default) ── */
        [data-theme="dark"] {
            --bg-base: #050510;
            --bg-mesh-1: #0a0a2e;
            --bg-mesh-2: #1a0530;
            --bg-mesh-3: #050520;
            --bg-surface: rgba(255, 255, 255, 0.03);
            --bg-surface-hover: rgba(255, 255, 255, 0.06);
            --bg-glass: rgba(15, 15, 35, 0.6);
            --bg-glass-strong: rgba(15, 15, 35, 0.8);

            --border-glass: rgba(255, 255, 255, 0.08);
            --border-glass-hover: rgba(255, 255, 255, 0.15);
            --border-glow: rgba(139, 92, 246, 0.3);

            --text-main: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --text-dim: #475569;

            --primary: #8b5cf6;
            --primary-hover: #a78bfa;
            --primary-glow: rgba(139, 92, 246, 0.4);
            --primary-soft: rgba(139, 92, 246, 0.12);

            --cyan: #22d3ee;
            --cyan-glow: rgba(34, 211, 238, 0.3);
            --cyan-soft: rgba(34, 211, 238, 0.1);

            --green: #34d399;
            --green-glow: rgba(52, 211, 153, 0.3);
            --green-soft: rgba(52, 211, 153, 0.1);
            --green-border: rgba(52, 211, 153, 0.25);

            --red: #f43f5e;
            --red-glow: rgba(244, 63, 94, 0.3);
            --red-soft: rgba(244, 63, 94, 0.1);
            --red-border: rgba(244, 63, 94, 0.25);

            --amber: #fbbf24;
            --amber-soft: rgba(251, 191, 36, 0.1);
            --amber-border: rgba(251, 191, 36, 0.25);

            --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            --shadow-glow: 0 0 40px rgba(139, 92, 246, 0.15);
            --shadow-btn: 0 4px 15px rgba(139, 92, 246, 0.3);

            --input-bg: rgba(255, 255, 255, 0.04);
            --input-border: rgba(255, 255, 255, 0.1);
            --input-focus: var(--primary);
            --input-focus-ring: rgba(139, 92, 246, 0.25);

            --particle-color: rgba(139, 92, 246, 0.15);
            --orb-1: radial-gradient(circle at 20% 30%, rgba(139, 92, 246, 0.12) 0%, transparent 50%);
            --orb-2: radial-gradient(circle at 80% 70%, rgba(34, 211, 238, 0.08) 0%, transparent 50%);
            --orb-3: radial-gradient(circle at 50% 80%, rgba(244, 63, 94, 0.06) 0%, transparent 40%);
        }

        /* ── Light Theme ── */
        [data-theme="light"] {
            --bg-base: #f0f2f8;
            --bg-mesh-1: #e8edf5;
            --bg-mesh-2: #f5f0ff;
            --bg-mesh-3: #f0f8ff;
            --bg-surface: rgba(255, 255, 255, 0.6);
            --bg-surface-hover: rgba(255, 255, 255, 0.8);
            --bg-glass: rgba(255, 255, 255, 0.65);
            --bg-glass-strong: rgba(255, 255, 255, 0.85);

            --border-glass: rgba(0, 0, 0, 0.06);
            --border-glass-hover: rgba(0, 0, 0, 0.12);
            --border-glow: rgba(124, 58, 237, 0.2);

            --text-main: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-dim: #94a3b8;

            --primary: #7c3aed;
            --primary-hover: #6d28d9;
            --primary-glow: rgba(124, 58, 237, 0.25);
            --primary-soft: rgba(124, 58, 237, 0.08);

            --cyan: #0891b2;
            --cyan-glow: rgba(8, 145, 178, 0.2);
            --cyan-soft: rgba(8, 145, 178, 0.06);

            --green: #059669;
            --green-glow: rgba(5, 150, 105, 0.2);
            --green-soft: rgba(5, 150, 105, 0.06);
            --green-border: rgba(5, 150, 105, 0.2);

            --red: #dc2626;
            --red-glow: rgba(220, 38, 38, 0.2);
            --red-soft: rgba(220, 38, 38, 0.06);
            --red-border: rgba(220, 38, 38, 0.2);

            --amber: #d97706;
            --amber-soft: rgba(217, 119, 6, 0.06);
            --amber-border: rgba(217, 119, 6, 0.2);

            --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
            --shadow-glow: 0 0 40px rgba(124, 58, 237, 0.08);
            --shadow-btn: 0 4px 15px rgba(124, 58, 237, 0.2);

            --input-bg: rgba(255, 255, 255, 0.8);
            --input-border: rgba(0, 0, 0, 0.1);
            --input-focus: var(--primary);
            --input-focus-ring: rgba(124, 58, 237, 0.15);

            --particle-color: rgba(124, 58, 237, 0.08);
            --orb-1: radial-gradient(circle at 20% 30%, rgba(124, 58, 237, 0.08) 0%, transparent 50%);
            --orb-2: radial-gradient(circle at 80% 70%, rgba(8, 145, 178, 0.06) 0%, transparent 50%);
            --orb-3: radial-gradient(circle at 50% 80%, rgba(244, 63, 94, 0.04) 0%, transparent 40%);
        }

        /* ═══════════════════════════════════════════════
           RESET + BASE
           ═══════════════════════════════════════════════ */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--font-body);
            background: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
            transition: background 0.5s ease, color 0.3s ease;
        }

        /* ═══════════════════════════════════════════════
           ANIMATED BACKGROUND
           ═══════════════════════════════════════════════ */
        .bg-mesh {
            position: fixed; inset: 0; z-index: 0; pointer-events: none;
            background: var(--bg-base);
        }
        .bg-mesh::before, .bg-mesh::after {
            content: ''; position: absolute; inset: 0; opacity: 1;
        }
        .bg-mesh::before {
            background: var(--orb-1), var(--orb-2), var(--orb-3);
            animation: meshFloat 20s ease-in-out infinite alternate;
        }
        .bg-mesh::after {
            background: radial-gradient(circle at 60% 40%, var(--particle-color) 0%, transparent 40%);
            animation: meshFloat2 25s ease-in-out infinite alternate-reverse;
        }
        @keyframes meshFloat {
            0% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(-30px, 20px) scale(1.05); }
            100% { transform: translate(20px, -15px) scale(0.98); }
        }
        @keyframes meshFloat2 {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(30px, -25px) rotate(3deg); }
        }

        /* Floating Particles */
        .particles {
            position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
        }
        .particle {
            position: absolute; border-radius: 50%;
            background: var(--primary);
            opacity: 0.12;
            animation: particleFloat linear infinite;
        }
        @keyframes particleFloat {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 0.12; }
            90% { opacity: 0.12; }
            100% { transform: translateY(-10vh) rotate(720deg); opacity: 0; }
        }

        /* ═══════════════════════════════════════════════
           GLASS SYSTEM
           ═══════════════════════════════════════════════ */
        .glass {
            background: var(--bg-glass);
            backdrop-filter: blur(20px) saturate(1.3);
            -webkit-backdrop-filter: blur(20px) saturate(1.3);
            border: 1px solid var(--border-glass);
            box-shadow: var(--shadow-glass);
            transition: all var(--transition);
        }
        .glass:hover {
            border-color: var(--border-glass-hover);
            box-shadow: var(--shadow-glass), var(--shadow-glow);
        }
        .glass-strong {
            background: var(--bg-glass-strong);
            backdrop-filter: blur(28px) saturate(1.4);
            -webkit-backdrop-filter: blur(28px) saturate(1.4);
            border: 1px solid var(--border-glass);
            box-shadow: var(--shadow-glass);
        }

        /* ═══════════════════════════════════════════════
           HEADER
           ═══════════════════════════════════════════════ */
        .header {
            position: sticky; top: 0; z-index: 100;
            background: var(--bg-glass-strong);
            backdrop-filter: blur(24px) saturate(1.5);
            -webkit-backdrop-filter: blur(24px) saturate(1.5);
            border-bottom: 1px solid var(--border-glass);
            padding: 0 24px; height: 72px;
            display: flex; align-items: center; justify-content: center;
        }
        .header-content {
            width: 100%; max-width: 1200px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .brand-section { display: flex; align-items: center; gap: 14px; }
        .logo {
            width: 40px; height: 40px; border-radius: var(--radius-sm);
            object-fit: cover;
            border: 1px solid var(--border-glass);
            box-shadow: 0 0 20px var(--primary-glow);
            transition: all var(--spring);
        }
        .logo:hover { transform: scale(1.1) rotate(-5deg); box-shadow: 0 0 30px var(--primary-glow); }
        .brand-text { display: flex; flex-direction: column; }
        .brand-text h1 {
            font-family: var(--font-heading); font-size: 20px; font-weight: 800;
            letter-spacing: -0.5px; color: var(--text-main); line-height: 1.2;
            background: linear-gradient(135deg, var(--primary), var(--cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .version {
            font-size: 10px; font-weight: 700; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 2px;
        }
        .header-actions { display: flex; align-items: center; gap: 10px; }

        /* ═══════════════════════════════════════════════
           BUTTONS
           ═══════════════════════════════════════════════ */
        .icon-btn {
            background: var(--bg-surface); border: 1px solid var(--border-glass);
            border-radius: var(--radius-full); width: 40px; height: 40px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 17px; color: var(--text-muted);
            transition: all var(--spring); position: relative; overflow: hidden;
        }
        .icon-btn:hover {
            background: var(--bg-surface-hover); color: var(--text-main);
            transform: scale(1.1); border-color: var(--border-glass-hover);
            box-shadow: 0 0 20px var(--primary-glow);
        }

        .btn {
            padding: 10px 20px; border-radius: var(--radius-sm);
            font-size: 13px; font-weight: 700; cursor: pointer;
            transition: all var(--spring); border: none;
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            font-family: var(--font-heading); letter-spacing: 0.3px;
            position: relative; overflow: hidden;
        }
        .btn:active { transform: scale(0.97); }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), #6d28d9);
            color: #fff;
            box-shadow: var(--shadow-btn), inset 0 1px 0 rgba(255,255,255,0.15);
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, var(--primary-hover), var(--primary));
            box-shadow: 0 6px 25px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

        .btn-outline {
            background: var(--bg-surface); color: var(--text-main);
            border: 1px solid var(--border-glass);
        }
        .btn-outline:hover {
            background: var(--bg-surface-hover);
            border-color: var(--primary);
            box-shadow: 0 0 15px var(--primary-glow);
        }

        .btn-danger {
            background: linear-gradient(135deg, var(--red), #be123c);
            color: #fff; box-shadow: 0 4px 15px var(--red-glow);
        }
        .btn-danger:hover { box-shadow: 0 6px 25px var(--red-glow); transform: translateY(-2px); }

        /* Status Pill */
        .status-pill {
            display: flex; align-items: center; gap: 8px;
            padding: 7px 16px; border-radius: var(--radius-full);
            font-size: 12px; font-weight: 700; cursor: pointer;
            transition: all var(--spring); user-select: none;
            font-family: var(--font-heading); letter-spacing: 0.5px;
        }
        .status-pill:hover { transform: scale(1.05); }
        .status-pill.active {
            background: var(--green-soft); border: 1px solid var(--green-border);
            color: var(--green); box-shadow: 0 0 15px var(--green-glow);
        }
        .status-pill.paused {
            background: var(--red-soft); border: 1px solid var(--red-border);
            color: var(--red); box-shadow: 0 0 15px var(--red-glow);
        }
        .dot {
            width: 8px; height: 8px; border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        .active .dot { background: var(--green); box-shadow: 0 0 10px var(--green); }
        .paused .dot { background: var(--red); animation: none; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

        /* ═══════════════════════════════════════════════
           LAYOUT
           ═══════════════════════════════════════════════ */
        .layout {
            position: relative; z-index: 1;
            max-width: 1200px; margin: 0 auto; padding: 32px 24px;
            display: grid; grid-template-columns: 220px 1fr; gap: 28px;
        }
        @media (max-width: 860px) {
            .layout { grid-template-columns: 1fr; padding: 20px 16px; }
            .sidebar { flex-direction: row; overflow-x: auto; position: static; gap: 6px; }
            .nav-item { white-space: nowrap; font-size: 13px; padding: 8px 14px; }
            .header-actions .btn-label { display: none; }
            .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        }

        /* ═══════════════════════════════════════════════
           SIDEBAR
           ═══════════════════════════════════════════════ */
        .sidebar {
            display: flex; flex-direction: column; gap: 6px;
            position: sticky; top: 104px; align-self: start;
        }
        .nav-item {
            padding: 11px 18px; border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 600; color: var(--text-muted);
            cursor: pointer; transition: all var(--transition);
            display: flex; align-items: center; gap: 12px;
            border: 1px solid transparent; background: transparent;
            text-align: left; font-family: var(--font-heading); width: 100%;
        }
        .nav-item:hover {
            color: var(--text-main); background: var(--bg-surface);
            border-color: var(--border-glass);
        }
        .nav-item.on {
            color: var(--primary); background: var(--primary-soft);
            border-color: var(--border-glow);
            box-shadow: 0 0 20px var(--primary-glow), var(--shadow-glass);
            font-weight: 700;
        }
        .nav-icon { font-size: 17px; }

        /* ═══════════════════════════════════════════════
           CONTENT + PANELS
           ═══════════════════════════════════════════════ */
        .content { display: flex; flex-direction: column; gap: 24px; }
        .panel { display: none; }
        .panel.on { display: block; animation: panelIn 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
        @keyframes panelIn {
            from { opacity: 0; transform: translateY(16px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ═══════════════════════════════════════════════
           STAT CARDS
           ═══════════════════════════════════════════════ */
        .stats-row {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px;
        }
        .stat-card {
            border-radius: var(--radius); padding: 20px;
            display: flex; flex-direction: column; gap: 6px;
            position: relative; overflow: hidden;
        }
        .stat-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, var(--primary), var(--cyan));
            opacity: 0.6;
        }
        .stat-val {
            font-family: var(--font-heading); font-size: 32px; font-weight: 900;
            letter-spacing: -1px; line-height: 1;
            background: linear-gradient(135deg, var(--text-main), var(--primary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-lbl {
            font-size: 11px; font-weight: 700; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 1.5px;
        }
        .stat-icon {
            position: absolute; top: 14px; right: 16px;
            font-size: 28px; opacity: 0.2;
        }

        /* ═══════════════════════════════════════════════
           GLASS CARDS
           ═══════════════════════════════════════════════ */
        .card {
            border-radius: var(--radius); padding: 24px;
            margin-bottom: 20px;
        }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
        .card-title {
            font-family: var(--font-heading); font-size: 17px; font-weight: 700;
            color: var(--text-main); letter-spacing: -0.3px;
        }
        .card-desc {
            font-size: 13px; color: var(--text-muted); margin-bottom: 18px;
            line-height: 1.7;
        }
        .card-icon { font-size: 20px; }

        /* ═══════════════════════════════════════════════
           FORM ELEMENTS
           ═══════════════════════════════════════════════ */
        .fg { margin-bottom: 18px; }
        .fl {
            display: block; font-size: 12px; font-weight: 700; color: var(--text-secondary);
            margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.8px;
            font-family: var(--font-heading);
        }
        .fi {
            width: 100%; padding: 12px 16px;
            background: var(--input-bg); border: 1px solid var(--input-border);
            border-radius: var(--radius-sm); color: var(--text-main);
            font-size: 14px; font-family: var(--font-body); transition: all var(--transition);
        }
        .fi:focus {
            outline: none; border-color: var(--input-focus);
            box-shadow: 0 0 0 3px var(--input-focus-ring), 0 0 20px var(--primary-glow);
        }
        .fi::placeholder { color: var(--text-dim); }

        /* ═══════════════════════════════════════════════
           CHIPS + RADIOS
           ═══════════════════════════════════════════════ */
        .chips, .radios { display: flex; flex-wrap: wrap; gap: 8px; }
        .chip, .radio {
            padding: 9px 18px; border-radius: var(--radius-full);
            font-size: 13px; font-weight: 600; cursor: pointer;
            border: 1px solid var(--border-glass); background: var(--bg-surface);
            color: var(--text-muted); transition: all var(--spring);
            user-select: none; font-family: var(--font-heading);
        }
        .chip:hover, .radio:hover {
            border-color: var(--border-glass-hover); color: var(--text-main);
            background: var(--bg-surface-hover); transform: translateY(-1px);
        }
        .chip.sel, .radio.sel {
            background: var(--primary-soft);
            border-color: var(--primary);
            color: var(--primary); font-weight: 700;
            box-shadow: 0 0 15px var(--primary-glow);
        }

        /* ═══════════════════════════════════════════════
           UPLOAD ZONE
           ═══════════════════════════════════════════════ */
        .upload {
            border: 2px dashed var(--border-glass-hover); border-radius: var(--radius);
            padding: 48px 20px; text-align: center; cursor: pointer;
            transition: all var(--spring);
            background: var(--bg-surface); position: relative; overflow: hidden;
        }
        .upload::before {
            content: ''; position: absolute; inset: -2px; border-radius: var(--radius);
            background: conic-gradient(from 0deg, var(--primary), var(--cyan), var(--primary));
            opacity: 0; transition: opacity 0.5s; z-index: -1;
            animation: borderRotate 3s linear infinite;
        }
        @keyframes borderRotate { to { transform: rotate(360deg); } }
        .upload:hover::before, .upload.over::before { opacity: 0.3; }
        .upload:hover, .upload.over {
            border-color: var(--primary); background: var(--primary-soft);
            transform: scale(1.01); box-shadow: 0 0 30px var(--primary-glow);
        }
        .upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
        .upload-icon { font-size: 40px; margin-bottom: 14px; }
        .upload-text { font-size: 15px; font-weight: 600; color: var(--text-main); font-family: var(--font-heading); }
        .upload-hint { font-size: 12px; color: var(--text-muted); margin-top: 6px; }

        /* ═══════════════════════════════════════════════
           HISTORY
           ═══════════════════════════════════════════════ */
        .hist-list { display: flex; flex-direction: column; gap: 10px; }
        .hist {
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 18px; border-radius: var(--radius-sm);
            border: 1px solid var(--border-glass); background: var(--bg-surface);
            transition: all var(--transition);
        }
        .hist:hover {
            border-color: var(--border-glass-hover); transform: translateX(4px);
            box-shadow: 0 0 15px var(--primary-glow);
        }
        .hist-date { font-weight: 700; font-size: 14px; color: var(--text-main); font-family: var(--font-heading); }
        .hist-meta { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
        .badge {
            padding: 5px 14px; border-radius: var(--radius-full);
            font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
            font-family: var(--font-heading);
        }
        .badge-ok { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }
        .badge-wait { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber-border); }

        /* ═══════════════════════════════════════════════
           SCHEDULE
           ═══════════════════════════════════════════════ */
        .sched-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
        .sched {
            background: var(--bg-surface); border: 1px solid var(--border-glass);
            border-radius: var(--radius-sm); padding: 24px; text-align: center;
            transition: all var(--spring); position: relative; overflow: hidden;
        }
        .sched:hover { border-color: var(--border-glow); transform: translateY(-3px); box-shadow: 0 0 20px var(--primary-glow); }
        .sched-time {
            font-family: var(--font-heading); font-size: 28px; font-weight: 800;
            color: var(--text-main); margin: 10px 0 4px; letter-spacing: -0.5px;
        }
        .sched-lbl { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }

        /* ═══════════════════════════════════════════════
           ACTION CARDS
           ═══════════════════════════════════════════════ */
        .action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
        .action-card {
            border-radius: var(--radius); padding: 22px; text-align: left;
            cursor: pointer; transition: all var(--spring);
            background: var(--bg-glass); border: 1px solid var(--border-glass);
            backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
        }
        .action-card:hover {
            border-color: var(--primary); transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2), 0 0 25px var(--primary-glow);
        }
        .action-icon { font-size: 28px; margin-bottom: 14px; }
        .action-title {
            font-family: var(--font-heading); font-size: 15px; font-weight: 700;
            color: var(--text-main); margin-bottom: 4px;
        }
        .action-desc { font-size: 12px; color: var(--text-muted); line-height: 1.6; }

        /* ═══════════════════════════════════════════════
           QUICK LINKS
           ═══════════════════════════════════════════════ */
        .quick-link {
            display: flex; align-items: center; gap: 10px;
            color: var(--primary); text-decoration: none; font-weight: 600; font-size: 14px;
            padding: 10px 14px; border-radius: var(--radius-xs);
            transition: all var(--transition);
            font-family: var(--font-heading);
        }
        .quick-link:hover {
            background: var(--primary-soft); transform: translateX(4px);
        }

        /* ═══════════════════════════════════════════════
           TOAST NOTIFICATIONS
           ═══════════════════════════════════════════════ */
        .toast {
            position: fixed; bottom: 24px; right: 24px; z-index: 9999;
            padding: 14px 22px; border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 600; color: #fff;
            font-family: var(--font-heading);
            backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            animation: toastIn 0.4s var(--spring);
            max-width: 420px;
        }
        .toast-ok {
            background: rgba(52, 211, 153, 0.9); border: 1px solid var(--green-border);
            box-shadow: 0 8px 30px var(--green-glow);
        }
        .toast-err {
            background: rgba(244, 63, 94, 0.9); border: 1px solid var(--red-border);
            box-shadow: 0 8px 30px var(--red-glow);
        }
        @keyframes toastIn {
            from { opacity: 0; transform: translateY(20px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ═══════════════════════════════════════════════
           SPINNER
           ═══════════════════════════════════════════════ */
        .spin {
            width: 16px; height: 16px;
            border: 2px solid rgba(255,255,255,0.2);
            border-top-color: currentColor; border-radius: 50%;
            animation: sp 0.6s linear infinite;
            display: inline-block; vertical-align: middle;
        }
        @keyframes sp { to { transform: rotate(360deg); } }

        /* ═══════════════════════════════════════════════
           MISC
           ═══════════════════════════════════════════════ */
        .last-updated {
            font-size: 11px; color: var(--text-dim); text-align: right;
            margin-top: -16px; margin-bottom: 16px; font-weight: 500;
        }
        .divider {
            height: 1px; background: var(--border-glass); margin: 16px 0;
        }

        /* Entrance animations for staggered load */
        .stagger { opacity: 0; animation: staggerIn 0.5s ease forwards; }
        .stagger:nth-child(1) { animation-delay: 0.05s; }
        .stagger:nth-child(2) { animation-delay: 0.1s; }
        .stagger:nth-child(3) { animation-delay: 0.15s; }
        .stagger:nth-child(4) { animation-delay: 0.2s; }
        @keyframes staggerIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border-glass-hover); border-radius: 99px; }
    </style>
</head>
<body>

<!-- Animated Background -->
<div class="bg-mesh"></div>
<div class="particles" id="particles"></div>

<!-- ═══ Header ═══ -->
<header class="header">
    <div class="header-content">
        <div class="brand-section">
            <img src="/static/weblogo.png" alt="JS" class="logo" onerror="this.style.display='none'">
            <div class="brand-text">
                <h1>JobScout-AI</h1>
                <span class="version">Command Center</span>
            </div>
        </div>
        <div class="header-actions">
            <button id="themeToggle" class="icon-btn" onclick="toggleTheme()" title="Toggle Theme">
                <span id="themeIcon">☀️</span>
            </button>
            <div id="pill" class="status-pill active" onclick="toggleStatus()">
                <span class="dot"></span><span id="pillTxt">Active</span>
            </div>
            <button class="btn btn-primary" id="btnReport" onclick="sendReport(this)">
                <span>📧</span> <span class="btn-label">Send Report</span>
            </button>
        </div>
    </div>
</header>

<!-- ═══ Main Layout ═══ -->
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
            <div class="stat-card glass stagger">
                <span class="stat-icon">📋</span>
                <span class="stat-lbl">Pending Today</span>
                <span class="stat-val" id="sP" data-target="0">—</span>
            </div>
            <div class="stat-card glass stagger">
                <span class="stat-icon">📥</span>
                <span class="stat-lbl">Total Scraped</span>
                <span class="stat-val" id="sT" data-target="0">—</span>
            </div>
            <div class="stat-card glass stagger">
                <span class="stat-icon">📧</span>
                <span class="stat-lbl">Digests Sent</span>
                <span class="stat-val" id="sD" data-target="0">—</span>
            </div>
            <div class="stat-card glass stagger">
                <span class="stat-icon">🌐</span>
                <span class="stat-lbl">Job Sources</span>
                <span class="stat-val" id="sS">4</span>
            </div>
        </div>
        <div class="last-updated" id="lastUpdated"></div>

        <!-- ═══ Profile Panel ═══ -->
        <div id="p-profile" class="panel on">
            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">📧</span><h2 class="card-title">Identity</h2>
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

            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">🎯</span><h2 class="card-title">Job Sectors</h2>
                </div>
                <p class="card-desc">Select the government sectors you're interested in.</p>
                <div class="chips" id="chipBox"></div>
            </div>

            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">💼</span><h2 class="card-title">Experience Level</h2>
                </div>
                <div class="radios" id="expBox"></div>
            </div>

            <div style="margin-top: 12px;">
                <button class="btn btn-primary" onclick="saveProfile()" id="btnSave">
                    💾 Save Profile
                </button>
            </div>
        </div>

        <!-- ═══ Schedule Panel ═══ -->
        <div id="p-schedule" class="panel">
            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">📅</span><h2 class="card-title">Digest Schedule</h2>
                </div>
                <p class="card-desc">You receive <strong>two professional PDF digests</strong> daily with all matched government jobs, delivered right to your inbox.</p>
                <div class="sched-grid">
                    <div class="sched glass">
                        <div style="font-size:36px;">🌅</div>
                        <div class="sched-time">10:00 AM</div>
                        <div class="sched-lbl">Morning Digest</div>
                    </div>
                    <div class="sched glass">
                        <div style="font-size:36px;">🌇</div>
                        <div class="sched-time">6:00 PM</div>
                        <div class="sched-lbl">Evening Digest</div>
                    </div>
                </div>
            </div>

            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">🔔</span><h2 class="card-title">Deadline Reminders</h2>
                </div>
                <p class="card-desc" style="margin-bottom:0;">Automatic reminders are sent at <strong>3 days</strong>, <strong>1 day</strong>, and the <strong>last day</strong> of application deadlines.</p>
            </div>

            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">⚙️</span><h2 class="card-title">System Status</h2>
                </div>
                <div id="schedStatus" style="font-size:14px;color:var(--text-main);">Checking...</div>
            </div>
        </div>

        <!-- ═══ Resume Panel ═══ -->
        <div id="p-resume" class="panel">
            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">📄</span><h2 class="card-title">Upload Resume</h2>
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
            <div class="card glass" id="resumeCard" style="display:none;">
                <div class="card-header">
                    <span class="card-icon">✅</span><h2 class="card-title">Resume on File</h2>
                </div>
                <div id="resumeInfo" style="font-size:14px;color:var(--text-main);line-height:1.7;"></div>
            </div>
        </div>

        <!-- ═══ History Panel ═══ -->
        <div id="p-history" class="panel">
            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">📬</span><h2 class="card-title">Digest History</h2>
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

            <div class="card glass" style="margin-top:20px;">
                <div class="card-header">
                    <span class="card-icon">📬</span><h2 class="card-title">Brevo Email Status</h2>
                </div>
                <div id="brevoStatus" style="font-size:14px;color:var(--text-main);margin-bottom:16px;">Click to check...</div>
                <button class="btn btn-outline" onclick="verifyBrevo()">🔍 Check Connection</button>
            </div>

            <div class="card glass">
                <div class="card-header">
                    <span class="card-icon">🔗</span><h2 class="card-title">Quick Links</h2>
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;">
                    <a href="/health" target="_blank" class="quick-link">🩺 Health Check →</a>
                    <a href="/api/profile" target="_blank" class="quick-link">📊 Profile JSON →</a>
                    <a href="/api/digest-status" target="_blank" class="quick-link">📋 Digest Status →</a>
                    <a href="/api/debug" target="_blank" class="quick-link">🔬 Pipeline Debug →</a>
                </div>
            </div>
        </div>

    </div>
</main>

<script>
/* ═══════════════════════════════════════════════════════
   THEME
   ═══════════════════════════════════════════════════════ */
(function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
})();

function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon();
}
function updateThemeIcon() {
    const el = document.getElementById('themeIcon');
    if (el) el.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
}

/* ═══════════════════════════════════════════════════════
   PARTICLES
   ═══════════════════════════════════════════════════════ */
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 4 + 2;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = (Math.random() * 20 + 15) + 's';
        p.style.animationDelay = (Math.random() * 15) + 's';
        container.appendChild(p);
    }
}

/* ═══════════════════════════════════════════════════════
   DATA + STATE
   ═══════════════════════════════════════════════════════ */
const INTERESTS = [
    {n:"PSU",e:"🏭"},{n:"Banking",e:"🏦"},{n:"Railways",e:"🚂"},{n:"Defence",e:"🎖️"},
    {n:"IT/Software",e:"💻"},{n:"SSC",e:"📊"},{n:"UPSC",e:"🏛️"},{n:"Teaching",e:"📚"},
    {n:"State Govt",e:"🏘️"},{n:"Judiciary",e:"⚖️"},{n:"Medical",e:"🏥"}
];
const EXPS = ["Fresher", "0-2 yrs", "2+ yrs"];
let selInt = [], selExp = "Fresher", curSt = "active";

/* ═══════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
    updateThemeIcon();
    createParticles();
    renderChips(); renderExps();
    loadProfile(); loadStats(); loadScheduler();
    updateTimestamp();
});

/* ═══════════════════════════════════════════════════════
   NAVIGATION
   ═══════════════════════════════════════════════════════ */
function tab(id, el) {
    document.querySelectorAll(".nav-item").forEach(t => t.classList.remove("on"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("on"));
    el.classList.add("on");
    document.getElementById("p-" + id).classList.add("on");
    if (id === "history") loadHistory();
    if (id === "schedule") loadScheduler();
    if (id === "actions") verifyBrevo();
}

/* ═══════════════════════════════════════════════════════
   CHIPS + EXPERIENCE
   ═══════════════════════════════════════════════════════ */
function renderChips() {
    document.getElementById("chipBox").innerHTML = INTERESTS.map(i =>
        `<div class="chip ${selInt.includes(i.n)?'sel':''}" onclick="togChip('${i.n}',this)">${i.e} ${i.n}</div>`
    ).join("");
}
function togChip(n, el) {
    if (selInt.includes(n)) { selInt = selInt.filter(x => x !== n); el.classList.remove("sel"); }
    else { selInt.push(n); el.classList.add("sel"); }
}
function renderExps() {
    document.getElementById("expBox").innerHTML = EXPS.map(e =>
        `<div class="radio ${selExp===e?'sel':''}" onclick="selE('${e}',this)">${e}</div>`
    ).join("");
}
function selE(e, el) {
    selExp = e;
    document.querySelectorAll("#expBox .radio").forEach(r => r.classList.remove("sel"));
    el.classList.add("sel");
}

/* ═══════════════════════════════════════════════════════
   API HELPERS
   ═══════════════════════════════════════════════════════ */
async function safeJson(r) {
    if (!r.ok) return { _error: true, status: r.status };
    const ct = r.headers.get("content-type");
    if (ct && ct.includes("application/json")) return await r.json();
    return { _error: true, message: "Server returned non-JSON response." };
}

/* ═══════════════════════════════════════════════════════
   LOAD PROFILE
   ═══════════════════════════════════════════════════════ */
async function loadProfile() {
    try {
        const r = await fetch("/api/profile");
        if (!r.ok) { if (r.status !== 404) toast("Failed to load profile", "err"); return; }
        const p = await safeJson(r);
        if (p._error) return;
        document.getElementById("iEmail").value = p.email || "";
        document.getElementById("iQual").value = p.qualification || "";
        selInt = p.interests || []; selExp = p.experience_level || "Fresher"; curSt = p.status || "active";
        renderChips(); renderExps(); updatePill();
        if (p.resume_url) {
            document.getElementById("resumeCard").style.display = "block";
            document.getElementById("resumeInfo").innerHTML =
                `<strong>📎 Resume uploaded</strong><br>Qualification: ${p.qualification||"—"}<br>Experience: ${p.experience_level||"—"}`;
        }
    } catch(e) { console.error(e); }
}

/* ═══════════════════════════════════════════════════════
   LOAD STATS (with animated counters)
   ═══════════════════════════════════════════════════════ */
async function loadStats() {
    try {
        const r = await fetch("/api/stats"); if (!r.ok) return;
        const s = await safeJson(r); if (s._error) return;
        animateCounter("sP", s.pending_today ?? 0);
        animateCounter("sT", s.total_jobs ?? 0);
        animateCounter("sD", s.digests_sent ?? 0);
        updateTimestamp();
    } catch(e) {}
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    target = parseInt(target) || 0;
    el.setAttribute("data-target", target);
    if (target === 0) { el.textContent = "0"; return; }
    let current = 0;
    const step = Math.max(1, Math.ceil(target / 30));
    const interval = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(interval); }
        el.textContent = current.toLocaleString();
    }, 30);
}

function updateTimestamp() {
    const now = new Date();
    const ts = now.toLocaleString('en-IN', { timeZone:'Asia/Kolkata', hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:true, day:'2-digit', month:'short' });
    const el = document.getElementById('lastUpdated');
    if (el) el.textContent = 'Last refreshed: ' + ts;
}

/* ═══════════════════════════════════════════════════════
   LOAD HISTORY
   ═══════════════════════════════════════════════════════ */
async function loadHistory() {
    try {
        const r = await fetch("/api/digest-history");
        if (!r.ok) { document.getElementById("histList").innerHTML = "<p style='color:var(--text-muted);text-align:center;padding:30px;'>No history yet.</p>"; return; }
        const h = await safeJson(r); if (h._error) throw new Error("Invalid format");
        if (!h.length) { document.getElementById("histList").innerHTML = "<p style='color:var(--text-muted);text-align:center;padding:30px;'>No digests sent yet. Jobs are collected and emailed at 10 AM & 6 PM IST.</p>"; return; }
        document.getElementById("histList").innerHTML = h.map(i => `
            <div class="hist"><div><div class="hist-date">📧 ${i.date}</div><div class="hist-meta">${i.job_count} jobs • ${i.type||"Digest"}</div></div>
            <span class="badge ${i.sent?'badge-ok':'badge-wait'}">${i.sent?'✅ Sent':'⏳ Pending'}</span></div>`).join("");
    } catch(e) { document.getElementById("histList").innerHTML = "<p style='color:var(--red);text-align:center;'>Could not load history.</p>"; }
}

/* ═══════════════════════════════════════════════════════
   LOAD SCHEDULER
   ═══════════════════════════════════════════════════════ */
async function loadScheduler() {
    try {
        const r = await fetch("/api/scheduler-status"); const d = await safeJson(r);
        if (d._error) throw new Error("Format error");
        if (d.running) {
            let html = "<div style='color:var(--green);font-weight:700;margin-bottom:12px;font-family:var(--font-heading);'>● Running</div>";
            d.jobs.forEach(j => {
                html += `<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-glass);font-size:13px;'><span style='font-weight:600;'>${j.name}</span><span style='color:var(--text-muted);font-size:12px;'>${j.next_run}</span></div>`;
            });
            document.getElementById("schedStatus").innerHTML = html;
        } else {
            document.getElementById("schedStatus").innerHTML = "<span style='color:var(--amber);font-weight:600;'>⚠️ Scheduler not running (serverless mode)</span>";
        }
    } catch(e) { document.getElementById("schedStatus").innerHTML = "<span style='color:var(--text-muted);'>Could not fetch status</span>"; }
}

/* ═══════════════════════════════════════════════════════
   SAVE PROFILE
   ═══════════════════════════════════════════════════════ */
async function saveProfile() {
    const e = document.getElementById("iEmail").value.trim();
    const q = document.getElementById("iQual").value.trim();
    if (!e || !q) { toast("Email and Qualification required", "err"); return; }
    if (!selInt.length) { toast("Select at least one interest", "err"); return; }
    const btn = document.getElementById("btnSave");
    btn.innerHTML = '<span class="spin"></span> Saving...'; btn.disabled = true;
    try {
        const r = await fetch("/api/profile", { method: "POST", headers: {"Content-Type":"application/json"},
            body: JSON.stringify({ email:e, qualification:q, interests:selInt, experience_level:selExp })
        });
        if (r.ok) { toast("Profile saved successfully! ✅", "ok"); loadStats(); }
        else {
            const ct = r.headers.get("content-type");
            if (ct && ct.includes("application/json")) { const d = await r.json(); toast(d.error || "Save failed", "err"); }
            else toast("Save failed (Server error)", "err");
        }
    } catch(x) { toast("Network error", "err"); }
    btn.innerHTML = "💾 Save Profile"; btn.disabled = false;
}

/* ═══════════════════════════════════════════════════════
   TOGGLE STATUS
   ═══════════════════════════════════════════════════════ */
async function toggleStatus() {
    const ns = curSt === "active" ? "paused" : "active";
    try {
        const r = await fetch("/api/status", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({status:ns}) });
        if (r.ok) { curSt = ns; updatePill(); toast(ns === "active" ? "Notifications resumed! 🔔" : "Notifications paused ⏸️", "ok"); }
        else toast("Failed to update status", "err");
    } catch(e) { toast("Failed to update", "err"); }
}
function updatePill() {
    const p = document.getElementById("pill"), t = document.getElementById("pillTxt");
    const ti = document.getElementById("actToggleIcon"), tt = document.getElementById("actToggle");
    if (curSt === "active") { p.className = "status-pill active"; t.textContent = "Active"; if(ti)ti.textContent="⏸️"; if(tt)tt.textContent="Pause Notifications"; }
    else { p.className = "status-pill paused"; t.textContent = "Paused"; if(ti)ti.textContent="▶️"; if(tt)tt.textContent="Resume Notifications"; }
}

/* ═══════════════════════════════════════════════════════
   TEST EMAIL
   ═══════════════════════════════════════════════════════ */
async function testEmail(card) {
    const t = document.getElementById("actTest");
    const orig = t.innerHTML;
    const e = document.getElementById("iEmail").value.trim();
    if (!e) { toast("Please enter an email in the Profile section first", "err"); return; }
    t.innerHTML = '<span class="spin"></span> Sending...';
    try {
        const r = await fetch("/api/test-email?email=" + encodeURIComponent(e));
        if (r.ok) { const d = await safeJson(r); toast(`Test email sent to ${d.email||''}! Check your inbox 📧`, "ok"); }
        else {
            const ct = r.headers.get("content-type");
            if (ct && ct.includes("application/json")) {
                const d = await r.json(); const err = d.error || "Email failed";
                if (err.includes('IP_BLOCKED')) toast('❌ IP blocked by Brevo. Disable IP restriction.', 'err');
                else if (err.includes('INVALID_API_KEY')) toast('❌ Brevo API key is invalid.', 'err');
                else if (err.includes('SENDER_NOT_VERIFIED')) toast('❌ Sender email not verified in Brevo.', 'err');
                else if (err.includes('RATE_LIMITED')) toast('❌ Daily email limit reached. Try tomorrow.', 'err');
                else toast(err, 'err');
            } else toast("Server error sending email", "err");
        }
    } catch(e) { toast("Network error", "err"); }
    t.innerHTML = orig;
}

/* ═══════════════════════════════════════════════════════
   VERIFY BREVO
   ═══════════════════════════════════════════════════════ */
async function verifyBrevo() {
    const el = document.getElementById('brevoStatus');
    el.innerHTML = '<span class="spin"></span> Checking Brevo connection...';
    try {
        const r = await fetch('/api/verify-brevo'); const d = await r.json();
        if (d.status === 'ok') {
            el.innerHTML = `<div style='color:var(--green);font-weight:700;margin-bottom:8px;font-family:var(--font-heading);'>✅ Connected</div>`
                + `<div style='display:grid;gap:6px;font-size:13px;'>`
                + `<div>📧 Account: <strong>${d.account}</strong></div>`
                + `<div>📋 Plan: <strong>${d.plan}</strong> (${d.credits} emails/day)</div>`
                + `<div>✅ Sender: <strong>${d.sender_email}</strong> (verified)</div>`
                + `</div>`;
        } else {
            const err = d.error || 'Unknown error'; let hint = '';
            if (err.includes('IP')) hint = '<br><a href="https://app.brevo.com/security/authorised_ips" target="_blank" style="color:var(--primary);">Fix: Disable IP restriction →</a>';
            else if (err.includes('API KEY')) hint = '<br>Fix: Generate new API key at Brevo dashboard';
            else if (err.includes('SENDER')) hint = '<br><a href="https://app.brevo.com/senders/list" target="_blank" style="color:var(--primary);">Fix: Verify sender email →</a>';
            el.innerHTML = `<div style='color:var(--red);font-weight:700;margin-bottom:8px;'>❌ Error</div><div style='font-size:13px;color:var(--text-muted);word-break:break-word;'>${err}${hint}</div>`;
        }
    } catch(e) { el.innerHTML = '<span style="color:var(--red);">❌ Could not reach server</span>'; }
}

/* ═══════════════════════════════════════════════════════
   TRIGGER DIGEST
   ═══════════════════════════════════════════════════════ */
async function triggerDigest(card) {
    const t = document.getElementById("actDigest"); const orig = t.innerHTML;
    t.innerHTML = '<span class="spin"></span> Sending...';
    try {
        const r = await fetch("/api/trigger-digest");
        if (r.ok) {
            const d = await safeJson(r);
            if (d.status === "skipped") toast(d.message || "No pending jobs to digest", "ok");
            else toast(`Digest sent! ${d.jobs||0} jobs emailed to ${d.email||''} 📧`, "ok");
            loadHistory(); loadStats();
        } else {
            const ct = r.headers.get("content-type");
            if (ct && ct.includes("application/json")) { const d = await r.json(); toast(d.error||"Failed","err"); }
            else toast("Server error generating digest", "err");
        }
    } catch(e) { toast("Network error", "err"); }
    t.innerHTML = orig;
}

/* ═══════════════════════════════════════════════════════
   SEND REPORT (Header Button)
   ═══════════════════════════════════════════════════════ */
async function sendReport(btn) {
    btn.disabled = true; const origHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spin"></span> <span class="btn-label">Sending...</span>';
    try {
        const r = await fetch("/api/trigger-digest");
        if (r.ok) {
            const d = await safeJson(r);
            if (d.status === "skipped") {
                toast(d.message || "No pending jobs — digest queue is empty", "ok");
                btn.innerHTML = '✅ <span class="btn-label">No Pending Jobs</span>';
            } else {
                toast(`PDF Report sent! ${d.jobs||0} jobs emailed to ${d.email||''} 📧`, "ok");
                btn.innerHTML = '✅ <span class="btn-label">Report Sent!</span>';
            }
            loadStats(); loadHistory();
        } else {
            const ct = r.headers.get("content-type");
            if (ct && ct.includes("application/json")) { const d = await r.json(); toast(d.error||"Send failed","err"); }
            else toast("Server error sending report", "err");
            btn.innerHTML = '❌ <span class="btn-label">Failed</span>';
        }
    } catch(e) { toast("Network error","err"); btn.innerHTML = '❌ <span class="btn-label">Error</span>'; }
    setTimeout(() => { btn.innerHTML = origHTML; btn.disabled = false; }, 3000);
}

/* ═══════════════════════════════════════════════════════
   TRIGGER SCRAPE
   ═══════════════════════════════════════════════════════ */
async function triggerScrape(card) {
    const t = document.getElementById("actScrape"); const orig = t.innerHTML;
    t.innerHTML = '<span class="spin"></span> Scraping...';
    try {
        const r = await fetch("/api/trigger-scrape");
        if (r.ok) { toast("Scraper triggered! Running in background...", "ok"); loadStats(); }
        else if (r.status === 429) { const d = await safeJson(r); toast(d.error||"Already running","err"); }
        else { toast("Error triggering scraper", "err"); }
    } catch(e) { toast("Network error", "err"); }
    setTimeout(() => { t.innerHTML = orig; }, 2000);
}

/* ═══════════════════════════════════════════════════════
   RESUME UPLOAD
   ═══════════════════════════════════════════════════════ */
async function uploadResume(ev) {
    let files;
    if (ev.target && ev.target.files) files = ev.target.files;
    else if (ev.dataTransfer && ev.dataTransfer.files) files = ev.dataTransfer.files;
    const f = files ? files[0] : null;
    if (!f) return;
    if (f.size > 5*1024*1024) { toast("File too large (max 5MB)", "err"); return; }
    const s = document.getElementById("upStatus");
    s.style.display = "block";
    s.innerHTML = '<span class="spin"></span> Uploading & analyzing...';
    const fd = new FormData(); fd.append("file", f);
    try {
        const r = await fetch("/api/resume", { method: "POST", body: fd });
        if (r.ok) {
            s.innerHTML = "<span style='color:var(--green);font-weight:600;'>✅ Resume uploaded & analyzed!</span>";
            toast("Resume uploaded! Profile updated.", "ok");
            loadProfile();
        } else {
            const ct = r.headers.get("content-type");
            if (ct && ct.includes("application/json")) { const d = await r.json(); s.innerHTML = `<span style='color:var(--red);'>❌ ${d.error||'Failed'}</span>`; }
            else s.innerHTML = `<span style='color:var(--red);'>❌ Server error</span>`;
        }
    } catch(e) { s.innerHTML = "<span style='color:var(--red);'>❌ Network error</span>"; }
}

// Drag & Drop
const z = document.getElementById("upZone");
if (z) {
    z.addEventListener("dragover", e => { e.preventDefault(); z.classList.add("over"); });
    z.addEventListener("dragleave", () => z.classList.remove("over"));
    z.addEventListener("drop", e => {
        e.preventDefault(); z.classList.remove("over");
        if (e.dataTransfer && e.dataTransfer.files) uploadResume(e);
    });
}

/* ═══════════════════════════════════════════════════════
   TOAST
   ═══════════════════════════════════════════════════════ */
function toast(m, t) {
    const old = document.querySelector(".toast"); if (old) old.remove();
    const d = document.createElement("div");
    d.className = `toast toast-${t==='ok'?'ok':'err'}`;
    d.textContent = m;
    document.body.appendChild(d);
    setTimeout(() => d.remove(), 4000);
}
</script>
</body>
</html>
'''
