# Adaptive Scraping Reference

Adaptive scraping enables scrapers to survive website changes by intelligently tracking and relocating elements using similarity matching—no AI required.

---

## How It Works

### Save Phase

On first visit with `auto_save=True`, Scrapling stores unique element properties:
- Tag name
- Text content
- Attributes
- Sibling information
- Parent information
- DOM path (tag names only)

### Match Phase

When original selector fails and `adaptive=True` is enabled:
1. Retrieves stored properties for that selector
2. Calculates similarity scores against current page elements
3. Returns element with highest similarity percentage

---

## Usage

### CSS/XPath Selection

```python
# First visit - save element properties (returns Selectors list; use .first for single element)
element = page.css('#product-1', auto_save=True).first

# After website changes - auto-relocate
element = page.css('#product-1', adaptive=True).first

# XPath works the same way
element = page.xpath('//div[@id="product"]', auto_save=True).first
element = page.xpath('//div[@id="product"]', adaptive=True).first
```

The selector string serves as the identifier for storage/retrieval.

### Manual Save/Retrieve

For elements found via other methods:

```python
# Find element any way you want
element = page.find_by_text('Add to Cart', tag='button')

# Manually save with custom identifier
page.save(element, 'cart_button')

# Later, retrieve and relocate
element_dict = page.retrieve('cart_button')
relocated = page.relocate(element_dict)
```

---

## Storage Configuration

### Default SQLite

```python
from scrapling import Adaptor

adaptor = Adaptor(
    html,
    url='https://example.com',  # Required - used for domain separation
    auto_match=True,
    storage='sqlite',           # Default
    storage_args={'path': './selectors.db'}
)
```

### Global Configuration

```python
from scrapling.fetchers import Fetcher

Fetcher.configure(
    adaptive=True,
    storage='sqlite',
    storage_args={'path': './my_storage.db'}
)
```

### Domain-Based Organization

Storage is organized by domain to prevent cross-site data contamination. The `url` parameter is required to extract the domain.

---

## Best Practices

1. **Save on first run** - Use `auto_save=True` during initial scraping
2. **Enable adaptive on subsequent runs** - Use `adaptive=True` when structure may have changed
3. **Provide URL** - Always include URL for proper domain-based storage
4. **Test relocations** - Verify adaptive selectors find correct elements after changes

---

## Limitations

1. **First element only** - Only properties of the first matched element are saved
2. **Requires storage** - Must configure storage for persistence across runs
3. **Similarity-based** - Not guaranteed to find exact match if page changes dramatically
4. **Domain required** - URL must be provided for storage organization
