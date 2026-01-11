# Scrapling CLI Reference

## Installation

```bash
pip install "scrapling[shell]"
scrapling install  # Install browsers
```

---

## Interactive Shell

```bash
scrapling shell
```

IPython-based shell with shortcuts and utilities for interactive scraping.

---

## Extract Commands

Scrape websites from terminal without coding. Output format determined by extension.

### HTTP Requests

```bash
# GET request
scrapling extract get "https://example.com" output.md

# With CSS selector
scrapling extract get "https://blog.com" articles.md --css-selector "article"

# POST with JSON
scrapling extract post "https://api.site.com" response.json --json '{"key": "value"}'

# POST with form data
scrapling extract post "https://site.com/form" out.txt --data "name=test&email=test@example.com"

# PUT request
scrapling extract put "https://api.site.com/item/1" out.json --json '{"updated": true}'

# DELETE request
scrapling extract delete "https://api.site.com/item/1" out.json
```

### Dynamic Content (Browser)

```bash
# JavaScript-rendered pages
scrapling extract fetch "https://spa-app.com" content.md --network-idle

# Wait for element
scrapling extract fetch "https://site.com" out.html --wait-selector ".loaded"

# Use installed Chrome
scrapling extract fetch "https://site.com" out.md --real-chrome

# Disable resources for speed
scrapling extract fetch "https://site.com" out.md --disable-resources
```

### Cloudflare Bypass

```bash
# Auto-solve Cloudflare challenges
scrapling extract stealthy-fetch "https://protected.com" out.html --solve-cloudflare

# With WebRTC blocking
scrapling extract stealthy-fetch "https://site.com" out.html --solve-cloudflare --block-webrtc

# Canvas fingerprint protection
scrapling extract stealthy-fetch "https://site.com" out.html --hide-canvas
```

---

## Common Options

### HTTP Request Options

| Option | Description |
|--------|-------------|
| `-s, --css-selector TEXT` | Extract specific content |
| `-H, --headers TEXT` | Custom headers (repeatable) |
| `--cookies TEXT` | Cookies as "name1=value1;name2=value2" |
| `--timeout INTEGER` | Timeout in seconds (default: 30) |
| `--proxy TEXT` | Proxy URL |
| `-p, --params TEXT` | Query parameters (repeatable) |
| `--follow-redirects / --no-follow-redirects` | Handle redirects (default: True) |
| `--verify / --no-verify` | SSL verification (default: True) |
| `--impersonate TEXT` | Browser impersonation (chrome, firefox) |
| `--stealthy-headers` | Enable stealth headers (default: True) |

### POST/PUT Options

| Option | Description |
|--------|-------------|
| `-d, --data TEXT` | Form data as string |
| `-j, --json TEXT` | JSON payload |

### Browser Options (fetch)

| Option | Description |
|--------|-------------|
| `--headless / --no-headless` | Headless mode (default: True) |
| `--disable-resources / --enable-resources` | Drop fonts/images/media |
| `--network-idle / --no-network-idle` | Wait for network |
| `--timeout INTEGER` | Timeout in ms (default: 30000) |
| `--wait INTEGER` | Extra wait after load |
| `--wait-selector TEXT` | Wait for element |
| `--locale TEXT` | Browser locale |
| `--real-chrome / --no-real-chrome` | Use installed Chrome |

### Stealth Options (stealthy-fetch)

| Option | Description |
|--------|-------------|
| `--solve-cloudflare / --no-solve-cloudflare` | Auto-solve Cloudflare |
| `--block-webrtc / --allow-webrtc` | WebRTC blocking |
| `--hide-canvas / --show-canvas` | Canvas noise |

---

## Output Formats

File extension determines output:

| Extension | Format |
|-----------|--------|
| `.html` | Raw HTML |
| `.md` | Converted Markdown |
| `.txt` | Plain text content |

---

## Help

```bash
scrapling --help
scrapling extract --help
scrapling extract get --help
```
