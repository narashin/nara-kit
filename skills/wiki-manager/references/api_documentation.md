# Wiki Manager API Documentation

## ConfluenceParser

### Class: `ConfluenceParser`

Main class for parsing Confluence content.

#### Methods

##### `parse_multiple_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Parse multiple Confluence pages at once.

**Parameters:**
- `pages` (List[Dict]): List of page dictionaries, each containing:
  - `title` (str, required): Page title
  - `content` (str, required): Page content (HTML, wiki markup, or plain text)
  - `author` (str, optional): Page author
  - `created_date` (str, optional): Creation date
  - `updated_date` (str, optional): Last modified date
  - `labels` (List[str], optional): Page labels/tags

**Returns:**
- List[Dict]: Parsed page data with structured content elements

**Example:**
```python
parser = ConfluenceParser()
pages = [
    {
        "title": "Project Overview",
        "content": "<h1>Introduction</h1><p>Content here...</p>"
    }
]
result = parser.parse_multiple_pages(pages)
```

##### `parse_page(page: Dict[str, Any]) -> Dict[str, Any]`

Parse a single Confluence page.

**Parameters:**
- `page` (Dict): Page dictionary with required `title` and `content` keys

**Returns:**
- Dict: Parsed page data with the following structure:
  ```python
  {
      'title': str,
      'author': str,
      'created_date': str,
      'updated_date': str,
      'labels': List[str],
      'elements': List[Dict]  # Structured content elements
  }
  ```

**Content Elements:**

Each element in the `elements` list has a `type` field and type-specific data:

1. **Heading**
   ```python
   {
       'type': 'heading',
       'level': int,  # 1-6
       'text': str
   }
   ```

2. **Paragraph**
   ```python
   {
       'type': 'paragraph',
       'text': str
   }
   ```

3. **Unordered List**
   ```python
   {
       'type': 'unordered_list',
       'items': List[str]
   }
   ```

4. **Ordered List**
   ```python
   {
       'type': 'ordered_list',
       'items': List[str]
   }
   ```

5. **Table**
   ```python
   {
       'type': 'table',
       'headers': List[str],
       'rows': List[List[str]]
   }
   ```

6. **Code Block**
   ```python
   {
       'type': 'code_block',
       'language': str,
       'text': str
   }
   ```

---

## PDFReportGenerator

### Class: `PDFReportGenerator`

Generate formatted PDF reports from structured data.

#### Constructor

```python
PDFReportGenerator(
    font_family: str = "Helvetica",
    title_size: int = 24,
    heading1_size: int = 18,
    heading2_size: int = 16,
    heading3_size: int = 14,
    body_size: int = 11,
    page_size = letter,
    page_margin: float = 72,
    include_toc: bool = True,
    include_page_numbers: bool = True
)
```

**Parameters:**
- `font_family` (str): Base font family (default: "Helvetica")
- `title_size` (int): Title font size in points
- `heading1_size` (int): H1 heading size
- `heading2_size` (int): H2 heading size
- `heading3_size` (int): H3 heading size
- `body_size` (int): Body text size
- `page_size`: Page size from reportlab (default: letter)
- `page_margin` (float): Page margin in points (72 = 1 inch)
- `include_toc` (bool): Include table of contents
- `include_page_numbers` (bool): Include page numbers

#### Methods

##### `create_report(pages_data: List[Dict[str, Any]], output_path: str, report_title: str = "Confluence Report")`

Create a PDF report from parsed Confluence pages.

**Parameters:**
- `pages_data` (List[Dict]): List of parsed page dictionaries from `ConfluenceParser`
- `output_path` (str): Path to save the PDF file
- `report_title` (str): Title for the report cover page

**Example:**
```python
generator = PDFReportGenerator()
generator.create_report(
    parsed_pages, 
    "output_report.pdf",
    "Q1 2024 Project Report"
)
```

##### `set_color_scheme(scheme: Dict[str, str])`

Set custom color scheme for the report.

**Parameters:**
- `scheme` (Dict[str, str]): Dictionary with color keys:
  - `primary`: Primary color (headings, cover)
  - `secondary`: Secondary color (subheadings)
  - `text`: Body text color

Colors should be hex strings (e.g., "#003366").

**Example:**
```python
generator.set_color_scheme({
    "primary": "#003366",
    "secondary": "#0066CC",
    "text": "#333333"
})
```

---

## Complete Workflow Example

```python
from confluence_parser import ConfluenceParser
from pdf_generator import PDFReportGenerator

# 1. Prepare input data
pages = [
    {
        "title": "Project Overview",
        "content": """
# Project Goals
This project aims to improve efficiency.

## Key Objectives
* Reduce processing time
* Improve accuracy
* Enhance user experience
""",
        "author": "Jane Smith",
        "created_date": "2024-01-15"
    },
    {
        "title": "Technical Architecture",
        "content": """
# System Design
The system consists of three main components.

## Components
1. Frontend Application
2. Backend Services
3. Database Layer
""",
        "author": "John Doe",
        "created_date": "2024-01-20"
    }
]

# 2. Parse Confluence pages
parser = ConfluenceParser()
parsed_pages = parser.parse_multiple_pages(pages)

# 3. Customize PDF generator
generator = PDFReportGenerator(
    font_family="Helvetica",
    title_size=28,
    body_size=12,
    include_toc=True
)

# Set custom colors
generator.set_color_scheme({
    "primary": "#1a5490",
    "secondary": "#3498db",
    "text": "#2c3e50"
})

# 4. Generate PDF report
generator.create_report(
    parsed_pages,
    "project_report.pdf",
    "Q1 2024 Project Documentation"
)

print("Report generated successfully!")
```

---

## Error Handling

Both classes may raise exceptions in the following cases:

**ConfluenceParser:**
- `ValueError`: Invalid page structure or missing required fields
- `HTMLParser.HTMLParseError`: Malformed HTML content

**PDFReportGenerator:**
- `IOError`: Unable to write output file
- `ValueError`: Invalid color scheme or parameters
- `reportlab exceptions`: PDF generation errors

**Example with error handling:**
```python
try:
    parser = ConfluenceParser()
    parsed_pages = parser.parse_multiple_pages(pages)
    
    generator = PDFReportGenerator()
    generator.create_report(parsed_pages, "output.pdf")
    
except ValueError as e:
    print(f"Invalid input data: {e}")
except IOError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```