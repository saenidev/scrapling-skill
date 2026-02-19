# Scrapling Fetchers Reference

> **v0.4:** `Response.body` is always `bytes`. Browser fetchers now auto-retry by default (`retries=3`, `retry_delay=1`). New: `blocked_domains`, `Response.meta`, `Response.follow()`, `ProxyRotator`.

## Global Configuration

Configure parser settings globally for all fetchers:

```python
Fetcher.configure(adaptive=True, encoding="utf-8", keep_comments=False)
```

Or per-request via `selector_config` parameter.

---

## Response Object

All fetchers return a Response inheriting from Selector with HTTP metadata:

```python
page = Fetcher.get('https://example.com')
page.status      # HTTP status code (200, 404, etc.)
page.headers     # Response headers dict
page.cookies     # Cookies dict
page.body        # Raw response content (always bytes in v0.4+)
page.history     # Redirect chain
page.meta        # Metadata dict (includes proxy used, request metadata)
```

### Response.follow()

Create a follow-up Request for use with the Spider framework:

```python
# Designed for spider-style chained navigation
request = response.follow('/next-page', callback=self.parse_detail)
```

---

## Fetcher (Fast HTTP)

Fastest option for simple requests. Uses TLS fingerprint spoofing via `curl_cffi`.

```python
from scrapling.fetchers import Fetcher

# Basic request
page = Fetcher.get('https://example.com')

# With options
page = Fetcher.get(
    'https://example.com',
    impersonate='chrome110',   # chrome110, firefox102, safari, edge
    stealthy_headers=True,     # Anti-detection headers (default: True)
    follow_redirects=True,     # Follow redirects (default: True)
    timeout=30,                # Timeout in seconds (default: 30)
    retries=3,                 # Retry attempts (default: 3)
    http3=True,                # Enable HTTP/3 protocol
    proxy='http://user:pass@proxy:8080'
)

# POST request
page = Fetcher.post('https://api.example.com/data', json={'key': 'value'})
```

### Impersonate Options

Browser TLS fingerprints: `chrome110`, `chrome120`, `firefox102`, `firefox120`, `safari`, `edge`

### Session Support

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page1 = session.get('https://example.com/login')
    page2 = session.get('https://example.com/dashboard')  # Keeps cookies
```

---

## DynamicFetcher (Playwright/JavaScript)

For JavaScript-rendered content. Uses Playwright Chromium or installed Chrome.

```python
from scrapling.fetchers import DynamicFetcher

# Basic fetch
page = DynamicFetcher.fetch('https://spa-app.com', headless=True)

# With all options
page = DynamicFetcher.fetch(
    'https://example.com',
    headless=True,
    network_idle=True,         # Wait for network to settle (500ms inactivity)
    wait=2000,                 # Extra wait in ms
    wait_selector='.loaded',   # Wait for element
    wait_selector_state='visible',  # attached|detached|visible|hidden
    real_chrome=True,          # Use installed Chrome (more authentic)
    disable_resources=True,    # Block fonts/images/media (~25% faster)
    google_search=True,        # Set Google as referrer (default: True)
    locale='en-US',            # Browser locale
    timezone_id='America/New_York',  # Browser timezone
    timeout=30000,             # Timeout in ms (default: 30000)
    retries=3,                 # Auto-retry on failure (default: 3)
    retry_delay=1,             # Seconds between retries (default: 1)
    blocked_domains=['ads.example.com', 'tracker.io'],  # Block domains (subdomains auto-matched)
    extra_headers={'X-Custom': 'value'},
    proxy='http://proxy:8080'
)

# Connect to remote browser via CDP
page = DynamicFetcher.fetch('https://example.com', cdp_url='http://localhost:9222')

# Custom page action (runs after network idle, before wait_selector)
def scroll_page(page):
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_page)
```

### Session Support

```python
from scrapling.fetchers import DynamicSession

# Tab pooling for concurrent fetches
with DynamicSession(headless=True, max_pages=5) as session:
    page = session.fetch('https://example.com')
    stats = session.get_pool_stats()  # total, busy, max pages
```

---

## StealthyFetcher (Anti-Bot Bypass)

Maximum stealth using Camoufox (modified Firefox). Best for protected sites.

**Built-in protections:** Cloudflare bypass, CDP/WebRTC leak prevention, headless detection patching, canvas fingerprint noise, Google referer spoofing, autoplay blocking.

```python
from scrapling.fetchers import StealthyFetcher

# Cloudflare bypass (requires 60s+ timeout for challenge solving)
page = StealthyFetcher.fetch(
    'https://cloudflare-protected.com',
    solve_cloudflare=True,     # Auto-solve Cloudflare challenges
    headless=True,
    timeout=60000              # Min 60s for Cloudflare
)

# Full stealth mode
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True,
    humanize=True,             # Human-like mouse movement
    hide_canvas=True,          # Canvas fingerprint noise
    geoip=True,                # Match IP geolocation
    os_randomize=True,         # Random OS fingerprint
    block_webrtc=True,         # Block WebRTC leaks
    google_search=True,        # Set Google as referrer (default: True)
    disable_ads=True,          # Install uBlock Origin
    blocked_domains=['tracker.io']  # Block specific domains
)
```

### All StealthyFetcher Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `headless` | bool | Hide browser window |
| `solve_cloudflare` | bool | Auto-solve Cloudflare (JS, interactive, invisible, embedded) |
| `humanize` | bool/float | Human mouse movement (True or max seconds) |
| `hide_canvas` | bool | Canvas fingerprint noise injection |
| `geoip` | bool | Use IP geolocation for timezone/language |
| `os_randomize` | bool | Randomize OS fingerprint |
| `block_webrtc` | bool | Block WebRTC entirely |
| `allow_webgl` | bool | Keep WebGL enabled (recommended) |
| `google_search` | bool | Set Google as referrer (default: True) |
| `disable_ads` | bool | Install uBlock Origin |
| `block_images` | bool | Don't load images |
| `disable_resources` | bool | Drop fonts/media/beacons (~25% faster) |
| `blocked_domains` | list | Block requests to these domains (subdomains auto-matched) |
| `proxy` | str/dict | Proxy server config |
| `timeout` | int | Timeout in ms (default: 30000, use 60000+ for Cloudflare) |
| `retries` | int | Auto-retry on failure (default: 3) |
| `retry_delay` | int | Seconds between retries (default: 1) |
| `network_idle` | bool | Wait for network to settle |
| `wait` | int | Extra wait in milliseconds |
| `wait_selector` | str | CSS selector to wait for |
| `wait_selector_state` | str | attached/detached/visible/hidden |
| `page_action` | callable | Custom Playwright page function |
| `extra_headers` | dict | Additional HTTP headers |
| `cookies` | list | Cookies to set |

### Session Support

```python
from scrapling.fetchers import StealthySession

# Tab pooling for concurrent stealth fetches
with StealthySession(headless=True, solve_cloudflare=True, max_pages=5) as session:
    page = session.fetch('https://protected-site.com')
    stats = session.get_pool_stats()  # total, busy, max pages
```

---

## Proxy Rotation

Thread-safe proxy rotation across all fetchers and sessions.

```python
from scrapling import ProxyRotator

# Basic rotation (round-robin by default)
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://user:pass@proxy2:8080",
    "socks5://proxy3:1080"
])

# Use with any fetcher
page = Fetcher.get('https://example.com', proxy_rotator=rotator)
page = DynamicFetcher.fetch('https://example.com', proxy_rotator=rotator)
page = StealthyFetcher.fetch('https://example.com', proxy_rotator=rotator)

# Per-request override (bypasses rotator for that call)
page = Fetcher.get('https://example.com', proxy_rotator=rotator, proxy='http://specific:8080')
```

### Custom Rotation Strategy

```python
class MyRotator(ProxyRotator):
    def get_proxy(self):
        # Custom logic — e.g., weighted, sticky per domain, etc.
        return self.proxies[my_selection_logic()]
```

---

## Async Variants

All fetchers have async equivalents:

```python
from scrapling.fetchers import AsyncFetcher, AsyncStealthyFetcher

async def scrape():
    page = await AsyncFetcher.get('https://example.com')
    page = await AsyncStealthyFetcher.fetch('https://protected.com')
```

---

## Fetcher Selection Guide

| Scenario | Use |
|----------|-----|
| Static HTML, no protection | `Fetcher` |
| Need cookies/session | `FetcherSession` |
| JavaScript-rendered content | `DynamicFetcher` |
| Cloudflare/anti-bot protection | `StealthyFetcher` |
| High-volume, speed critical | `Fetcher` with `impersonate` |
| Maximum stealth needed | `StealthyFetcher` with all stealth options |
| Multiple proxy IPs | Any fetcher + `ProxyRotator` |
| Multi-page crawl | `Spider` (see [spiders.md](spiders.md)) |
