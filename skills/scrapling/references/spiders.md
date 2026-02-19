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

## Concurrent Crawling

```python
class MySpider(Spider):
    name = "concurrent"
    start_urls = ["https://example.com/"]
    concurrency = 10           # Max simultaneous requests (default: 8)
    download_delay = 0.5       # Seconds between requests (default: 0)
    domain_delay = {           # Per-domain throttle
        "example.com": 1.0
    }
```

---

## Multi-Session (HTTP + Browser)

Route requests to different fetcher sessions by ID:

```python
class HybridSpider(Spider):
    name = "hybrid"
    start_urls = ["https://example.com/listing"]

    async def parse(self, response: Response):
        for link in response.css('a.product::attr(href)').getall():
            # Route product pages through browser session
            yield response.follow(link, session_id='browser', callback=self.parse_product)

    async def parse_product(self, response: Response):
        yield {"title": response.css('h1').get()}

MySpider().start(sessions={
    'default': {'fetcher': 'http'},          # Fast HTTP for listings
    'browser': {'fetcher': 'dynamic', 'headless': True}  # Browser for products
})
```

Sessions are initialized lazily on first use.

---

## Pause & Resume

```python
MySpider().start(checkpoint='./crawl_state.db')
# Press Ctrl+C to gracefully shut down
# Re-run to resume from the last checkpoint
```

---

## Streaming Mode

Process items as they arrive in real time:

```python
import asyncio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(item)  # Items arrive as they're scraped

asyncio.run(main())
```

---

## Blocked Request Detection

Automatically detects and retries blocked requests:

```python
class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    def is_blocked(self, response: Response) -> bool:
        # Custom detection logic — default checks status codes
        return response.status == 403 or 'captcha' in response.text.lower()
```

---

## Built-in Export

```python
result = MySpider().start()

result.items.to_json('output.json')
result.items.to_jsonl('output.jsonl')
```

Via lifecycle hooks (streaming pipeline):

```python
class MySpider(Spider):
    async def on_scraped_item(self, item):
        await my_pipeline.process(item)
```

---

## Lifecycle Hooks

Override any of these async methods:

```python
class MySpider(Spider):
    async def on_start(self):
        """Called before crawl begins."""
        self.db = await connect_db()

    async def on_close(self):
        """Called after crawl finishes."""
        await self.db.close()

    async def on_error(self, request, exception):
        """Called when a request raises an exception."""
        print(f"Error on {request.url}: {exception}")

    async def on_scraped_item(self, item):
        """Called for each yielded item — use as pipeline."""
        await self.db.insert(item)
```

---

## Crawl Stats

```python
result = MySpider().start()
stats = result.stats

stats.requests_count       # Total requests made
stats.responses_count      # Total responses received
stats.bytes_downloaded     # Total bytes
stats.status_codes         # Dict of {code: count}
stats.per_domain           # Per-domain breakdown
stats.per_session          # Per-session breakdown
stats.log_level_counts     # {DEBUG: n, ERROR: n, ...}
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
from scrapling.spiders import Spider, Response
from scrapling import ProxyRotator

proxies = ProxyRotator(["http://p1:8080", "http://p2:8080"])

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/catalog"]
    concurrency = 5
    download_delay = 0.3

    async def parse(self, response: Response):
        for card in response.css('.product-card'):
            link = card.css('a::attr(href)').get()
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

    async def parse_product(self, response: Response):
        yield {
            "title": response.css('h1').get(),
            "price": response.css('.price').get(),
            "url": response.url,
        }

result = ProductSpider().start(
    proxy_rotator=proxies,
    checkpoint='./state.db',
    use_uvloop=True
)
result.items.to_jsonl('products.jsonl')
print(result.stats)
```
