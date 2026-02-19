# Scrapling Selectors & Navigation Reference

> **v0.4:** `css_first()`/`xpath_first()` removed. Use `.css('.sel').first`, `.css('.sel')[0]`, or `.css('.sel').get()`. `css('::text')` and `css('::attr()')` now return `Selector` objects (tag `"#text"`), not `TextHandler`. `.first`/`.last` are safe — return `None` instead of raising `IndexError`.

## CSS Selectors

```python
# Multiple elements → Selectors list
elements = page.css('.product-card')

# Single element (safe — None if missing)
element = page.css('.product-title').first
element = page.css('.product-title').last

# Index access
element = page.css('.product-title')[0]

# get() — first element as TextHandler (alias: extract_first)
text = page.css('.title').get()

# getall() — all elements as TextHandlers (alias: extract)
texts = page.css('.title').getall()

# With pseudo-elements (Scrapy-style) — return Selector objects
selectors = page.css('.title::text')         # Text nodes as Selectors
selectors = page.css('a::attr(href)')        # Attributes as Selectors
```

## XPath Selectors

```python
# Multiple elements
elements = page.xpath('//a[contains(@href, "product")]')

# Single element (safe)
element = page.xpath('//div[@class="content"]').first

# Text extraction
texts = page.xpath('//h1/text()')
```

## BeautifulSoup-Style Methods

```python
# find / find_all
element = page.find('div', class_='product')
elements = page.find_all('a', attrs={'data-type': 'link'})

# By ID
element = page.find(id='main-content')

# By tag
divs = page.find_all('div')
```

## Text Search

```python
# Find by text content (no tag= param — find_by_text searches all elements)
element = page.find_by_text('Add to Cart')

# Partial match
element = page.find_by_text('Cart', partial=True)

# To restrict to a specific tag, filter after
button = page.css('button').filter(lambda el: el.text == 'Add to Cart').first

# Find by regex pattern
import re
element = page.find_by_regex(r'Price: \$\d+')
element = page.find_by_regex(re.compile(r'\d+ items'))
```

## Similar Element Discovery

Find elements with matching structure:

```python
element = page.css('.product-card').first

# Find similar elements — called on the element itself, not the page
similar = element.find_similar()

# With options
similar = element.find_similar(
    similarity_threshold=0.2,  # 0.0-1.0 (default: 0.2 = 20% attribute similarity)
    ignore_attributes=['id'],  # Attributes to skip (default: ('href', 'src'))
    match_text=False           # Include text content in comparison
)
```

## Adaptive Selectors (Auto-Relocate)

Elements survive website changes via similarity matching:

```python
# Save element properties on first visit
element = page.css('#product-1', auto_save=True).first

# Auto-relocate when website changes
element = page.css('#product-1', adaptive=True).first

# Manual save/retrieve/relocate
page.save(element, 'my_product')
element_dict = page.retrieve('my_product')
relocated = page.relocate(element_dict)
```

### Storage Configuration

```python
from scrapling import Selector
from scrapling.core.storage import SQLiteStorageSystem

adaptor = Selector(
    html,
    url='https://example.com',         # Required for domain-based storage
    adaptive=True,
    storage=SQLiteStorageSystem,        # Pass the class, not the string 'sqlite'
    storage_args={'storage_file': './selectors.db'}  # Key is storage_file, not path
)

# Simplest approach — omit storage entirely, defaults to SQLite in the library directory
adaptor = Selector(html, url='https://example.com', adaptive=True)
```

See [adaptive.md](adaptive.md) for complete adaptive scraping guide.

---

## Element Navigation

### Parent/Child/Sibling

```python
element = page.css('.target').first

# Navigation
parent = element.parent
children = element.children
first_child = element.children.first   # children is a Selectors list
last_child = element.children.last
below_elements = element.below_elements  # All nested descendants

# Siblings
all_siblings = element.siblings

# Adjacent elements (property names are next/previous, not next_sibling/prev_sibling)
next_el = element.next
prev_el = element.previous
```

### Traversal Methods

```python
# Iterate ancestors (iterancestors is a @property returning a Generator)
for ancestor in element.iterancestors:
    print(ancestor.tag)

# Find ancestor with predicate
ancestor = element.find_ancestor(lambda el: el.has_class('container'))

# Get path (all ancestors)
path = element.path

# Find descendants
descendants = element.find_all('span')

# Chaining
result = page.css('.container').first.css('.item').css('.title').first
```

---

## Text Extraction

```python
element = page.css('.content').first

# Basic text (returns TextHandler - enhanced string)
text = element.text                    # Inner text
text = element.get_all_text()          # Recursive text from all descendants

# Cleaned text (clean_text property doesn't exist — use TextHandler.clean())
text = element.text.clean()            # Whitespace normalized

# Raw HTML
html = element.html_content            # @property
pretty = element.prettify              # @property — returns TextHandler (formatted HTML)

# TextHandler methods (string subclass)
text = element.text
text.re(r'Price: (\$[\d.]+)')         # Regex match
text.re_first(r'\d+')                  # First match only
text.json()                            # Parse JSON
text.clean()                           # Remove whitespace/entities
text.sort()                            # Sort characters
```

---

## Attribute Access

```python
element = page.css('a.link').first

# Get attributes
href = element.attrib['href']          # Direct dict-style access (KeyError if missing)
href = element.attrib.get('href')      # Safe access via AttributesHandler.get()
href = element.attrib.get('href', '#') # With default (element.get() takes no args — use attrib.get())

# All attributes (AttributesHandler - read-only dict)
attrs = element.attrib
attrs.json_string                      # Serialize all attrs to JSON — returns bytes
attrs.search_values('http')            # Find attrs containing value
attrs.search_values('btn', partial=True)  # Partial match

# Check existence
has_class = element.has_class('active')
```

---

## Selectors Class (List Container)

When `.css()` or `.xpath()` returns multiple elements, they're wrapped in a `Selectors` list:

```python
# Selectors inherits from list with extra methods
products = page.css('.product-card')

# Safe first/last (None instead of IndexError)
first = products.first
last = products.last

# List-like operations
products.length                        # Count (JavaScript-style)
len(products)                          # Count (Python-style)

# get/getall
first_text = products.get()            # First as TextHandler
all_texts = products.getall()          # All as TextHandlers

# Chain queries across all elements
all_prices = products.css('.price')    # CSS on each element
all_links = products.xpath('//a')      # XPath on each element

# Regex on all elements
matches = products.re(r'\$\d+')

# Filter and search
results = products.filter(lambda el: el.has_class('sale'))
first_match = products.search(lambda el: el.text == 'Featured')
```

---

## Iteration Patterns

```python
# Iterate elements
for product in page.css('.product-card'):
    title = product.css('.title').first.text
    price = product.css('.price').first.text
    link = product.css('a::attr(href)').get()

# List comprehension
prices = [el.text for el in page.css('.price')]

# With filtering using Selectors.filter()
active = page.css('.item').filter(lambda el: el.has_class('active'))
```

---

## Auto Selector Generation

Generate robust selectors for any element:

```python
element = page.css('.product').first

# All four are @property — access without parentheses
css = element.generate_css_selector
xpath = element.generate_xpath_selector

# Full path selectors (from root)
full_css = element.generate_full_css_selector
full_xpath = element.generate_full_xpath_selector
```

---

## Parser-Only Usage

Use without fetching (for existing HTML):

```python
from scrapling.parser import Selector

html = '<html><body><div class="content">Hello</div></body></html>'
page = Selector(html)

# Now use all selection methods
content = page.css('.content').first.text
```
