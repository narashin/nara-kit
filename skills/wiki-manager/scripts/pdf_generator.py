"""
PDF Report Generator

Generates professional PDF reports from structured Confluence data.
Uses reportlab for PDF creation with support for TOC, styling, and formatting.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Dict, Any
from datetime import datetime
import os
import platform


class PDFReportGenerator:
    """Generate formatted PDF reports from structured data."""

    def __init__(self,
                 font_family: str = "Helvetica",
                 title_size: int = 24,
                 heading1_size: int = 18,
                 heading2_size: int = 16,
                 heading3_size: int = 14,
                 body_size: int = 11,
                 page_size=letter,
                 page_margin: float = 72,
                 include_toc: bool = True,
                 include_page_numbers: bool = True):
        """
        Initialize PDF generator with customization options.

        Args:
            font_family: Base font family (default: Helvetica)
            title_size: Title font size in points
            heading1_size: H1 heading size
            heading2_size: H2 heading size
            heading3_size: H3 heading size
            body_size: Body text size
            page_size: Page size (default: letter)
            page_margin: Page margin in points (72 = 1 inch)
            include_toc: Whether to include table of contents
            include_page_numbers: Whether to include page numbers
        """
        # Register CJK fonts for Korean and Japanese support
        self._register_cjk_fonts()

        self.title_size = title_size
        self.heading1_size = heading1_size
        self.heading2_size = heading2_size
        self.heading3_size = heading3_size
        self.body_size = body_size
        self.page_size = page_size
        self.page_margin = page_margin
        self.include_toc = include_toc
        self.include_page_numbers = include_page_numbers

        # Color scheme (default professional blue)
        self.color_scheme = {
            'primary': colors.HexColor('#003366'),
            'secondary': colors.HexColor('#0066CC'),
            'text': colors.HexColor('#333333'),
            'light_gray': colors.HexColor('#F5F5F5')
        }

        # Initialize styles
        self.styles = self._create_styles()

    def _register_cjk_fonts(self):
        """Register CJK fonts for Korean and Japanese support."""
        system = platform.system()
        font_registered = False

        # Try to find and register system fonts
        font_paths = []

        if system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # Korean
                "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf",  # Korean
                "/Library/Fonts/AppleSDGothicNeo.ttc",  # Korean (newer macOS)
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",  # Japanese
                "/System/Library/Fonts/Hiragino Sans GB.ttc",  # CJK
            ]
        elif system == "Linux":
            font_paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Korean
                "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",  # Korean
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # CJK
            ]
        elif system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # Korean (Malgun Gothic)
                "C:/Windows/Fonts/batang.ttc",  # Korean (Batang)
                "C:/Windows/Fonts/msgothic.ttc",  # Japanese (MS Gothic)
            ]

        # Try to register the first available font
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CJKFont', font_path))
                    pdfmetrics.registerFont(TTFont('CJKFont-Bold', font_path))
                    self.font_family = 'CJKFont'
                    font_registered = True
                    print(f"Registered CJK font: {font_path}")
                    break
                except Exception as e:
                    print(f"Failed to register font {font_path}: {e}")
                    continue

        if not font_registered:
            print("Warning: No CJK font found. Korean/Japanese text may not display correctly.")
            print("Falling back to Helvetica (Latin characters only)")

    def set_color_scheme(self, scheme: Dict[str, str]):
        """
        Set custom color scheme.

        Args:
            scheme: Dictionary with color keys (primary, secondary, text)
        """
        if 'primary' in scheme:
            self.color_scheme['primary'] = colors.HexColor(scheme['primary'])
        if 'secondary' in scheme:
            self.color_scheme['secondary'] = colors.HexColor(scheme['secondary'])
        if 'text' in scheme:
            self.color_scheme['text'] = colors.HexColor(scheme['text'])

        # Recreate styles with new colors
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create paragraph styles for the document."""
        base_styles = getSampleStyleSheet()

        # Use CJK font for bold as well (CJK fonts don't have separate bold variants)
        bold_font = self.font_family if self.font_family == 'CJKFont' else f'{self.font_family}-Bold'

        styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=self.title_size,
                textColor=self.color_scheme['primary'],
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=bold_font,
                wordWrap='CJK'
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=self.heading1_size,
                textColor=self.color_scheme['primary'],
                spaceAfter=12,
                spaceBefore=12,
                fontName=bold_font,
                wordWrap='CJK'
            ),
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=self.heading2_size,
                textColor=self.color_scheme['secondary'],
                spaceAfter=10,
                spaceBefore=10,
                fontName=bold_font,
                wordWrap='CJK'
            ),
            'Heading3': ParagraphStyle(
                'CustomHeading3',
                parent=base_styles['Heading3'],
                fontSize=self.heading3_size,
                textColor=self.color_scheme['text'],
                spaceAfter=8,
                spaceBefore=8,
                fontName=bold_font,
                wordWrap='CJK'
            ),
            'Body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=self.body_size,
                textColor=self.color_scheme['text'],
                alignment=TA_JUSTIFY,
                spaceAfter=6,
                fontName=self.font_family,
                wordWrap='CJK'
            ),
            'Code': ParagraphStyle(
                'CustomCode',
                parent=base_styles['Code'],
                fontSize=self.body_size - 1,
                textColor=colors.black,
                backColor=self.color_scheme['light_gray'],
                leftIndent=10,
                rightIndent=10,
                spaceAfter=6,
                spaceBefore=6,
                fontName='Courier',
                wordWrap='CJK'
            )
        }

        return styles

    def create_report(self, pages_data: List[Dict[str, Any]], output_path: str,
                      report_title: str = "Confluence Report"):
        """
        Create a PDF report from parsed Confluence pages.

        Args:
            pages_data: List of parsed page dictionaries
            output_path: Path to save the PDF file
            report_title: Title for the report cover page
        """
        print("pdf output_path:", output_path)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            leftMargin=self.page_margin,
            rightMargin=self.page_margin,
            topMargin=self.page_margin,
            bottomMargin=self.page_margin
        )

        story = []

        # Cover page
        story.extend(self._create_cover_page(report_title, pages_data))
        story.append(PageBreak())

        # Table of contents (placeholder for now)
        if self.include_toc:
            story.extend(self._create_toc(pages_data))
            story.append(PageBreak())

        # Content pages
        for i, page_data in enumerate(pages_data):
            story.extend(self._create_page_content(page_data))

            # Add page break between pages (except last)
            if i < len(pages_data) - 1:
                story.append(PageBreak())

        # Build PDF
        doc.build(story)

    def _create_cover_page(self, title: str, pages_data: List[Dict[str, Any]]) -> List:
        """Create the report cover page."""
        elements = []

        # Add some space at top
        elements.append(Spacer(1, 2 * inch))

        # Report title
        title_para = Paragraph(title, self.styles['Title'])
        elements.append(title_para)
        elements.append(Spacer(1, 0.5 * inch))

        # Metadata
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=self.styles['Body'],
            alignment=TA_CENTER,
            fontSize=self.body_size - 1
        )

        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated: {date_str}", metadata_style))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"Pages: {len(pages_data)}", metadata_style))

        return elements

    def _create_toc(self, pages_data: List[Dict[str, Any]]) -> List:
        """Create table of contents."""
        elements = []

        # TOC Title
        toc_title = Paragraph("Table of Contents", self.styles['Heading1'])
        elements.append(toc_title)
        elements.append(Spacer(1, 0.3 * inch))

        # TOC entries
        toc_style = ParagraphStyle(
            'TOC',
            parent=self.styles['Body'],
            fontSize=self.body_size,
            leftIndent=20,
            spaceAfter=8
        )

        for i, page_data in enumerate(pages_data):
            title = page_data.get('title', 'Untitled')
            entry = Paragraph(f"{i + 1}. {title}", toc_style)
            elements.append(entry)

        return elements

    def _create_page_content(self, page_data: Dict[str, Any]) -> List:
        """Create content for a single page."""
        elements = []

        # Page title
        title = page_data.get('title', 'Untitled')
        title_para = Paragraph(title, self.styles['Heading1'])
        elements.append(title_para)

        # Page metadata
        if page_data.get('author') or page_data.get('created_date'):
            metadata_parts = []
            if page_data.get('author'):
                metadata_parts.append(f"Author: {page_data['author']}")
            if page_data.get('created_date'):
                metadata_parts.append(f"Created: {page_data['created_date']}")

            metadata_text = " | ".join(metadata_parts)
            metadata_style = ParagraphStyle(
                'PageMetadata',
                parent=self.styles['Body'],
                fontSize=self.body_size - 2,
                textColor=colors.gray,
                spaceAfter=12
            )
            elements.append(Paragraph(metadata_text, metadata_style))

        elements.append(Spacer(1, 0.2 * inch))

        # Content elements
        for element in page_data.get('elements', []):
            element_type = element.get('type')

            if element_type == 'heading':
                level = element.get('level', 1)
                text = element.get('text', '')

                if level <= 3:
                    style_name = f'Heading{level}'
                    para = Paragraph(text, self.styles[style_name])
                    elements.append(para)
                else:
                    para = Paragraph(f"<b>{text}</b>", self.styles['Body'])
                    elements.append(para)

            elif element_type == 'paragraph':
                text = element.get('text', '')
                para = Paragraph(text, self.styles['Body'])
                elements.append(para)

            elif element_type in ['unordered_list', 'ordered_list']:
                items = element.get('items', [])
                for item in items:
                    bullet = '•' if element_type == 'unordered_list' else '1.'
                    para = Paragraph(f"{bullet} {item}", self.styles['Body'])
                    elements.append(para)
                elements.append(Spacer(1, 6))

            elif element_type == 'table':
                table_elem = self._create_table(element)
                if table_elem:
                    elements.append(table_elem)
                    elements.append(Spacer(1, 12))

            elif element_type == 'code_block':
                code_text = element.get('text', '')
                para = Paragraph(f"<pre>{code_text}</pre>", self.styles['Code'])
                elements.append(para)

        return elements

    def _create_table(self, table_data: Dict[str, Any]):
        """Create a table element."""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        if not headers and not rows:
            return None

        # Prepare table data
        table_content = []
        if headers:
            table_content.append(headers)
        table_content.extend(rows)

        # Create table
        table = Table(table_content)

        # Use CJK font for table as well
        bold_font = self.font_family if self.font_family == 'CJKFont' else f'{self.font_family}-Bold'

        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.color_scheme['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), self.body_size),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.color_scheme['text']),
            ('FONTNAME', (0, 1), (-1, -1), self.font_family),
            ('FONTSIZE', (0, 1), (-1, -1), self.body_size),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])

        table.setStyle(style)

        return table


if __name__ == '__main__':
    # Example usage
    sample_data = [
        {
            'title': 'Sample Page',
            'author': 'John Doe',
            'created_date': '2024-01-15',
            'elements': [
                {'type': 'heading', 'level': 2, 'text': '헬로'},
                {'type': 'paragraph', 'text': '複数のConfluenceウィキページを1つの包括的なPDFレポートに変換します。'},
                {'type': 'unordered_list', 'items': ['Item 1', 'Item 2', 'Item 3']}
            ]
        }
    ]

    generator = PDFReportGenerator()
    generator.create_report(sample_data, 'sample_report.pdf', 'Sample Report')
    print("Report generated: sample_report.pdf")