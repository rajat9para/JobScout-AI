"""Professional PDF generator for the nightly job digest.

Uses ReportLab to create a clean, branded PDF containing
medium-length descriptions of all matched jobs for the day.
"""
import io
import logging
from datetime import date, datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models import Job

logger = logging.getLogger(__name__)

# ── Color Palette ──
BRAND_BLUE = colors.HexColor("#1a73e8")
BRAND_DARK = colors.HexColor("#202124")
BRAND_GRAY = colors.HexColor("#5f6368")
BRAND_LIGHT_BG = colors.HexColor("#f8f9fa")
BRAND_GREEN = colors.HexColor("#0d652d")
BRAND_RED = colors.HexColor("#c5221f")
BRAND_ORANGE = colors.HexColor("#e37400")
DIVIDER_COLOR = colors.HexColor("#dadce0")


class PDFGenerator:
    """Generates a professional PDF digest of matched government jobs."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_custom_styles()

    def _register_custom_styles(self):
        """Register custom paragraph styles for the digest PDF."""
        # Title style for the PDF header
        self.styles.add(ParagraphStyle(
            name="DigestTitle",
            parent=self.styles["Title"],
            fontSize=22,
            textColor=BRAND_BLUE,
            spaceAfter=6 * mm,
            alignment=TA_CENTER,
        ))

        # Subtitle/date style
        self.styles.add(ParagraphStyle(
            name="DigestSubtitle",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=BRAND_GRAY,
            alignment=TA_CENTER,
            spaceAfter=8 * mm,
        ))

        # Job title style
        self.styles.add(ParagraphStyle(
            name="JobTitle",
            parent=self.styles["Heading2"],
            fontSize=13,
            textColor=BRAND_DARK,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
            leftIndent=0,
        ))

        # Organization name
        self.styles.add(ParagraphStyle(
            name="JobOrg",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=BRAND_BLUE,
            spaceAfter=2 * mm,
        ))

        # Job field label (bold)
        self.styles.add(ParagraphStyle(
            name="FieldLabel",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=BRAND_GRAY,
            spaceAfter=0.5 * mm,
        ))

        # Job field value
        self.styles.add(ParagraphStyle(
            name="FieldValue",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=BRAND_DARK,
            spaceAfter=1.5 * mm,
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name="Footer",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=BRAND_GRAY,
            alignment=TA_CENTER,
        ))

        # Summary stat style
        self.styles.add(ParagraphStyle(
            name="SummaryStat",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=BRAND_DARK,
            alignment=TA_CENTER,
            spaceAfter=3 * mm,
        ))

        # No jobs message
        self.styles.add(ParagraphStyle(
            name="NoJobs",
            parent=self.styles["Normal"],
            fontSize=14,
            textColor=BRAND_GRAY,
            alignment=TA_CENTER,
            spaceBefore=30 * mm,
        ))

    def generate(self, jobs: List[Job], digest_date: date = None) -> bytes:
        """Generate the digest PDF and return as bytes.

        Args:
            jobs: List of Job objects to include in the digest.
            digest_date: The date for the digest header. Defaults to today.

        Returns:
            PDF file content as bytes.
        """
        if digest_date is None:
            digest_date = date.today()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title=f"JobScout Digest — {digest_date.strftime('%d %b %Y')}",
            author="JobScout Bot",
            subject="Daily Government Job Digest",
        )

        story = []

        # ── Header ──
        story.append(Paragraph("📋 JobScout — Daily Job Digest", self.styles["DigestTitle"]))
        story.append(Paragraph(
            f"Generated on {digest_date.strftime('%A, %d %B %Y')} • "
            f"{len(jobs)} matching job{'s' if len(jobs) != 1 else ''} found",
            self.styles["DigestSubtitle"]
        ))
        story.append(HRFlowable(
            width="100%", thickness=1.5, color=BRAND_BLUE,
            spaceBefore=2 * mm, spaceAfter=6 * mm
        ))

        # ── Empty state ──
        if not jobs:
            story.append(Paragraph(
                "No matching government jobs were found today.",
                self.styles["NoJobs"]
            ))
            story.append(Spacer(1, 10 * mm))
            story.append(Paragraph(
                "Don't worry — JobScout is monitoring 4 portals around the clock. "
                "You'll receive a digest whenever matching jobs are posted.",
                self.styles["Footer"]
            ))
        else:
            # ── Summary Stats ──
            sources = set(j.source for j in jobs)
            upcoming = sum(1 for j in jobs if j.last_date and j.last_date >= date.today())
            story.append(Paragraph(
                f"<b>{len(jobs)}</b> Jobs • <b>{len(sources)}</b> Sources • "
                f"<b>{upcoming}</b> Open Deadlines",
                self.styles["SummaryStat"]
            ))
            story.append(Spacer(1, 4 * mm))

            # ── Job Cards ──
            for idx, job in enumerate(jobs, 1):
                job_block = self._build_job_block(job, idx, len(jobs))
                story.append(KeepTogether(job_block))

        # ── Footer ──
        story.append(Spacer(1, 10 * mm))
        story.append(HRFlowable(
            width="100%", thickness=0.5, color=DIVIDER_COLOR,
            spaceBefore=4 * mm, spaceAfter=4 * mm
        ))
        story.append(Paragraph(
            f"Generated by JobScout Bot • {datetime.now().strftime('%d %b %Y, %I:%M %p')} • "
            "Sources: NCS.gov.in, SarkariResult.com, FreeJobAlert.com, EmploymentNews.gov.in",
            self.styles["Footer"]
        ))

        try:
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # Fallback: generate minimal PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            doc.build([Paragraph(f"JobScout Digest — {digest_date}", self.styles["Title"]),
                        Paragraph(f"Error generating full PDF: {e}", self.styles["Normal"])])

        buffer.seek(0)
        return buffer.read()

    def _build_job_block(self, job: Job, index: int, total: int) -> list:
        """Build the flowable elements for a single job card."""
        elements = []

        # Job number + title
        elements.append(Paragraph(
            f"<b>{index}.</b> {self._escape(job.title)}",
            self.styles["JobTitle"]
        ))

        # Organization
        elements.append(Paragraph(
            f"🏢 {self._escape(job.organization)}",
            self.styles["JobOrg"]
        ))

        # Details table (two-column layout for compact display)
        detail_rows = []

        if job.eligibility:
            detail_rows.append(("📚 Eligibility", self._escape(job.eligibility)))
        if job.salary:
            detail_rows.append(("💰 Salary", self._escape(job.salary)))
        if job.vacancies:
            detail_rows.append(("👥 Vacancies", self._escape(job.vacancies)))
        if job.exam_required:
            detail_rows.append(("📝 Exam", self._escape(job.exam_required)))
        if job.last_date:
            days_left = (job.last_date - date.today()).days
            urgency = ""
            if days_left < 0:
                urgency = " (Expired)"
            elif days_left == 0:
                urgency = " (Last Day!)"
            elif days_left <= 3:
                urgency = f" ({days_left} days left!)"
            elif days_left <= 7:
                urgency = f" ({days_left} days left)"
            detail_rows.append(("📅 Last Date", f"{job.last_date.strftime('%d %b %Y')}{urgency}"))
        if job.apply_link:
            link_text = job.apply_link if len(job.apply_link) <= 60 else job.apply_link[:57] + "..."
            detail_rows.append(("🔗 Apply Link", f'<a href="{job.apply_link}" color="blue">{self._escape(link_text)}</a>'))

        detail_rows.append(("📡 Source", self._escape(job.source)))

        # Build details as labeled paragraphs
        for label, value in detail_rows:
            elements.append(Paragraph(
                f"<b>{label}:</b>  {value}",
                self.styles["FieldValue"]
            ))

        # Degree tags as a compact line
        if job.degree_tags:
            tags = ", ".join(job.degree_tags)
            elements.append(Paragraph(
                f"<b>🎓 Degrees:</b>  {self._escape(tags)}",
                self.styles["FieldValue"]
            ))

        # Divider between jobs (not after the last one)
        if index < total:
            elements.append(Spacer(1, 3 * mm))
            elements.append(HRFlowable(
                width="100%", thickness=0.5, color=DIVIDER_COLOR,
                spaceBefore=2 * mm, spaceAfter=4 * mm
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
        """Add page number to the bottom of each page."""
        page_num = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(BRAND_GRAY)
        canvas.drawCentredString(
            A4[0] / 2, 12 * mm,
            f"Page {page_num}"
        )
        canvas.restoreState()
