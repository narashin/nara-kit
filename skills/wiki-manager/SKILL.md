---
name: wiki-manager
description: Convert multiple Confluence wiki pages into a comprehensive PDF report. Use when the user has Confluence page data and wants to generate a formatted PDF report/document that consolidates information from multiple wiki pages. Handles parsing wiki markup, extracting content structure, and generating professional PDF reports.
---

# Wiki Manager - Confluence to PDF Report Generator

## Overview

This skill converts multiple Confluence wiki pages into a professional PDF report. It parses Confluence content, extracts structure, and generates a formatted PDF document.

## Quick Start

```python
from scripts.confluence_parser import ConfluenceParser
from scripts.pdf_generator import PDFReportGenerator

# Parse Confluence pages
parser = ConfluenceParser()
pages_data = parser.parse_multiple_pages([
    {"title": "Page 1", "content": "...confluence markup..."},
    {"title": "Page 2", "content": "...confluence markup..."}
])

# Generate PDF report
generator = PDFReportGenerator()
generator.create_report(pages_data, "output_report.pdf")
```

## Workflow

1. **Parse Confluence data**: Use `ConfluenceParser` to extract and structure content
2. **Process content**: Convert Confluence markup to structured format
3. **Generate PDF**: Use `PDFReportGenerator` to create formatted PDF

## Input Format

Confluence pages should be provided as a list of dictionaries:

```python
pages = [
    {
        "title": "Project Overview",
        "content": "<p>Confluence content here...</p>",
        "author": "John Doe",
        "created_date": "2024-01-15",
        "labels": ["project", "documentation"]
    },
    # More pages...
]
```

Required fields:
- `title`: Page title
- `content`: Page content (Confluence storage format, wiki markup, or plain text)

Optional fields:
- `author`: Page author
- `created_date`: Creation date
- `updated_date`: Last modified date
- `labels`: List of page labels/tags

## Output Format

The generated PDF includes:
- **Cover page** with report title and metadata
- **Table of contents** with page numbers
- **Individual sections** for each wiki page
- **Preserved formatting**: headings, lists, tables, code blocks
- **Page numbers** and consistent styling

## Scripts

### confluence_parser.py
Parses Confluence content and extracts structure:
- Handles Confluence storage format (XHTML)
- Converts wiki markup to structured data
- Extracts headings, lists, tables, code blocks
- Preserves content hierarchy

### pdf_generator.py
Generates formatted PDF from structured data:
- Creates professional layouts
- Handles text formatting and styles
- Generates table of contents
- Adds page numbers and headers

### generate_report.py
End-to-end workflow script that combines parsing and PDF generation:

```bash
python scripts/generate_report.py input_pages.json output_report.pdf
```

## Customization

Customize PDF output by modifying `PDFReportGenerator` parameters:

```python
generator = PDFReportGenerator(
    font_family="Helvetica",
    title_size=24,
    heading_size=16,
    body_size=11,
    page_margin=72,  # 1 inch
    include_toc=True,
    include_page_numbers=True
)
```

## Common Tasks

### Generate report from JSON file
```bash
python scripts/generate_report.py confluence_pages.json report.pdf
```

### Parse and inspect content
```python
parser = ConfluenceParser()
pages_data = parser.parse_multiple_pages(pages)

# Inspect parsed structure
for page in pages_data:
    print(f"Title: {page['title']}")
    print(f"Sections: {len(page['sections'])}")
```

### Custom styling
```python
generator = PDFReportGenerator()
generator.set_color_scheme({
    "primary": "#003366",
    "secondary": "#0066CC",
    "text": "#333333"
})
generator.create_report(pages_data, "styled_report.pdf")
```

## Troubleshooting

**Issue**: Confluence markup not parsing correctly
- Ensure content is in Confluence storage format (XHTML)
- Check for malformed HTML tags
- See `references/confluence_formats.md` for supported formats

**Issue**: PDF layout problems
- Adjust page margins and font sizes
- Check for overly long tables or code blocks
- See `references/layout_guidelines.md` for best practices

For detailed API documentation, see `references/api_documentation.md`.