# PDF Layout Guidelines

Best practices for creating well-formatted PDF reports from Confluence pages.

## Page Layout

### Standard Margins

Default margins provide good readability:
- **1 inch (72 points)** on all sides
- Adjust for specific needs:
  - Narrow: 0.5 inch (36 points)
  - Wide: 1.5 inch (108 points)

```python
# Custom margins
generator = PDFReportGenerator(page_margin=54)  # 0.75 inch
```

### Page Sizes

Available page sizes:
- **letter** (8.5" × 11") - US standard
- **A4** (210mm × 297mm) - International standard
- **legal** (8.5" × 14") - US legal documents

```python
from reportlab.lib.pagesizes import letter, A4, legal

generator = PDFReportGenerator(page_size=A4)
```

## Typography

### Font Selection

**Recommended Fonts:**
- **Helvetica** - Clean, professional, default
- **Times-Roman** - Traditional, formal documents
- **Courier** - Monospace, code-heavy documents

```python
generator = PDFReportGenerator(font_family="Times-Roman")
```

### Font Sizes

Standard hierarchy:
```python
PDFReportGenerator(
    title_size=24,      # Cover page title
    heading1_size=18,   # Main section headings
    heading2_size=16,   # Subsection headings
    heading3_size=14,   # Minor headings
    body_size=11        # Body text
)
```

**Guidelines:**
- Minimum body size: 10pt (accessibility)
- Maximum title size: 28pt (avoid overwhelming)
- Maintain 2-4pt difference between heading levels

### Line Spacing

- Body text: 1.2× font size (default)
- Headings: 1.0× font size
- Space after paragraphs: 6pt
- Space before/after headings: 10-12pt

## Color Guidelines

### Professional Color Schemes

**Corporate Blue:**
```python
generator.set_color_scheme({
    "primary": "#003366",    # Dark blue
    "secondary": "#0066CC",  # Medium blue
    "text": "#333333"        # Dark gray
})
```

**Modern Green:**
```python
generator.set_color_scheme({
    "primary": "#2C5F2D",    # Forest green
    "secondary": "#97BC62",  # Light green
    "text": "#2D3748"        # Charcoal
})
```

**Elegant Gray:**
```python
generator.set_color_scheme({
    "primary": "#2C3E50",    # Navy gray
    "secondary": "#7F8C8D",  # Medium gray
    "text": "#34495E"        # Dark gray
})
```

### Accessibility

- Ensure sufficient contrast (4.5:1 minimum for body text)
- Avoid pure black (#000000), use dark gray (#333333)
- Test colors in grayscale
- Don't rely solely on color to convey information

## Content Structure

### Document Organization

1. **Cover Page**
   - Report title
   - Generation date
   - Optional: Author, version, confidentiality

2. **Table of Contents**
   - Page titles with page numbers
   - Optional: Section numbers

3. **Content Pages**
   - One wiki page per section
   - Clear heading hierarchy
   - Consistent spacing

4. **Appendices** (optional)
   - Additional data
   - Reference materials

### Heading Hierarchy

Maintain consistent hierarchy:

```
H1: Main page title (once per page)
  H2: Major sections
    H3: Subsections
      H4: Minor points (use sparingly)
```

**Best Practices:**
- Don't skip levels (H1 → H3)
- Limit to 3-4 levels deep
- Each section should have content, not just subsections

### Paragraph Formatting

- **Length**: 3-7 lines ideal, max 10 lines
- **Alignment**: Justified for formal, left for casual
- **Spacing**: Consistent between all paragraphs
- **Orphans/Widows**: Avoid single lines at page breaks

## Lists

### Bullet Points

✅ **Good:**
- Parallel structure (all start with verbs or all nouns)
- Consistent punctuation
- 2-4 items ideal, max 8
- Single line per item (or max 2 lines)

❌ **Bad:**
- Mixing sentence structures
- Inconsistent capitalization
- Too many items (>10)
- Paragraph-length items

### Numbered Lists

Use for:
- Sequential steps
- Prioritized items
- Instructions

Don't use for:
- Unordered information
- Non-sequential items
- Short lists (<3 items)

## Tables

### Table Design

**Good table structure:**
```python
{
    'type': 'table',
    'headers': ['Column 1', 'Column 2', 'Column 3'],
    'rows': [
        ['Data 1A', 'Data 1B', 'Data 1C'],
        ['Data 2A', 'Data 2B', 'Data 2C']
    ]
}
```

**Best Practices:**
- Clear, descriptive headers
- Consistent column widths
- Avoid overly wide tables (max 6-7 columns)
- Keep cell content concise
- Alternate row colors for readability (auto-applied)

### Handling Long Tables

If table exceeds one page:
- Consider splitting into multiple tables
- Use clear table titles/captions
- Repeat headers on each page (manual implementation needed)

## Code Blocks

### Formatting

Code blocks receive special formatting:
- Monospace font (Courier)
- Light gray background
- Increased left/right padding
- Smaller font size (body_size - 1)

**Best Practices:**
- Keep lines under 80 characters
- Include language identifier when possible
- Add comments for context
- Consider syntax highlighting (manual implementation)

### Long Code

For lengthy code:
- Break into logical sections
- Add descriptive comments
- Consider moving to appendix
- Link to external repository if available

## Images and Graphics

Currently not supported directly, but can be added:

```python
# Example extension (not in base skill)
from reportlab.lib.utils import ImageReader

img = ImageReader('diagram.png')
story.append(Image(img, width=400, height=300))
```

**Recommendations:**
- Maximum width: page width minus margins
- Maintain aspect ratio
- Add captions and references
- Compress for file size

## Page Breaks

Automatic page breaks occur when:
- Content exceeds page height
- PageBreak() element added
- Between wiki pages

**Control page breaks:**
- Use `KeepTogether()` for content that shouldn't split
- Strategic PageBreak() placement
- Adjust margins if needed

## Common Layout Issues

### Issue: Text Overflow

**Problem:** Text runs off page edge

**Solutions:**
- Reduce font size
- Increase margins
- Break long words/URLs
- Use smaller page size

### Issue: Too Much White Space

**Problem:** Pages have large blank areas

**Solutions:**
- Reduce spacing after elements
- Combine related sections
- Adjust margins
- Remove unnecessary page breaks

### Issue: Inconsistent Formatting

**Problem:** Different pages look different

**Solutions:**
- Use consistent heading levels
- Apply same spacing rules
- Maintain color scheme
- Standardize table formats

### Issue: Poor Readability

**Problem:** Text is difficult to read

**Solutions:**
- Increase font size (11-12pt minimum)
- Improve contrast
- Use better font (Helvetica, Georgia)
- Add more line spacing
- Break up long paragraphs

## Performance Considerations

### Large Documents

For reports >100 pages:
- Consider splitting into multiple PDFs
- Optimize image sizes
- Simplify complex tables
- Use simpler fonts

### Generation Time

Typical generation times:
- 10 pages: <2 seconds
- 50 pages: <10 seconds
- 100 pages: <30 seconds

**Optimization tips:**
- Minimize custom fonts
- Reduce image count/size
- Simplify table structures
- Use standard page sizes

## Quality Checklist

Before finalizing:

- [ ] All pages have consistent margins
- [ ] Heading hierarchy is logical
- [ ] Colors are professional and accessible
- [ ] No orphaned headings at page breaks
- [ ] Tables fit within page width
- [ ] Code blocks are readable
- [ ] TOC matches content
- [ ] No blank pages (unless intentional)
- [ ] Consistent spacing throughout
- [ ] All content is legible when printed

## Example Configurations

### Formal Business Report
```python
generator = PDFReportGenerator(
    font_family="Times-Roman",
    title_size=24,
    body_size=12,
    page_size=letter,
    page_margin=72,
    include_toc=True
)

generator.set_color_scheme({
    "primary": "#2C3E50",
    "secondary": "#34495E",
    "text": "#212529"
})
```

### Technical Documentation
```python
generator = PDFReportGenerator(
    font_family="Helvetica",
    title_size=22,
    body_size=11,
    page_size=A4,
    page_margin=54,
    include_toc=True
)

generator.set_color_scheme({
    "primary": "#0066CC",
    "secondary": "#4A90E2",
    "text": "#333333"
})
```

### Casual Internal Document
```python
generator = PDFReportGenerator(
    font_family="Helvetica",
    title_size=20,
    body_size=10,
    page_size=letter,
    page_margin=36,
    include_toc=False
)

generator.set_color_scheme({
    "primary": "#5C6BC0",
    "secondary": "#7E57C2",
    "text": "#424242"
})
```