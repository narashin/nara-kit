# Confluence Content Formats

This document describes the various Confluence content formats supported by the Wiki Manager skill.

## Supported Formats

### 1. Confluence Storage Format (XHTML)

Confluence stores page content in a structured XHTML format. This is the preferred format for accurate parsing.

**Example:**
```html
<h1>Project Overview</h1>
<p>This is an introduction to the project.</p>
<h2>Key Features</h2>
<ul>
    <li>Feature 1</li>
    <li>Feature 2</li>
    <li>Feature 3</li>
</ul>
<table>
    <tr>
        <th>Component</th>
        <th>Status</th>
    </tr>
    <tr>
        <td>Frontend</td>
        <td>Complete</td>
    </tr>
</table>
```

**Supported XHTML Elements:**

| Element | Description | Parsed As |
|---------|-------------|-----------|
| `<h1>` - `<h6>` | Headings | heading (level 1-6) |
| `<p>` | Paragraph | paragraph |
| `<ul>` | Unordered list | unordered_list |
| `<ol>` | Ordered list | ordered_list |
| `<li>` | List item | list_item |
| `<table>` | Table | table |
| `<tr>` | Table row | table_row |
| `<th>` | Table header | table_cell (header) |
| `<td>` | Table cell | table_cell |
| `<code>` | Code (inline) | inline_code |
| `<pre>` | Code block | code_block |
| `<strong>`, `<b>` | Bold text | (preserved in text) |
| `<em>`, `<i>` | Italic text | (preserved in text) |

### 2. Wiki Markup (Plain Text)

Simple plain text with wiki-style markup.

**Example:**
```
# Project Overview
This is an introduction to the project.

## Key Features
* Feature 1
* Feature 2
* Feature 3

## Implementation Steps
1. Design phase
2. Development phase
3. Testing phase

```python
def hello():
    print("Hello, World!")
```
```

**Supported Markup:**

| Markup | Description | Example |
|--------|-------------|---------|
| `#` - `######` | Headings | `# Heading 1`, `## Heading 2` |
| `*` or `-` | Unordered list | `* Item 1`, `- Item 2` |
| `1.`, `2.`, etc. | Ordered list | `1. First`, `2. Second` |
| ` ``` ` | Code block | ` ```python\ncode\n``` ` |
| Plain text | Paragraph | Any text not matching above |

### 3. Plain Text

Basic plain text without special markup. Each line becomes a paragraph.

**Example:**
```
This is a simple paragraph.

This is another paragraph.

Yet another paragraph here.
```

## Format Detection

The parser automatically detects the format:

1. **XHTML**: Content starting with `<` is treated as HTML
2. **Wiki Markup**: Content with markdown-style headings (`#`)
3. **Plain Text**: Everything else

## Best Practices

### For XHTML Content

✅ **DO:**
- Use proper HTML structure with opening and closing tags
- Include complete table structures (`<table>`, `<tr>`, `<td>`)
- Use semantic HTML (`<h1>` for top-level headings, etc.)

❌ **DON'T:**
- Mix HTML and wiki markup
- Use malformed or unclosed tags
- Rely on CSS for structure (not supported)

### For Wiki Markup

✅ **DO:**
- Start headings at the beginning of a line
- Use consistent list markers (`*` or `-`)
- Include blank lines between sections
- Close code blocks with ` ``` `

❌ **DON'T:**
- Indent headings
- Mix ordered and unordered lists
- Use complex nested structures

### For Plain Text

✅ **DO:**
- Keep paragraphs separated by blank lines
- Use simple, clear text
- Consider converting to wiki markup for better structure

❌ **DON'T:**
- Expect special formatting
- Use special characters expecting interpretation
- Rely on whitespace for structure

## Common Issues and Solutions

### Issue: Lists Not Parsing Correctly

**Problem:**
```
* Item 1
  * Nested item  ← Nested lists not supported
* Item 2
```

**Solution:**
```
* Item 1
* Nested item (use indentation in text)
* Item 2
```

### Issue: Tables Not Rendering

**Problem:**
```html
<table>
<tr><td>Cell 1<td>Cell 2</tr>  ← Unclosed <td> tags
</table>
```

**Solution:**
```html
<table>
<tr>
    <td>Cell 1</td>
    <td>Cell 2</td>
</tr>
</table>
```

### Issue: Code Blocks Not Formatting

**Problem:**
````
```python
code here
← No closing backticks
````

**Solution:**
````
```python
code here
```
````

## Format Conversion Tips

### From Confluence API

When fetching from Confluence API, use the `storage` format:

```python
# Using Confluence API
page = confluence.get_page_by_id(page_id, expand='body.storage')
content = page['body']['storage']['value']

# Pass to parser
pages = [{
    'title': page['title'],
    'content': content
}]
```

### From Confluence Export

Confluence exports may be in different formats:
- **HTML Export**: Use directly as XHTML
- **XML Export**: Extract `<ac:rich-text-body>` content
- **PDF Export**: Use OCR to extract text (see separate guide)

### Manual Conversion

To convert from other formats:

1. **Markdown → Wiki Markup**: Already similar, minor adjustments needed
2. **Word → XHTML**: Use document conversion tools
3. **Plain Text → Wiki Markup**: Add heading markers manually

## Testing Your Content

Quick test to verify format parsing:

```python
from confluence_parser import ConfluenceParser

parser = ConfluenceParser()
test_page = {
    'title': 'Test Page',
    'content': '<h1>Test</h1><p>Content here</p>'
}

result = parser.parse_page(test_page)
print(f"Parsed {len(result['elements'])} elements")
for element in result['elements']:
    print(f"  - {element['type']}: {element.get('text', '')[:50]}")
```

Expected output:
```
Parsed 2 elements
  - heading: Test
  - paragraph: Content here
```