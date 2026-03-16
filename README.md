# Simple Documentation Crawler

A Python-based web crawler that downloads documentation websites and converts them into clean, LLM-optimized Markdown files.

## Features

**Three Crawling Modes:**
- **Normal Mode** – Follows links recursively up to a configurable depth (BFS strategy)
- **Sitemap URL Mode** – Parses `sitemap.xml` from a URL and crawls all listed pages
- **Sitemap File Mode** – Parses a local `sitemap.xml` file and crawls all listed pages

**Smart Filtering:**
- Domain filtering (same domain only)
- URL prefix filtering (e.g., only `/api/` or `/docs/`)
- Configurable HTML element exclusions (navigation, footer, etc.)

**LLM Optimization:**
- Clean Markdown conversion
- Automatic `llms.txt` index generation
- Structured file organization

**Sitemap Support:**
- Standard `sitemap.xml` format
- Sitemap index files (with multiple sub-sitemaps)
- Automatic URL deduplication

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd simple-docs-crawler
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `crawl4ai` – Web crawling framework
- `aiohttp` – Async HTTP client for sitemap fetching

## Quick Start

```bash
# Crawl documentation with default settings
python crawl_docs.py --url https://docs.example.com

# Crawl from sitemap
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap

# Crawl with prefix filter and llms.txt index
python crawl_docs.py --url https://docs.example.com --prefix /api --llms-txt
```

## Usage

### Normal Mode (Link Following)

Follows links on the website up to a configurable depth.

```bash
# Basic crawling
python crawl_docs.py --url https://docs.example.com

# With URL prefix filter (only /api/* pages)
python crawl_docs.py --url https://docs.example.com --prefix /api

# Adjust crawl depth
python crawl_docs.py --url https://docs.example.com --depth 3

# Custom output directory
python crawl_docs.py --url https://docs.example.com --out ./my-docs

# Generate llms.txt index
python crawl_docs.py --url https://docs.example.com --llms-txt
```

### Sitemap URL Mode

Parse a `sitemap.xml` from a URL and crawl all listed pages.

```bash
# Parse sitemap from URL
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap

# With prefix filter (only URLs starting with /docs)
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --prefix /docs

# With llms.txt index
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --llms-txt
```

> [!NOTE]
> In Sitemap URL Mode, the `--depth` option is ignored since all URLs are extracted directly from the sitemap.

### Sitemap File Mode

Parse a local `sitemap.xml` file and crawl all listed pages.

```bash
# Parse local sitemap file
python crawl_docs.py --sitemap-file ./sitemap.xml

# With explicit base URL (for domain filtering and path generation)
python crawl_docs.py --sitemap-file ./sitemap.xml --url https://example.com

# With prefix filter
python crawl_docs.py --sitemap-file ./sitemap.xml --prefix /docs

# With llms.txt index
python crawl_docs.py --sitemap-file ./sitemap.xml --llms-txt

# Complete example with all options
python crawl_docs.py --sitemap-file ./my-sitemap.xml --url https://example.com --prefix /api --out ./api-docs --llms-txt
```

**Sitemap File Mode Specifics:**
- `--url` is **optional**. If not set, the domain is auto-detected from the first URL in the sitemap
- Domain filter is **only** applied when `--url` is explicitly set
- Supports sitemap index files (sub-sitemaps are automatically loaded via HTTP)
- The `--depth` option is ignored
- **Cannot** be combined with `--from-sitemap`

### All Options

```
--url URL              Start URL to crawl (optional with --sitemap-file)
--prefix PREFIX        Only crawl URLs with this path prefix
--depth DEPTH          Maximum crawl depth (default: 5, ignored in sitemap modes)
--out OUTPUT_DIR       Output directory (default: ./docs)
--exclude SELECTORS    CSS selectors to remove (e.g. "nav, footer")
--llms-txt             Generate llms.txt index file
--from-sitemap         Enable Sitemap URL Mode (parse sitemap.xml from URL)
--sitemap-file PATH    Enable Sitemap File Mode (parse local sitemap.xml file)
```

> [!WARNING]
> `--from-sitemap` and `--sitemap-file` cannot be used together.

## Configuration

Default configuration can be customized in [`crawl_docs.py`](crawl_docs.py):

```python
CONFIG = {
    "url": "",
    "url_prefix": "",
    "max_depth": 5,
    "output_dir": "./docs",
    "excluded_selectors": "nav, footer, .sidebar, .navbar, header, .toc, [role='navigation']",
    "generate_llms_txt": True,
    "from_sitemap": False,
    "sitemap_file": "",
}
```

## Examples

### Example 1: RemNote Plugin Documentation (Sitemap URL)

```bash
python crawl_docs.py --url https://plugins.remnote.com/sitemap.xml --from-sitemap --llms-txt
```

### Example 2: Local Sitemap File

```bash
python crawl_docs.py --sitemap-file ./my-sitemap.xml --llms-txt
```

### Example 3: Local Sitemap with Explicit Base URL

```bash
python crawl_docs.py --sitemap-file ./sitemap.xml --url https://example.com --prefix /docs
```

### Example 4: Crawl Only API Documentation (Normal Mode)

```bash
python crawl_docs.py --url https://docs.example.com --prefix /api/v2 --depth 3
```

### Example 5: Multiple Sitemaps (Sitemap Index)

```bash
# From URL
python crawl_docs.py --url https://example.com/sitemap_index.xml --from-sitemap

# From local file
python crawl_docs.py --sitemap-file ./sitemap_index.xml
```

## Output Structure

Crawled pages are saved as Markdown files that mirror the URL structure:

```
output_dir/
├── index.md                          # Homepage
├── api/
│   ├── classes/
│   │   ├── Rem/index.md
│   │   └── Query/index.md
│   └── enums/
│       └── RemType/index.md
└── llms.txt                          # Auto-generated index (optional)
```

## llms.txt Format

When `--llms-txt` is enabled, a structured index file is generated:

```markdown
# RemNote Plugin Documentation
> Auto-generated index of 150 pages from https://plugins.remnote.com
> All pages have been downloaded locally. Use the local file path instead of crawling the URL.

## API Reference

### Classes
- [Rem](https://plugins.remnote.com/api/classes/Rem): Main Rem object class (local: ./api/classes/Rem/index.md)
- [Query](https://plugins.remnote.com/api/classes/Query): Query builder class (local: ./api/classes/Query/index.md)

### Enums
- [RemType](https://plugins.remnote.com/api/enums/RemType): Rem type enumeration (local: ./api/enums/RemType/index.md)
```

## Advanced

### Mode Comparison

| Feature | Normal Mode | Sitemap URL Mode | Sitemap File Mode |
|---------|-------------|------------------|-------------------|
| URL Source | Link Following | sitemap.xml (URL) | sitemap.xml (local) |
| Depth | Configurable | Ignored | Ignored |
| Prefix Filter | ✓ Supported | ✓ Supported | ✓ Supported |
| Domain Filter | ✓ Always active | ✓ Always active | ⚡ Only with `--url` |
| Base URL | Required (`--url`) | Required (`--url`) | Optional (auto-detect) |
| Use Case | Exploratory Discovery | Complete Coverage | Offline/Local |
| Performance | Depends on Depth | Fast (direct URLs) | Fast (direct URLs) |
| Sitemap Index | N/A | ✓ Supported | ✓ Supported |

### Sitemap Technical Details

Both sitemap modes (URL and File) support the same XML formats and use the same parsing logic.

**Supported Sitemap Formats:**

Standard Sitemap:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
</urlset>
```

Sitemap Index:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-part1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-part2.xml</loc>
  </sitemap>
</sitemapindex>
```

**Processing Flow:**

**Sitemap URL Mode (`--from-sitemap`):**
1. Fetch sitemap via HTTP with `aiohttp`
2. Parse XML with `xml.etree.ElementTree` (via `_parse_sitemap_xml()`)
3. Detect sitemap index and recursively load sub-sitemaps via HTTP
4. Apply domain and prefix filters
5. Crawl each URL individually

**Sitemap File Mode (`--sitemap-file`):**
1. Read local XML file from disk
2. Parse XML with `xml.etree.ElementTree` (via `_parse_sitemap_xml()`)
3. Detect sitemap index and load sub-sitemaps via HTTP
4. Apply prefix filter always, domain filter only with `--url`
5. Crawl each URL individually

**Error Handling:**
- **Sitemap unreachable**: Fallback to Normal Mode
- **Invalid XML**: Clear error message
- **Empty sitemap**: Warning and abort
- **Individual URL errors**: Logged, crawling continues

## Troubleshooting

### No URLs Found in Sitemap Mode

- Verify the URL is actually a sitemap.xml
- Check your prefix filter settings
- Test the sitemap URL in your browser

### Timeout Errors

- Sitemap might be too large or slow
- Check network connection
- Adjust timeout value in [`parse_sitemap()`](crawl_docs.py:152)