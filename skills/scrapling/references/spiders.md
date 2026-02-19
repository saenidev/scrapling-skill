# Scrapling Spider Framework Reference

Introduced in v0.4. Async crawling framework built on `anyio` for structured, large-scale scraping. Scrapy-like API.

```bash
pip install scrapling
scrapling install  # Install browsers
```

---

## Basic Spider

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}

MySpider().start()
```

---

## Architecture

- **`start_urls`** — seed URLs, fetched concurrently on start
- **`parse()`** — default async callback; `yield` dicts (items) or `Request` objects (follow links)
- **`Request`/`Response`** — thin wrappers around fetchers, carrying metadata and callbacks
- **Priority queue** — requests are ordered by priority (lower = sooner)
- **Sessions** — configured via `configure_sessions()` override; first session added is the default

---

## Yielding Items and Requests

```python
async def parse(self, response: Response):
    # Yield scraped items
    yield {"title": response.css('h1').get(), "url": response.url}

    # Follow links to a different callback
    for link in response.css('a.next-page::attr(href)').getall():
        yield response.follow(link, callback=self.parse_next)

async def parse_next(self, response: Response):
    yield {"data": response.css('.content').get()}
```

---

## Concurrency Settings

Class attributes to configure crawl behaviour:

```python
class MySpider(Spider):
    name = "concurrent"
    start_urls = ["https://example.com/"]

    concurrent_requests: int = 4          # Max simultaneous requests (default: 4)
    concurrent_requests_per_domain: int = 0  # Per-domain concurrency cap (0 = unlimited)
    download_delay: float = 0.0           # Seconds between requests (default: 0)
    max_blocked_retries: int = 3          # Max retries for blocked responses (default: 3)
```

---

## Session Configuration (Multi-Session)

Override `configure_sessions()` to register fetcher sessions. The first added is the default.
Use `sid=` on `Request`/`response.follow()` to route to a specific session.

```python
from scrapling.fetchers import FetcherSession, AsyncDynamicSession
from scrapling.spiders import Spider, Response, Request

class HybridSpider(Spider):
    name = "hybrid"
    start_urls = ["https://example.com/listing"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession())                            # Fast HTTP for listings
        manager.add("browser", AsyncDynamicSession(headless=True), lazy=True)  # Browser for products

    async def parse(self, response: Response):
        for link in response.css('a.product::attr(href)').getall():
            # Route product pages through the browser session
            yield response.follow(link, sid='browser', callback=self.parse_product)

    async def parse_product(self, response: Response):
        yield {"title": response.css('h1').get()}

HybridSpider().start()
```

`lazy=True` defers session startup until the first request uses it.

---

## Pause & Resume

`crawldir` is passed to the **constructor**, not `start()`:

```python
# Pass crawldir to enable checkpoint persistence
spider = MySpider(crawldir='./crawl_state/')
spider.start()
# Press Ctrl+C to gracefully shut down; re-run to resume from checkpoint
```

---

## Streaming Mode

Process items as they arrive in real time:

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(item)  # Items arrive as they're scraped
        # Access real-time stats directly on the spider instance
        print(f"Items so far: {spider.stats.items_scraped}")

anyio.run(main)  # NOT asyncio.run — Scrapling is built on anyio
```

---

## Blocked Request Detection

Override `is_blocked()` (must be `async`) for custom detection logic:

```python
class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def is_blocked(self, response: Response) -> bool:
        # Default checks status codes in BLOCKED_CODES set
        # Override for custom detection:
        return response.status == 403 or 'captcha' in response.css('body').get('', '').lower()
```

Default blocked codes: `{401, 403, 407, 429, 444, 500, 502, 503, 504}`

---

## Built-in Export

```python
result = MySpider().start()

result.items.to_json('output.json')           # JSON array
result.items.to_json('output.json', indent=True)  # Pretty-printed
result.items.to_jsonl('output.jsonl')         # JSON Lines (one object per line)
```

---

## Lifecycle Hooks

Override any of these async methods:

```python
class MySpider(Spider):
    async def on_start(self, resuming: bool = False):
        """Called before crawl begins. resuming=True if resuming from checkpoint."""
        self.db = await connect_db()

    async def on_close(self):
        """Called after crawl finishes."""
        await self.db.close()

    async def on_error(self, request, error: Exception):
        """Called when a request raises an exception."""
        print(f"Error on {request.url}: {error}")

    async def on_scraped_item(self, item: dict):
        """Called for each yielded item. Return the item to keep it, None to drop it silently."""
        await self.db.insert(item)
        return item  # Must return item (or None to drop)
```

---

## Crawl Stats

`CrawlStats` dataclass on `result.stats`:

```python
result = MySpider().start()
stats = result.stats

stats.requests_count               # Total requests made
stats.failed_requests_count        # Failed requests
stats.blocked_requests_count       # Blocked + retried requests
stats.items_scraped                # Items yielded and kept
stats.items_dropped                # Items dropped (on_scraped_item returned None)
stats.response_bytes               # Total bytes downloaded
stats.response_status_count        # Dict of {"status_200": n, "status_404": n, ...}
stats.domains_response_bytes       # Per-domain bytes: {"example.com": n}
stats.sessions_requests_count      # Per-session request count: {"default": n}
stats.log_levels_counter           # {"debug": n, "info": n, "warning": n, "error": n, "critical": n}
stats.elapsed_seconds              # Total crawl duration
stats.requests_per_second          # Throughput

print(stats.to_dict())             # Full stats as plain dict
```

---

## Proxy Rotation with Spider

Use `ProxyRotator` via session configuration:

```python
from scrapling.fetchers import FetcherSession
from scrapling.engines.toolbelt import ProxyRotator

proxies = ProxyRotator(["http://p1:8080", "http://p2:8080"])

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession(proxy_rotator=proxies))
```

---

## Performance

```python
# Use uvloop for faster async execution (install: pip install uvloop)
MySpider().start(use_uvloop=True)
```

---

## Full Example

```python
from scrapling.fetchers import FetcherSession, AsyncDynamicSession
from scrapling.engines.toolbelt import ProxyRotator
from scrapling.spiders import Spider, Response

proxies = ProxyRotator(["http://p1:8080", "http://p2:8080"])

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/catalog"]
    concurrent_requests = 5
    download_delay = 0.3

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession(proxy_rotator=proxies))
        manager.add("browser", AsyncDynamicSession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for card in response.css('.product-card'):
            link = card.css('a::attr(href)').get()
            yield response.follow(link, sid='browser', callback=self.parse_product)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "title": response.css('h1').get(),
            "price": response.css('.price').get(),
            "url": response.url,
        }

    async def on_scraped_item(self, item):
        return item  # Return item to keep; return None to drop

result = ProductSpider(crawldir='./state/').start(use_uvloop=True)
result.items.to_jsonl('products.jsonl')
print(result.stats.to_dict())
```
