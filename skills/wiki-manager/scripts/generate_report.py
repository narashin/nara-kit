#!/usr/bin/env python3
"""
Generate Report - End-to-end Confluence to PDF workflow

Usage:
    python generate_report.py input_pages.json output_report.pdf
    python generate_report.py input_pages.json output_report.pdf --title "Custom Report Title"
"""

import sys
import json
import argparse
from pathlib import Path
from confluence_parser import ConfluenceParser
from pdf_generator import PDFReportGenerator


def load_pages_from_json(json_path: str) -> list:
    """Load Confluence pages from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle both array of pages and object with pages key
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'pages' in data:
        return data['pages']
    else:
        raise ValueError("JSON must be an array of pages or object with 'pages' key")


def generate_report(input_path: str, output_path: str, title: str = "Confluence Report"):
    """
    Generate PDF report from Confluence pages.

    Args:
        input_path: Path to JSON file containing Confluence pages
        output_path: Path for output PDF file
        title: Title for the report
    """
    print(f"Loading pages from: {input_path}")
    pages = load_pages_from_json(input_path)
    print(f"Loaded {len(pages)} pages")

    print("Parsing Confluence content...")
    parser = ConfluenceParser()
    parsed_pages = parser.parse_multiple_pages(pages)
    print(f"Parsed {len(parsed_pages)} pages")

    print(f"Generating PDF report: {output_path}")
    generator = PDFReportGenerator()
    generator.create_report(parsed_pages, output_path, title)

    print(f"✓ Report generated successfully: {output_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate PDF report from Confluence pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_report.py pages.json report.pdf
  python generate_report.py pages.json report.pdf --title "Q1 2024 Report"

Input JSON format:
  [
    {
      "title": "Page Title",
      "content": "<p>Page content...</p>",
      "author": "John Doe",
      "created_date": "2024-01-15"
    },
    ...
  ]
"""
    )

    parser.add_argument('input', help='Input JSON file with Confluence pages')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument('--title', '-t', default='Confluence Report',
                        help='Report title (default: Confluence Report)')
    parser.add_argument('--font', '-f', default='Helvetica',
                        help='Font family (default: Helvetica)')
    parser.add_argument('--no-toc', action='store_true',
                        help='Disable table of contents')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        generate_report(args.input, args.output, args.title)
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()