"""Professional PDF generator for the JobScout-AI daily report.

Uses ReportLab to create a clean, branded PDF with:
  - "JobScout-AI Daily Report" header
  - Jobs grouped by date (recent first) with date section headings
  - Clean professional cards for each job with key highlights
  - Salary, qualification, experience, apply links prominently shown
"""
import io
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict
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

# ── Color Palette — Professional Dark Blue Theme ──
PRIMARY = colors.HexColor("#1B2A4A")       # Deep navy
ACCENT = colors.HexColor("#3B82F6")        # Bright blue
ACCENT_LIGHT = colors.HexColor("#60A5FA")  # Light blue
SUCCESS = colors.HexColor("#10B981")       # Green
WARNING = colors.HexColor("#F59E0B")       # Amber
DANGER = colors.HexColor("#EF4444")        # Red
TEXT_DARK = colors.HexColor("#1E293B")      # Slate 800
TEXT_MED = colors.HexColor("#475569")       # Slate 600
TEXT_LIGHT = colors.HexColor("#94A3B8")     # Slate 400
BG_LIGHT = colors.HexColor("#F1F5F9")      # Slate 100
BG_CARD = colors.HexColor("#F8FAFC")       # Slate 50
BORDER = colors.HexColor("#E2E8F0")        # Slate 200
DIVIDER = colors.HexColor("#CBD5E1")       # Slate 300
WHITE = colors.HexColor("#FFFFFF")


class PDFGenerator:
    """Generates a professional PDF report of government jobs."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_custom_styles()

    def _register_custom_styles(self):
        """Register custom paragraph styles."""
        # Main report title
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Title"],
            fontSize=24,
            fontName="Helvetica-Bold",
            textColor=PRIMARY,
            spaceAfter=2 * mm,
            alignment=TA_CENTER,
            leading=30,
        ))

        # Report subtitle / date
        self.styles.add(ParagraphStyle(
            name="ReportSubtitle",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=6 * mm,
        ))

        # Date section heading (e.g., "August 20, 2026")
        self.styles.add(ParagraphStyle(
            name="DateHeading",
            parent=self.styles["Heading2"],
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
            spaceBefore=8 * mm,
            spaceAfter=4 * mm,
            leftIndent=0,
            borderPadding=(4, 8, 4, 8),
        ))

        # Job title
        self.styles.add(ParagraphStyle(
            name="JobTitle",
            parent=self.styles["Heading3"],
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            spaceBefore=2 * mm,
            spaceAfter=1 * mm,
            leftIndent=0,
        ))

        # Organization
        self.styles.add(ParagraphStyle(
            name="JobOrg",
            parent=self.styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
            spaceAfter=2 * mm,
        ))

        # Job detail field
        self.styles.add(ParagraphStyle(
            name="JobField",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=TEXT_MED,
            spaceAfter=1 * mm,
            leading=13,
        ))

        # Highlight field (salary, deadline)
        self.styles.add(ParagraphStyle(
            name="JobHighlight",
            parent=self.styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            spaceAfter=1 * mm,
            leading=13,
        ))

        # Summary stat
        self.styles.add(ParagraphStyle(
            name="StatValue",
            parent=self.styles["Normal"],
            fontSize=20,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name="StatLabel",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=2 * mm,
        ))

        # Footer
        self.styles.add(ParagraphStyle(
            name="Footer",
            parent=self.styles["Normal"],
            fontSize=7,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
        ))

        # Empty state
        self.styles.add(ParagraphStyle(
            name="EmptyState",
            parent=self.styles["Normal"],
            fontSize=14,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            spaceBefore=30 * mm,
        ))

        # Source tag
        self.styles.add(ParagraphStyle(
            name="SourceTag",
            parent=self.styles["Normal"],
            fontSize=7,
            textColor=TEXT_LIGHT,
            spaceAfter=0,
        ))

    def generate(self, jobs: List[Job], digest_date: date = None) -> bytes:
        """Generate the report PDF and return as bytes."""
        if digest_date is None:
            digest_date = date.today()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"JobScout-AI Report — {digest_date.strftime('%d %b %Y')}",
            author="JobScout-AI",
            subject="Government Job Report",
        )

        story = []

        # ── Header ──
        story.append(Paragraph("JobScout-AI", self.styles["ReportTitle"]))
        story.append(Paragraph("Daily Government Job Report", self.styles["ReportSubtitle"]))
        story.append(Paragraph(
            f"{digest_date.strftime('%A, %d %B %Y')}",
            self.styles["ReportSubtitle"]
        ))

        # Accent line
        story.append(HRFlowable(
            width="100%", thickness=2, color=ACCENT,
            spaceBefore=2 * mm, spaceAfter=4 * mm
        ))

        # ── Summary Stats Bar ──
        if jobs:
            sources = set(j.source for j in jobs)
            upcoming = sum(1 for j in jobs if j.last_date and j.last_date >= date.today())
            expired = sum(1 for j in jobs if j.last_date and j.last_date < date.today())

            stats_data = [
                [
                    Paragraph(str(len(jobs)), self.styles["StatValue"]),
                    Paragraph(str(len(sources)), self.styles["StatValue"]),
                    Paragraph(str(upcoming), self.styles["StatValue"]),
                ],
                [
                    Paragraph("Total Jobs", self.styles["StatLabel"]),
                    Paragraph("Sources", self.styles["StatLabel"]),
                    Paragraph("Open Deadlines", self.styles["StatLabel"]),
                ],
            ]
            stats_table = Table(stats_data, colWidths=[doc.width / 3] * 3)
            stats_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 6 * mm))

        # ── Empty State ──
        if not jobs:
            story.append(Paragraph(
                "No government jobs found in the last 15 days.",
                self.styles["EmptyState"]
            ))
            story.append(Spacer(1, 8 * mm))
            story.append(Paragraph(
                "JobScout-AI is monitoring 4 portals continuously. "
                "You'll receive a report whenever matching jobs are posted.",
                self.styles["Footer"]
            ))
        else:
            # ── Group Jobs by Date ──
            grouped = self._group_by_date(jobs)

            job_idx = 0
            for date_key, date_jobs in grouped.items():
                # Date section heading
                story.append(HRFlowable(
                    width="100%", thickness=0.5, color=BORDER,
                    spaceBefore=3 * mm, spaceAfter=1 * mm
                ))
                story.append(Paragraph(
                    f"📅 {date_key}  —  {len(date_jobs)} job{'s' if len(date_jobs) != 1 else ''}",
                    self.styles["DateHeading"]
                ))

                # Job cards for this date
                for job in date_jobs:
                    job_idx += 1
                    job_block = self._build_job_card(job, job_idx, len(jobs))
                    story.append(KeepTogether(job_block))

        # ── Footer ──
        story.append(Spacer(1, 8 * mm))
        story.append(HRFlowable(
            width="100%", thickness=1, color=ACCENT,
            spaceBefore=4 * mm, spaceAfter=4 * mm
        ))
        story.append(Paragraph(
            f"JobScout-AI • Report generated {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}",
            self.styles["Footer"]
        ))
        story.append(Paragraph(
            "Sources: SarkariResult.com • FreeJobAlert.com • SarkariExam.com • RojgarResult.com",
            self.styles["Footer"]
        ))

        try:
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            doc.build([
                Paragraph(f"JobScout-AI Report — {digest_date}", self.styles["Title"]),
                Paragraph(f"Error generating report: {e}", self.styles["Normal"])
            ])

        buffer.seek(0)
        return buffer.read()

    def _group_by_date(self, jobs: List[Job]) -> Dict[str, List[Job]]:
        """Group jobs by scraped date, sorted most recent first."""
        grouped = defaultdict(list)
        for job in jobs:
            if job.scraped_at:
                # Use the scraped date
                if isinstance(job.scraped_at, str):
                    try:
                        dt = datetime.fromisoformat(job.scraped_at.replace("Z", "+00:00"))
                        key = dt.strftime("%A, %d %B %Y")
                    except ValueError:
                        key = "Unknown Date"
                else:
                    key = job.scraped_at.strftime("%A, %d %B %Y")
            else:
                key = "Unknown Date"
            grouped[key].append(job)

        # Sort by date (most recent first) — parse back the date keys
        def _parse_date_key(key):
            try:
                return datetime.strptime(key, "%A, %d %B %Y")
            except ValueError:
                return datetime.min

        sorted_keys = sorted(grouped.keys(), key=_parse_date_key, reverse=True)
        return {k: grouped[k] for k in sorted_keys}

    def _build_job_card(self, job: Job, index: int, total: int) -> list:
        """Build a detailed, information-rich job card."""
        elements = []

        # ── Card top border accent ──
        elements.append(HRFlowable(
            width="100%", thickness=3, color=ACCENT,
            spaceBefore=4 * mm, spaceAfter=2 * mm
        ))

        # ── Job number + title ──
        elements.append(Paragraph(
            f"<b>{index}.</b>  {self._escape(job.title)}",
            self.styles["JobTitle"]
        ))

        # ── Organization ──
        elements.append(Paragraph(
            f"🏛️  {self._escape(job.organization)}",
            self.styles["JobOrg"]
        ))

        # ── Description (if available) ──
        if job.description:
            elements.append(Paragraph(
                f"<i>{self._escape(job.description)}</i>",
                self.styles["JobField"]
            ))
            elements.append(Spacer(1, 1 * mm))

        # ── Key Details Grid ──
        # Row 1: Vacancies + Salary (most important, shown first)
        row1 = []
        if job.vacancies:
            row1.append(f"<b>👥 Vacancies:</b>  {self._escape(job.vacancies)}")
        if job.salary:
            row1.append(f"<b>💰 Salary/Pay:</b>  {self._escape(job.salary)}")
        for r in row1:
            elements.append(Paragraph(r, self.styles["JobHighlight"]))

        # Row 2: Age Limit + Selection Process
        row2 = []
        if job.age_limit:
            row2.append(f"<b>🎂 Age Limit:</b>  {self._escape(job.age_limit)}")
        if job.selection_process:
            row2.append(f"<b>📋 Selection:</b>  {self._escape(job.selection_process)}")
        for r in row2:
            elements.append(Paragraph(r, self.styles["JobField"]))

        # Row 3: Full Eligibility / Qualification
        if job.eligibility:
            elements.append(Paragraph(
                f"<b>📚 Eligibility:</b>  {self._escape(job.eligibility)}",
                self.styles["JobField"]
            ))

        # Row 4: Degree tags (compact pill row)
        if job.degree_tags:
            tags = "  •  ".join(job.degree_tags)
            elements.append(Paragraph(
                f"<b>🎓 Degrees:</b>  {self._escape(tags)}",
                self.styles["JobField"]
            ))

        # Row 5: Exam required
        if job.exam_required:
            elements.append(Paragraph(
                f"<b>📝 Exam:</b>  {self._escape(job.exam_required)}",
                self.styles["JobField"]
            ))

        # Row 6: Last Date with urgency colour
        if job.last_date:
            days_left = (job.last_date - date.today()).days
            if days_left < 0:
                urgency = f'<font color="#EF4444"><b>  ⚠️ EXPIRED</b></font>'
            elif days_left == 0:
                urgency = f'<font color="#EF4444"><b>  🚨 LAST DAY!</b></font>'
            elif days_left <= 3:
                urgency = f'<font color="#F59E0B"><b>  ⏰ {days_left} days left!</b></font>'
            elif days_left <= 7:
                urgency = f'<font color="#3B82F6">  ({days_left} days left)</font>'
            else:
                urgency = f'<font color="#10B981">  ({days_left} days left)</font>'
            elements.append(Paragraph(
                f"<b>📅 Last Date:</b>  <b>{job.last_date.strftime('%d %B %Y')}</b>{urgency}",
                self.styles["JobHighlight"]
            ))

        # ── Apply / Read Full Details Link (PROMINENT) ──
        link_url = job.apply_link or job.notification_link
        if link_url:
            # Truncate long URLs for display but keep full URL in href
            display_url = link_url if len(link_url) <= 60 else link_url[:57] + "..."
            elements.append(Spacer(1, 2 * mm))
            elements.append(Paragraph(
                f'🔗  <b>Apply / Read Full Details:</b>  '
                f'<a href="{link_url}" color="#3B82F6"><u>{self._escape(display_url)}</u></a>',
                self.styles["JobHighlight"]
            ))

        # ── Source tag ──
        elements.append(Spacer(1, 1 * mm))
        elements.append(Paragraph(
            f"Source: {self._escape(job.source)}",
            self.styles["SourceTag"]
        ))

        # Card bottom separator
        elements.append(Spacer(1, 2 * mm))
        if index < total:
            elements.append(HRFlowable(
                width="100%", thickness=0.5, color=DIVIDER,
                spaceBefore=1 * mm, spaceAfter=2 * mm
            ))

        return elements


    @staticmethod
    def _escape(text: str) -> str:
        """Escape XML special characters for ReportLab paragraphs."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _add_page_number(canvas, doc):
        """Add page number and branding to each page."""
        page_num = canvas.getPageNumber()
        canvas.saveState()
        # Page number
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawCentredString(
            A4[0] / 2, 10 * mm,
            f"JobScout-AI  •  Page {page_num}"
        )
        canvas.restoreState()
