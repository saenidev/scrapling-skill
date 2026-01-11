#!/usr/bin/env python3
"""
Scrapling utility: Extract items from a list page.

Usage:
    python scrape_list.py <url> <item_selector> [options]

Example:
    python scrape_list.py "https://example.com/products" ".product-card" \
        --fields "title:.title::text,price:.price::text,link:a::attr(href)" \
        --output products.json

Features:
    - Adaptive selectors for self-healing scraping
    - Resource blocking for faster fetches
    - Fallback to find_similar() when selector fails
"""

import argparse
import json
import csv
import sys
from typing import Optional


def get_fetcher(fetcher_type: str, adaptive: bool = False):
    """Get the appropriate fetcher based on type and configure it."""
    if fetcher_type == "stealth":
        from scrapling.fetchers import StealthyFetcher
        if adaptive:
            StealthyFetcher.configure(adaptive=True)
        return StealthyFetcher
    elif fetcher_type == "dynamic":
        from scrapling.fetchers import DynamicFetcher
        if adaptive:
            DynamicFetcher.configure(adaptive=True)
        return DynamicFetcher
    else:
        from scrapling.fetchers import Fetcher
        if adaptive:
            Fetcher.configure(adaptive=True)
        return Fetcher


def parse_fields(fields_str: str) -> dict:
    """Parse field definitions like 'name:selector,price:.price::text'."""
    fields = {}
    for field in fields_str.split(","):
        if ":" in field:
            name, selector = field.split(":", 1)
            fields[name.strip()] = selector.strip()
    return fields


def extract_field(element, selector: str) -> Optional[str]:
    """Extract a field value from an element using a selector."""
    import re

    if "::text" in selector:
        sel = selector.replace("::text", "")
        el = element.css_first(sel) if sel else element
        return el.text.strip() if el else None

    if "::attr(" in selector:
        match = re.match(r"(.*)::attr\((\w+)\)", selector)
        if match:
            sel, attr = match.groups()
            el = element.css_first(sel) if sel else element
            return el.get(attr) if el else None
        return None

    el = element.css_first(selector)
    return el.text.strip() if el else None


def scrape_page(url: str, item_selector: str, fields: dict, fetcher_type: str,
                solve_cloudflare: bool = False, headless: bool = True,
                adaptive: bool = False, disable_resources: bool = False) -> list:
    """Scrape a single page and extract items."""
    Fetcher = get_fetcher(fetcher_type, adaptive=adaptive)

    fetch_args = {}
    if fetcher_type == "stealth":
        fetch_args = {
            "solve_cloudflare": solve_cloudflare,
            "humanize": True,
            "headless": headless,
            "disable_resources": disable_resources,
            "timeout": 60000 if solve_cloudflare else 30000
        }
        page = Fetcher.fetch(url, **fetch_args)
    elif fetcher_type == "dynamic":
        fetch_args = {
            "headless": headless,
            "network_idle": True,
            "disable_resources": disable_resources
        }
        page = Fetcher.fetch(url, **fetch_args)
    else:
        page = Fetcher.get(url)

    # Check response status
    if hasattr(page, 'status') and page.status >= 400:
        print(f"Warning: HTTP {page.status} response", file=sys.stderr)

    # Try primary selector
    elements = page.css(item_selector, adaptive=adaptive)

    # Fallback to find_similar if no results and we have a reference
    if not elements and adaptive:
        first = page.css_first(item_selector)
        if first:
            elements = page.find_similar(first, similarity_threshold=0.7)
            print(f"Using find_similar fallback, found {len(elements)} elements")

    items = []
    for element in elements:
        item = {}
        for name, selector in fields.items():
            item[name] = extract_field(element, selector)
        items.append(item)

    return items


def save_output(items: list, output_path: str, format: str):
    """Save items to file in specified format."""
    if format == "json":
        with open(output_path, "w") as f:
            json.dump(items, f, indent=2)
    elif format == "csv":
        if items:
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
    print(f"Saved {len(items)} items to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape list items from a webpage")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("item_selector", help="CSS selector for list items")
    parser.add_argument("--fields", required=True,
                        help="Field definitions: name:selector,name2:selector2")
    parser.add_argument("--output", "-o", default="output.json",
                        help="Output file path")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                        help="Output format")
    parser.add_argument("--fetcher", choices=["basic", "dynamic", "stealth"],
                        default="basic", help="Fetcher type to use")
    parser.add_argument("--cloudflare", action="store_true",
                        help="Enable Cloudflare solving (stealth only)")
    parser.add_argument("--visible", action="store_true",
                        help="Show browser window (dynamic/stealth)")
    parser.add_argument("--adaptive", action="store_true",
                        help="Enable adaptive selectors (self-healing)")
    parser.add_argument("--disable-resources", action="store_true",
                        help="Block fonts/images/media for faster fetches")

    args = parser.parse_args()

    fields = parse_fields(args.fields)
    if not fields:
        print("Error: No valid fields specified", file=sys.stderr)
        sys.exit(1)

    print(f"Scraping {args.url}")
    print(f"Item selector: {args.item_selector}")
    print(f"Fields: {list(fields.keys())}")
    if args.adaptive:
        print("Adaptive mode: enabled")

    items = scrape_page(
        args.url,
        args.item_selector,
        fields,
        args.fetcher,
        solve_cloudflare=args.cloudflare,
        headless=not args.visible,
        adaptive=args.adaptive,
        disable_resources=args.disable_resources
    )

    if items:
        save_output(items, args.output, args.format)
    else:
        print("No items found")


if __name__ == "__main__":
    main()
