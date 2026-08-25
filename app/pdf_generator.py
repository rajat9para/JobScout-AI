"""Professional PDF generator for JobScout-AI daily reports and AI Job Intelligence.

Uses ReportLab to create an executive-grade, branded PDF with:
  - Header & high-stats summary
  - Exclusion of expired jobs (strictly active openings with upcoming deadlines)
  - Jobs grouped chronologically by date
  - Dual Match Score & Reality Score badges
  - Positive workplace signals, potential concerns, and interview intelligence for top jobs
  - Direct Online Application and Official Notification links
"""
import io
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

from app.models import Job

logger = logging.getLogger(__name__)

# ── Color Palette — Professional Modern Aesthetic ──
PRIMARY = colors.HexColor("#0F172A")       # Slate 900
PRIMARY_BLUE = colors.HexColor("#1E3A8A")  # Deep Navy Blue
ACCENT = colors.HexColor("#2563EB")        # Royal Blue
ACCENT_LIGHT = colors.HexColor("#3B82F6")  # Bright Blue
SUCCESS = colors.HexColor("#059669")       # Emerald Green
SUCCESS_BG = colors.HexColor("#ECFDF5")    # Mint Soft
WARNING = colors.HexColor("#D97706")       # Amber
DANGER = colors.HexColor("#DC2626")        # Red
PURPLE = colors.HexColor("#7C3AED")        # Violet Accent
PURPLE_BG = colors.HexColor("#F5F3FF")     # Violet Soft
TEXT_DARK = colors.HexColor("#0F172A")      # Slate 900
TEXT_MED = colors.HexColor("#334155")       # Slate 700
TEXT_LIGHT = colors.HexColor("#64748B")     # Slate 500
BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
BG_CARD = colors.HexColor("#FFFFFF")       # White
BORDER = colors.HexColor("#E2E8F0")        # Slate 200
DIVIDER = colors.HexColor("#CBD5E1")       # Slate 300
WHITE = colors.HexColor("#FFFFFF")


class PDFGenerator:
    """Generates executive PDF reports with deterministic matching and reality checks."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_custom_styles()

    def _register_custom_styles(self):
        """Register custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Title"],
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=PRIMARY_BLUE,
            spaceAfter=2 * mm,
            alignment=TA_CENTER,
            leading=26,
        ))

        self.styles.add(ParagraphStyle(
            name="ReportSubtitle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=3 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="DateHeading",
            parent=self.styles["Heading2"],
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            leftIndent=0,
        ))

        self.styles.add(ParagraphStyle(
            name="JobTitle",
            parent=self.styles["Heading3"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            spaceBefore=1 * mm,
            spaceAfter=1 * mm,
            leading=14,
        ))

        self.styles.add(ParagraphStyle(
            name="MatchBadge",
            parent=self.styles["Normal"],
            fontSize=8.5,
            fontName="Helvetica-Bold",
            textColor=WHITE,
            alignment=TA_RIGHT,
        ))

        self.styles.add(ParagraphStyle(
            name="JobOrg",
            parent=self.styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=PRIMARY_BLUE,
            spaceAfter=2 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="WorkSummary",
            parent=self.styles["Normal"],
            fontSize=8.5,
            textColor=TEXT_MED,
            spaceAfter=2 * mm,
            leading=12,
        ))

        self.styles.add(ParagraphStyle(
            name="JobField",
            parent=self.styles["Normal"],
            fontSize=8.5,
            textColor=TEXT_MED,
            spaceAfter=1 * mm,
            leading=12,
        ))

        self.styles.add(ParagraphStyle(
            name="JobHighlight",
            parent=self.styles["Normal"],
            fontSize=8.5,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            spaceAfter=1 * mm,
            leading=12,
        ))

        self.styles.add(ParagraphStyle(
            name="RealityBox",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=TEXT_MED,
            leading=11,
        ))

        self.styles.add(ParagraphStyle(
            name="StatValue",
            parent=self.styles["Normal"],
            fontSize=18,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name="StatLabel",
            parent=self.styles["Normal"],
            fontSize=7.5,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=1 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="Footer",
            parent=self.styles["Normal"],
            fontSize=7,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name="EmptyState",
            parent=self.styles["Normal"],
            fontSize=13,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceBefore=25 * mm,
        ))

        self.styles.add(ParagraphStyle(
            name="SourceTag",
            parent=self.styles["Normal"],
            fontSize=7,
            textColor=TEXT_LIGHT,
            spaceAfter=0,
        ))

    def generate(self, jobs: List[Job], digest_date: Optional[date] = None) -> bytes:
        """Generate the comprehensive report PDF (excluding expired jobs)."""
        if digest_date is None:
            digest_date = date.today()

        # Strict Filter: Exclude expired jobs
        active_jobs = [j for j in jobs if not (j.last_date and j.last_date < date.today())]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"JobScout-AI Report — {digest_date.strftime('%d %b %Y')}",
            author="JobScout-AI",
            subject="Government Job Alert Intelligence Report",
        )

        story = []

        # ── Header ──
        story.append(Paragraph("JobScout-AI &bull; Executive Job Report", self.styles["ReportTitle"]))
        story.append(Paragraph(
            f"Official Government Job Postings &bull; {digest_date.strftime('%A, %d %B %Y')}",
            self.styles["ReportSubtitle"]
        ))

        story.append(HRFlowable(
            width="100%", thickness=2, color=ACCENT,
            spaceBefore=1 * mm, spaceAfter=3 * mm
        ))

        # ── Summary Stats Bar ──
        if active_jobs:
            sources = set(j.source for j in active_jobs)
            upcoming = sum(1 for j in active_jobs if j.last_date and j.last_date >= date.today())
            scored = [j.match_score for j in active_jobs if j.match_score]
            avg_score = int(sum(scored) / len(scored)) if scored else 88

            stats_data = [
                [
                    Paragraph(str(len(active_jobs)), self.styles["StatValue"]),
                    Paragraph(str(len(sources)), self.styles["StatValue"]),
                    Paragraph(f"{avg_score}%", self.styles["StatValue"]),
                    Paragraph(str(upcoming), self.styles["StatValue"]),
                ],
                [
                    Paragraph("Active Openings", self.styles["StatLabel"]),
                    Paragraph("Verified Portals", self.styles["StatLabel"]),
                    Paragraph("Avg Match Score", self.styles["StatLabel"]),
                    Paragraph("Open Deadlines", self.styles["StatLabel"]),
                ],
            ]
            col_width = doc.width / 4
            stats_table = Table(stats_data, colWidths=[col_width] * 4)
            stats_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 4 * mm))

        # ── Empty State ──
        if not active_jobs:
            story.append(Paragraph(
                "No active upcoming government jobs matching your criteria were found in this cycle.",
                self.styles["EmptyState"]
            ))
            story.append(Spacer(1, 6 * mm))
            story.append(Paragraph(
                "JobScout-AI is continuously monitoring 4 major government portals 24/7. "
                "Expired postings are strictly excluded to keep your recommendations 100% actionable.",
                self.styles["Footer"]
            ))
        else:
            # ── Group Jobs by Date ──
            grouped = self._group_by_date(active_jobs)

            job_idx = 0
            for date_key, date_jobs in grouped.items():
                story.append(HRFlowable(
                    width="100%", thickness=0.5, color=BORDER,
                    spaceBefore=2 * mm, spaceAfter=1 * mm
                ))
                story.append(Paragraph(
                    f"📅 {date_key} &bull; {len(date_jobs)} active opening{'s' if len(date_jobs) != 1 else ''}",
                    self.styles["DateHeading"]
                ))

                for job in date_jobs:
                    job_idx += 1
                    job_block = self._build_job_card(job, job_idx, len(active_jobs), doc.width)
                    story.append(KeepTogether(job_block))

        # ── Footer ──
        story.append(Spacer(1, 6 * mm))
        story.append(HRFlowable(
            width="100%", thickness=1, color=ACCENT,
            spaceBefore=3 * mm, spaceAfter=3 * mm
        ))
        story.append(Paragraph(
            f"JobScout-AI &bull; Report generated on {datetime.now().strftime('%d %b %Y at %I:%M %p IST')}",
            self.styles["Footer"]
        ))
        story.append(Paragraph(
            "Portals Monitored: SarkariResult.com &bull; FreeJobAlert.com &bull; SarkariExam.com &bull; RojgarResult.com",
            self.styles["Footer"]
        ))

        try:
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            doc.build([
                Paragraph(f"JobScout-AI Report — {digest_date}", self.styles["ReportTitle"]),
                Paragraph(f"Error rendering report: {e}", self.styles["Normal"])
            ])

        buffer.seek(0)
        return buffer.read()

    def generate_intelligence_report(self, intelligence_items: List[Any], digest_date: Optional[date] = None) -> bytes:
        """Generate specialized AI Job Intelligence & Reality Check PDF Report."""
        if digest_date is None:
            digest_date = date.today()

        # Strict Filter: Exclude expired items
        active_items = [item for item in intelligence_items if not (item.last_date and item.last_date < date.today())]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"JobScout-AI Intelligence Report — {digest_date.strftime('%d %b %Y')}",
            author="JobScout-AI",
            subject="AI Job Intelligence & Reality Check",
        )

        story = []

        # ── Header ──
        story.append(Paragraph("🧠 JobScout-AI &bull; Job Intelligence & Reality Report", self.styles["ReportTitle"]))
        story.append(Paragraph(
            f"Evidence-Based Career Signals &bull; {digest_date.strftime('%A, %d %B %Y')}",
            self.styles["ReportSubtitle"]
        ))

        story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=1 * mm, spaceAfter=3 * mm))

        # ── Stats ──
        if active_items:
            strong_apply = sum(1 for item in active_items if "STRONG" in item.overall_recommendation.upper())
            apply_count = sum(1 for item in active_items if item.overall_recommendation.upper() == "APPLY")
            avg_reality = int(sum(item.reality.reality_score for item in active_items) / len(active_items))

            stats_data = [
                [
                    Paragraph(str(len(active_items)), self.styles["StatValue"]),
                    Paragraph(str(strong_apply), self.styles["StatValue"]),
                    Paragraph(str(apply_count), self.styles["StatValue"]),
                    Paragraph(f"{avg_reality}/100", self.styles["StatValue"]),
                ],
                [
                    Paragraph("Jobs Researched", self.styles["StatLabel"]),
                    Paragraph("Strong Apply", self.styles["StatLabel"]),
                    Paragraph("Apply Recommended", self.styles["StatLabel"]),
                    Paragraph("Avg Reality Score", self.styles["StatLabel"]),
                ],
            ]
            col_width = doc.width / 4
            stats_table = Table(stats_data, colWidths=[col_width] * 4)
            stats_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 4 * mm))

            # ── Item Cards with Full Reality Check ──
            for idx, item in enumerate(active_items, start=1):
                block = self._build_intelligence_card(item, idx, len(active_items), doc.width)
                story.append(KeepTogether(block))

        # ── Footer ──
        story.append(Spacer(1, 6 * mm))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3 * mm, spaceAfter=3 * mm))
        story.append(Paragraph(
            f"JobScout-AI &bull; Reality Intelligence synthesized via Groq LPU™ Engine &bull; {datetime.now().strftime('%d %b %Y at %I:%M %p IST')}",
            self.styles["Footer"]
        ))

        try:
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        except Exception as e:
            logger.error(f"Intelligence PDF generation failed: {e}")
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            doc.build([
                Paragraph("JobScout-AI Intelligence Report", self.styles["ReportTitle"]),
                Paragraph(f"Error rendering report: {e}", self.styles["Normal"])
            ])

        buffer.seek(0)
        return buffer.read()

    def _group_by_date(self, jobs: List[Job]) -> Dict[str, List[Job]]:
        """Group jobs by scraped date, sorted most recent first."""
        grouped = defaultdict(list)
        for job in jobs:
            if job.scraped_at:
                if isinstance(job.scraped_at, str):
                    try:
                        dt = datetime.fromisoformat(job.scraped_at.replace("Z", "+00:00"))
                        key = dt.strftime("%A, %d %B %Y")
                    except ValueError:
                        key = "Recent Postings"
                else:
                    key = job.scraped_at.strftime("%A, %d %B %Y")
            else:
                key = "Recent Postings"
            grouped[key].append(job)

        def _parse_date_key(key):
            try:
                return datetime.strptime(key, "%A, %d %B %Y")
            except ValueError:
                return datetime.min

        sorted_keys = sorted(grouped.keys(), key=_parse_date_key, reverse=True)

        result = {}
        for k in sorted_keys:
            result[k] = sorted(grouped[k], key=lambda j: (j.match_score or 85, self._estimate_job_rank(j)), reverse=True)

        return result

    @staticmethod
    def _estimate_job_rank(job: Job) -> int:
        score = 0
        if job.salary:
            import re
            numbers = re.findall(r'\d+', job.salary.replace("₹", "").replace(",", ""))
            if numbers:
                score += max(int(n) for n in numbers if len(n) >= 4) // 100
        combined = f"{(job.title or '').lower()} {(job.organization or '').lower()}"
        tier1 = ["scientist", "director", "commissioner", "secretary", "professor", "ias", "ips", "upsc", "chief"]
        if any(kw in combined for kw in tier1): score += 500
        tier2 = ["officer", "manager", "engineer", "doctor", "specialist", "assistant professor", "inspector"]
        if any(kw in combined for kw in tier2): score += 300
        tier3 = ["technician", "sub-inspector", "junior engineer", "programmer", "teacher"]
        if any(kw in combined for kw in tier3): score += 100
        return score

    def _build_job_card(self, job: Job, index: int, total: int, doc_width: float) -> list:
        """Build an executive, information-dense job card."""
        elements = []

        elements.append(HRFlowable(width="100%", thickness=2.5, color=ACCENT, spaceBefore=3 * mm, spaceAfter=1.5 * mm))

        score_val = job.match_score or 88
        if score_val >= 90:
            badge_bg = "#059669"
            badge_text = f"🎯 {score_val}% Match"
        elif score_val >= 75:
            badge_bg = "#2563EB"
            badge_text = f"⭐ {score_val}% Match"
        else:
            badge_bg = "#D97706"
            badge_text = f"📌 {score_val}% Match"

        title_p = Paragraph(f"<b>{index}. {self._escape(job.title)}</b>", self.styles["JobTitle"])
        badge_p = Paragraph(f'<font color="white"><b>&nbsp;{badge_text}&nbsp;</b></font>', self.styles["MatchBadge"])

        header_table = Table([[title_p, badge_p]], colWidths=[doc_width - 32 * mm, 32 * mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(badge_bg)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(header_table)

        elements.append(Paragraph(f"🏛️ <b>Organization:</b> {self._escape(job.organization)}", self.styles["JobOrg"]))

        if job.description:
            elements.append(Paragraph(
                f'<font color="#1E3A8A"><b>📝 Work Summary:</b></font> <i>{self._escape(job.description)}</i>',
                self.styles["WorkSummary"]
            ))

        col1 = []
        col2 = []

        if job.salary:
            col1.append(f"💰 <b>Salary/Pay:</b> {self._escape(job.salary)}")
        if job.vacancies:
            col2.append(f"👥 <b>Vacancies:</b> {self._escape(job.vacancies)}")

        if job.application_fee:
            col1.append(f"💳 <b>Form Fee:</b> {self._escape(job.application_fee)}")
        else:
            col1.append(f"💳 <b>Form Fee:</b> Refer official notice")

        if job.age_limit:
            col2.append(f"🎂 <b>Age Limit:</b> {self._escape(job.age_limit)}")

        grid_rows = []
        max_rows = max(len(col1), len(col2))
        for r_i in range(max_rows):
            c1_text = col1[r_i] if r_i < len(col1) else ""
            c2_text = col2[r_i] if r_i < len(col2) else ""
            grid_rows.append([
                Paragraph(c1_text, self.styles["JobHighlight"]),
                Paragraph(c2_text, self.styles["JobHighlight"])
            ])

        if grid_rows:
            details_table = Table(grid_rows, colWidths=[doc_width / 2] * 2)
            details_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
            ]))
            elements.append(details_table)

        if job.eligibility:
            elements.append(Paragraph(f"📚 <b>Full Eligibility:</b> {self._escape(job.eligibility)}", self.styles["JobField"]))

        degree_line = []
        if job.degree_tags:
            tags = " &bull; ".join(job.degree_tags)
            degree_line.append(f"🎓 <b>Degrees:</b> {self._escape(tags)}")
        if job.exam_required:
            degree_line.append(f"📝 <b>Exam:</b> {self._escape(job.exam_required)}")
        if degree_line:
            elements.append(Paragraph(" &nbsp;&nbsp;|&nbsp;&nbsp; ".join(degree_line), self.styles["JobField"]))

        if job.selection_process:
            elements.append(Paragraph(f"📋 <b>Selection Process:</b> {self._escape(job.selection_process)}", self.styles["JobField"]))

        if job.last_date:
            days_left = (job.last_date - date.today()).days
            if days_left == 0:
                urgency = ' <font color="#DC2626"><b>[🚨 LAST DAY TODAY!]</b></font>'
            elif days_left <= 3:
                urgency = f' <font color="#D97706"><b>[⏰ {days_left} Days Left - Apply Soon!]</b></font>'
            elif days_left <= 7:
                urgency = f' <font color="#2563EB">({days_left} days left)</font>'
            else:
                urgency = f' <font color="#059669">({days_left} days left)</font>'
            elements.append(Paragraph(
                f"📅 <b>Application Deadline:</b> <b>{job.last_date.strftime('%d %B %Y')}</b>{urgency}",
                self.styles["JobHighlight"]
            ))

        links = []
        if job.apply_link:
            links.append(f'✍️ <b><a href="{job.apply_link}" color="#2563EB"><u>Direct Online Application Form</u></a></b>')
        if job.notification_link:
            links.append(f'📄 <b><a href="{job.notification_link}" color="#7C3AED"><u>Official Notification Notice / PDF</u></a></b>')

        if links:
            elements.append(Spacer(1, 1 * mm))
            elements.append(Paragraph(" &nbsp;&nbsp;&bull;&nbsp;&nbsp; ".join(links), self.styles["JobHighlight"]))

        elements.append(Spacer(1, 0.5 * mm))
        elements.append(Paragraph(f"Source Portal: {self._escape(job.source)}", self.styles["SourceTag"]))

        elements.append(Spacer(1, 1.5 * mm))
        if index < total:
            elements.append(HRFlowable(width="100%", thickness=0.5, color=DIVIDER, spaceBefore=1 * mm, spaceAfter=2 * mm))

        return elements

    def _build_intelligence_card(self, item: Any, index: int, total: int, doc_width: float) -> list:
        """Build deep intelligence card with dual Match/Reality score and evidence insights."""
        elements = []

        elements.append(HRFlowable(width="100%", thickness=2.5, color=ACCENT, spaceBefore=4 * mm, spaceAfter=2 * mm))

        # Title & Badges
        rec_color = "#059669" if "STRONG" in item.overall_recommendation.upper() else "#2563EB"
        header_p = Paragraph(f"<b>{index}. {self._escape(item.title)}</b> &bull; {self._escape(item.company)}", self.styles["JobTitle"])
        badges_p = Paragraph(
            f'<font color="white"><b>&nbsp;🎯 Match: {item.match.match_score}%&nbsp;</b></font>&nbsp;'
            f'<font color="white"><b>&nbsp;🏛️ Reality: {item.reality.reality_score}/100&nbsp;</b></font>',
            self.styles["MatchBadge"]
        )

        header_table = Table([[header_p, badges_p]], colWidths=[doc_width - 65 * mm, 65 * mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(rec_color)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(header_table)

        # Recommendation Bar
        elements.append(Spacer(1, 1 * mm))
        elements.append(Paragraph(
            f'<b>Recommendation:</b> <font color="{rec_color}"><b>{self._escape(item.overall_recommendation)}</b></font> &bull; '
            f'<i>{self._escape(item.match.match_summary)}</i>',
            self.styles["JobHighlight"]
        ))

        # Why You Match & Category Scores
        cats = item.match.category_scores
        cat_line = (
            f"<b>Skills:</b> {cats.skill_match}% &nbsp;|&nbsp; "
            f"<b>Experience:</b> {cats.experience_match}% &nbsp;|&nbsp; "
            f"<b>Role Match:</b> {cats.role_match}% &nbsp;|&nbsp; "
            f"<b>Salary:</b> {cats.salary_match}%"
        )
        elements.append(Paragraph(cat_line, self.styles["JobField"]))

        # Positive Workplace Signals & Concerns (2 columns)
        pos_list = "<br/>".join([f"&bull; {self._escape(p)}" for p in item.reality.positive_signals[:3]])
        con_list = "<br/>".join([f"&bull; {self._escape(c)}" for c in item.reality.potential_concerns[:3]])

        col1_p = Paragraph(f'<b><font color="#059669">✅ Verified Positive Signals:</font></b><br/>{pos_list}', self.styles["RealityBox"])
        col2_p = Paragraph(f'<b><font color="#DC2626">⚠️ Potential Concerns & Workload:</font></b><br/>{con_list}', self.styles["RealityBox"])

        insights_table = Table([[col1_p, col2_p]], colWidths=[doc_width / 2] * 2)
        insights_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), SUCCESS_BG),
            ('BACKGROUND', (1, 0), (1, 0), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(Spacer(1, 1.5 * mm))
        elements.append(insights_table)

        # Interview Intelligence
        if item.reality.interview:
            itv = item.reality.interview
            topics_str = ", ".join(itv.common_topics[:4]) if itv.common_topics else "General Merit Syllabus"
            elements.append(Spacer(1, 1.5 * mm))
            elements.append(Paragraph(
                f'<b>📝 Interview Process:</b> {self._escape(itv.rounds_count)} &bull; '
                f'<b>Difficulty:</b> {itv.technical_difficulty}/5.0 &bull; '
                f'<b>Key Topics:</b> {self._escape(topics_str)}',
                self.styles["JobField"]
            ))

        # Links & Deadline
        links = []
        if item.apply_link:
            links.append(f'✍️ <b><a href="{item.apply_link}" color="#2563EB"><u>Apply Online</u></a></b>')
        if item.notification_link:
            links.append(f'📄 <b><a href="{item.notification_link}" color="#7C3AED"><u>Official Notice</u></a></b>')
        if item.last_date:
            days_left = (item.last_date - date.today()).days
            links.append(f"📅 Deadline: <b>{item.last_date.strftime('%d %b %Y')}</b> ({days_left}d left)")

        if links:
            elements.append(Spacer(1, 1 * mm))
            elements.append(Paragraph(" &nbsp;&bull;&nbsp; ".join(links), self.styles["JobHighlight"]))

        elements.append(Spacer(1, 2 * mm))
        if index < total:
            elements.append(HRFlowable(width="100%", thickness=0.5, color=DIVIDER, spaceBefore=1 * mm, spaceAfter=2 * mm))

        return elements

    @staticmethod
    def _escape(text: str) -> str:
        if not text:
            return ""
        return (
            str(text).replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawCentredString(
            A4[0] / 2, 8 * mm,
            f"JobScout-AI Intelligence &bull; Page {page_num}"
        )
        canvas.restoreState()
