"""
Confluence Content Parser

Parses Confluence wiki pages and extracts structured content.
Handles Confluence storage format (XHTML), wiki markup, and plain text.
"""

from html.parser import HTMLParser
from typing import List, Dict, Any
import re


class ConfluenceHTMLParser(HTMLParser):
    """Parse Confluence storage format (XHTML) into structured data."""

    def __init__(self):
        super().__init__()
        self.content_elements = []
        self.current_element = None
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.current_element = {
                'type': 'heading',
                'level': level,
                'text': ''
            }
            self.stack.append(('heading', self.current_element))

        elif tag == 'p':
            self.current_element = {
                'type': 'paragraph',
                'text': ''
            }
            self.stack.append(('paragraph', self.current_element))

        elif tag == 'ul':
            self.current_element = {
                'type': 'unordered_list',
                'items': []
            }
            self.stack.append(('list', self.current_element))

        elif tag == 'ol':
            self.current_element = {
                'type': 'ordered_list',
                'items': []
            }
            self.stack.append(('list', self.current_element))

        elif tag == 'li':
            self.current_element = {
                'type': 'list_item',
                'text': ''
            }
            self.stack.append(('list_item', self.current_element))

        elif tag == 'table':
            self.current_element = {
                'type': 'table',
                'headers': [],
                'rows': []
            }
            self.stack.append(('table', self.current_element))

        elif tag == 'tr':
            self.current_element = {
                'type': 'table_row',
                'cells': []
            }
            self.stack.append(('table_row', self.current_element))

        elif tag in ['th', 'td']:
            self.current_element = {
                'type': 'table_cell',
                'text': '',
                'is_header': tag == 'th'
            }
            self.stack.append(('table_cell', self.current_element))

        elif tag == 'code':
            if 'class' in attrs_dict and 'code-block' in attrs_dict['class']:
                self.current_element = {
                    'type': 'code_block',
                    'language': attrs_dict.get('data-language', ''),
                    'text': ''
                }
                self.stack.append(('code_block', self.current_element))
            else:
                self.current_element = {
                    'type': 'inline_code',
                    'text': ''
                }
                self.stack.append(('inline_code', self.current_element))

        elif tag == 'strong' or tag == 'b':
            self.stack.append(('bold', None))

        elif tag == 'em' or tag == 'i':
            self.stack.append(('italic', None))

    def handle_endtag(self, tag):
        if not self.stack:
            return

        element_type, element_data = self.stack.pop()

        if element_type in ['heading', 'paragraph']:
            self.content_elements.append(element_data)

        elif element_type == 'list_item' and self.stack:
            parent_type, parent_data = self.stack[-1]
            if parent_type == 'list':
                parent_data['items'].append(element_data['text'].strip())

        elif element_type == 'list':
            self.content_elements.append(element_data)

        elif element_type == 'table_cell' and self.stack:
            parent_type, parent_data = self.stack[-1]
            if parent_type == 'table_row':
                parent_data['cells'].append({
                    'text': element_data['text'].strip(),
                    'is_header': element_data['is_header']
                })

        elif element_type == 'table_row' and self.stack:
            parent_type, parent_data = self.stack[-1]
            if parent_type == 'table':
                cells = element_data['cells']
                if cells and cells[0]['is_header']:
                    parent_data['headers'] = [cell['text'] for cell in cells]
                else:
                    parent_data['rows'].append([cell['text'] for cell in cells])

        elif element_type == 'table':
            self.content_elements.append(element_data)

        elif element_type in ['code_block', 'inline_code']:
            self.content_elements.append(element_data)

    def handle_data(self, data):
        if self.stack:
            element_type, element_data = self.stack[-1]

            if element_type in ['heading', 'paragraph', 'list_item', 'table_cell', 'code_block', 'inline_code']:
                element_data['text'] += data


class ConfluenceParser:
    """Main parser for Confluence content."""

    def __init__(self):
        self.html_parser = None

    def parse_multiple_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse multiple Confluence pages.

        Args:
            pages: List of page dictionaries with 'title' and 'content' keys

        Returns:
            List of parsed page data with structured content
        """
        parsed_pages = []

        for page in pages:
            parsed_page = self.parse_page(page)
            parsed_pages.append(parsed_page)

        return parsed_pages

    def parse_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single Confluence page.

        Args:
            page: Page dictionary with 'title' and 'content' keys

        Returns:
            Parsed page data with structured content
        """
        title = page.get('title', 'Untitled')
        content = page.get('content', '')

        # Detect content format
        if content.strip().startswith('<'):
            # HTML/XHTML format
            elements = self._parse_html(content)
        else:
            # Plain text or wiki markup
            elements = self._parse_plain_text(content)

        return {
            'title': title,
            'author': page.get('author', ''),
            'created_date': page.get('created_date', ''),
            'updated_date': page.get('updated_date', ''),
            'labels': page.get('labels', []),
            'elements': elements
        }

    def _parse_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML/XHTML content."""
        parser = ConfluenceHTMLParser()
        parser.feed(html_content)
        return parser.content_elements

    def _parse_plain_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse plain text content with basic wiki markup."""
        elements = []
        lines = text.split('\n')

        in_code_block = False
        code_block_lines = []

        for line in lines:
            line = line.rstrip()

            # Code blocks
            if line.startswith('```'):
                if in_code_block:
                    elements.append({
                        'type': 'code_block',
                        'language': '',
                        'text': '\n'.join(code_block_lines)
                    })
                    code_block_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_block_lines.append(line)
                continue

            # Headings
            if line.startswith('#'):
                match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if match:
                    level = len(match.group(1))
                    text = match.group(2)
                    elements.append({
                        'type': 'heading',
                        'level': level,
                        'text': text
                    })
                    continue

            # Lists
            if line.startswith('* ') or line.startswith('- '):
                # Unordered list
                if not elements or elements[-1]['type'] != 'unordered_list':
                    elements.append({
                        'type': 'unordered_list',
                        'items': []
                    })
                elements[-1]['items'].append(line[2:].strip())
                continue

            if re.match(r'^\d+\.\s', line):
                # Ordered list
                if not elements or elements[-1]['type'] != 'ordered_list':
                    elements.append({
                        'type': 'ordered_list',
                        'items': []
                    })
                item_text = re.sub(r'^\d+\.\s+', '', line)
                elements[-1]['items'].append(item_text)
                continue

            # Paragraphs
            if line.strip():
                elements.append({
                    'type': 'paragraph',
                    'text': line
                })

        return elements


if __name__ == '__main__':
    # Example usage
    parser = ConfluenceParser()

    sample_pages = [
        {
            'title': 'Sample Page 1',
            'content': '''
# Introduction
This is a sample page with **bold** text.

## Section 1
Some content here.

* Item 1
* Item 2
* Item 3
'''
        }
    ]

    result = parser.parse_multiple_pages(sample_pages)
    print(f"Parsed {len(result)} pages")
    for page in result:
        print(f"\nTitle: {page['title']}")
        print(f"Elements: {len(page['elements'])}")