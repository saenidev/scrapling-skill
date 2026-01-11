# Scrapling MCP Server Reference

MCP (Model Context Protocol) server enables AI assistants like Claude to perform web scraping through conversational interfaces.

---

## Installation

```bash
pip install "scrapling[ai]"
scrapling install  # Install browsers
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `get` | Standard HTTP requests with browser fingerprint impersonation |
| `bulk_get` | Asynchronous multi-URL requests |
| `fetch` | Dynamic content scraping using Chromium/Chrome |
| `bulk_fetch` | Concurrent browser-based scraping across tabs |
| `stealthy_fetch` | Anti-bot bypass for Cloudflare protection |
| `bulk_stealthy_fetch` | Parallel stealth scraping |

---

## Key Features

### CSS Selector Support

Pass CSS selectors to extract specific content before AI processing:

```
"Scrape https://example.com, extract only .article-content"
```

This reduces token consumption compared to sending entire pages.

### Smart Content Conversion

Automatic conversion to Markdown or HTML for clean output.

### Parallel Processing

Bulk tools enable concurrent multi-URL fetching within resource constraints.

---

## Claude Desktop Configuration

Add to Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "scrapling",
      "args": ["mcp"]
    }
  }
}
```

---

## Claude Code Configuration

```bash
claude mcp add scrapling -- scrapling mcp
```

Or manually add to `.mcp.json`:

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "scrapling",
      "args": ["mcp"]
    }
  }
}
```

---

## Docker

```bash
docker pull scraplingorg/scrapling
docker run -p 8080:8080 scraplingorg/scrapling mcp --port 8080
```

---

## Usage Examples

Simple prompts:
- "Scrape the main content from https://example.com"
- "Get product prices from https://shop.com using .price selector"
- "Fetch https://protected-site.com with Cloudflare bypass"

Complex workflows:
- "Bulk fetch these 5 URLs and extract article titles"
- "Scrape https://spa-app.com waiting for .content to load"
