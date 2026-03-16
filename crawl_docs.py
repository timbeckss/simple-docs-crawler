#!/usr/bin/env python3
"""
Universal Documentation Crawler
Crawls any website and saves it as clean, LLM-optimized Markdown.

Usage:
    # Normal crawling mode (follows links)
    python crawl_docs.py                                      # uses config below
    python crawl_docs.py --url https://plugins.remnote.com/api
    python crawl_docs.py --url https://docs.example.com --prefix /api/v2
    python crawl_docs.py --url https://docs.example.com --depth 3 --out ./my-docs
    
    # Sitemap mode (parses sitemap.xml from URL and crawls all listed URLs)
    python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap
    python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --prefix /docs
    
    # Sitemap file mode (parses local sitemap.xml file and crawls all listed URLs)
    python crawl_docs.py --sitemap-file ./sitemap.xml
    python crawl_docs.py --sitemap-file ./sitemap.xml --url https://example.com
    python crawl_docs.py --sitemap-file ./sitemap.xml --prefix /docs
    
    # Generate llms.txt index after crawling
    python crawl_docs.py --llms-txt
"""

import asyncio
import argparse
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import aiohttp

# ─── Default Configuration ───────────────────────────────────────────────────
# Edit these defaults or override them via CLI arguments

CONFIG = {
    # Start URL to crawl
    "url": "",

    # Only crawl URLs that contain this prefix (set "" to crawl entire domain)
    "url_prefix": "",

    # Maximum crawl depth (1 = only the start page, 5 = go 5 links deep)
    "max_depth": 5,

    # Output directory for Markdown files
    "output_dir": "./docs",

    # HTML selectors to remove (navigation, sidebars, footers, etc.)
    "excluded_selectors": "nav, footer, .sidebar, .navbar, header, .toc, [role='navigation']",

    # Generate an llms.txt index file after crawling
    "generate_llms_txt": True,

    # Parse URL as sitemap.xml and crawl all listed URLs (ignores depth setting)
    "from_sitemap": False,

    # Path to local sitemap.xml file (alternative to from_sitemap)
    "sitemap_file": "",
}
# ─────────────────────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Crawl documentation websites and save as Markdown."
    )
    parser.add_argument("--url", default=CONFIG["url"],
                        help=f"Start URL to crawl (default: {CONFIG['url']})")
    parser.add_argument("--prefix", default=CONFIG["url_prefix"],
                        help=f"Only follow URLs containing this path prefix (default: '{CONFIG['url_prefix']}')")
    parser.add_argument("--depth", type=int, default=CONFIG["max_depth"],
                        help=f"Maximum crawl depth (default: {CONFIG['max_depth']})")
    parser.add_argument("--out", default=CONFIG["output_dir"],
                        help=f"Output directory (default: {CONFIG['output_dir']})")
    parser.add_argument("--exclude", default=CONFIG["excluded_selectors"],
                        help="CSS selectors to strip from pages")
    parser.add_argument("--llms-txt", action="store_true", default=CONFIG["generate_llms_txt"],
                        help="Generate llms.txt index file after crawling")
    parser.add_argument("--from-sitemap", action="store_true", default=CONFIG["from_sitemap"],
                        help="Parse URL as sitemap.xml and crawl all listed URLs (depth is ignored)")
    parser.add_argument("--sitemap-file", default=CONFIG["sitemap_file"],
                        help="Path to local sitemap.xml file (alternative to --from-sitemap)")
    
    args = parser.parse_args()
    
    # Validation: --sitemap-file and --from-sitemap are mutually exclusive
    if args.sitemap_file and args.from_sitemap:
        parser.error("--sitemap-file and --from-sitemap cannot be used together")
    
    return args


def make_url_filter(start_url: str, prefix: str):
    """Only crawl pages within the same domain and matching the prefix."""
    parsed = urlparse(start_url)
    domain = parsed.netloc

    def filter_fn(url: str) -> bool:
        p = urlparse(url)
        if p.netloc != domain:
            return False
        if prefix and not p.path.startswith(prefix):
            return False
        return True

    return filter_fn


def _parse_sitemap_xml(content: str) -> tuple[list[str], bool]:
    """
    Parse sitemap XML content and extract URLs.
    
    Supports:
    - Standard sitemap.xml with <url><loc> entries
    - Sitemap index files with <sitemap><loc> entries
    
    Args:
        content: XML content as string
        
    Returns:
        Tuple of (urls, is_index) where:
        - urls: List of URLs found in the sitemap
        - is_index: True if this is a sitemap index, False if regular sitemap
        
    Raises:
        Exception: If XML cannot be parsed
    """
    try:
        # Parse XML
        root = ET.fromstring(content)
        
        # Handle namespace
        namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Check if it's a sitemap index
        sitemaps = root.findall('.//sm:sitemap/sm:loc', namespace)
        if sitemaps:
            # It's a sitemap index - extract sitemap URLs
            sitemap_urls = [elem.text.strip() for elem in sitemaps if elem.text]
            return sitemap_urls, True
        
        # It's a normal sitemap - extract page URLs
        urls = root.findall('.//sm:url/sm:loc', namespace)
        page_urls = [elem.text.strip() for elem in urls if elem.text]
        return page_urls, False
        
    except Exception as e:
        raise Exception(f"Failed to parse sitemap XML: {e}")


async def parse_sitemap(sitemap_url: str) -> list[str]:
    """
    Parse a sitemap.xml from a URL and extract all URLs.
    
    Supports:
    - Standard sitemap.xml with <url><loc> entries
    - Sitemap index files with <sitemap><loc> entries
    
    Args:
        sitemap_url: URL to the sitemap.xml file
        
    Returns:
        List of URLs found in the sitemap(s)
        
    Raises:
        Exception: If sitemap cannot be fetched or parsed
    """
    all_urls = []
    
    async def fetch_and_parse(url: str) -> tuple[list[str], bool]:
        """Fetch and parse a single sitemap. Returns (urls, is_index)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    content = await response.text()
            
            # Use shared XML parsing function
            return _parse_sitemap_xml(content)
            
        except Exception as e:
            raise Exception(f"Failed to fetch/parse sitemap {url}: {e}")
    
    # Fetch the initial sitemap
    urls, is_index = await fetch_and_parse(sitemap_url)
    
    if is_index:
        # It's a sitemap index - recursively fetch all sub-sitemaps
        print(f"📋 Found sitemap index with {len(urls)} sub-sitemaps")
        for sub_sitemap_url in urls:
            try:
                sub_urls, _ = await fetch_and_parse(sub_sitemap_url)
                all_urls.extend(sub_urls)
                print(f"   ✓ Loaded {len(sub_urls)} URLs from {sub_sitemap_url}")
            except Exception as e:
                print(f"   ✗ Failed to load {sub_sitemap_url}: {e}")
    else:
        # It's a regular sitemap
        all_urls = urls
    
    # Deduplicate URLs
    all_urls = list(dict.fromkeys(all_urls))
    
    return all_urls


async def parse_sitemap_file(file_path: str) -> list[str]:
    """
    Parse a sitemap.xml from a local file and extract all URLs.
    
    Supports:
    - Standard sitemap.xml with <url><loc> entries
    - Sitemap index files with <sitemap><loc> entries (sub-sitemaps are fetched via HTTP)
    
    Args:
        file_path: Path to the local sitemap.xml file
        
    Returns:
        List of URLs found in the sitemap(s)
        
    Raises:
        Exception: If file cannot be read or parsed
    """
    all_urls = []
    
    try:
        # Read file from disk
        content = Path(file_path).read_text(encoding='utf-8')
        
        # Parse XML content
        urls, is_index = _parse_sitemap_xml(content)
        
        if is_index:
            # It's a sitemap index - recursively fetch all sub-sitemaps via HTTP
            print(f"📋 Found sitemap index with {len(urls)} sub-sitemaps")
            for sub_sitemap_url in urls:
                try:
                    # Sub-sitemaps from index are URLs, fetch them via HTTP
                    async with aiohttp.ClientSession() as session:
                        async with session.get(sub_sitemap_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            response.raise_for_status()
                            sub_content = await response.text()
                    
                    sub_urls, _ = _parse_sitemap_xml(sub_content)
                    all_urls.extend(sub_urls)
                    print(f"   ✓ Loaded {len(sub_urls)} URLs from {sub_sitemap_url}")
                except Exception as e:
                    print(f"   ✗ Failed to load {sub_sitemap_url}: {e}")
        else:
            # It's a regular sitemap
            all_urls = urls
        
        # Deduplicate URLs
        all_urls = list(dict.fromkeys(all_urls))
        
        return all_urls
        
    except Exception as e:
        raise Exception(f"Failed to read/parse sitemap file {file_path}: {e}")


def url_to_filepath(url: str, base_url: str, output_dir: Path) -> Path:
    """Convert a URL to a local file path mirroring the URL structure."""
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)

    # Strip the base path prefix so output starts clean
    path = parsed.path
    base_path = base_parsed.path.rstrip("/")
    if path.startswith(base_path):
        path = path[len(base_path):]

    path = path.strip("/")

    if not path:
        return output_dir / "index.md"

    parts = Path(path)
    if parts.suffix:
        # e.g. /api/classes/Rem.html → classes/Rem.md
        return output_dir / parts.with_suffix(".md")
    else:
        # e.g. /api/classes/Rem → classes/Rem/index.md
        return output_dir / parts / "index.md"


def _extract_title_and_desc(md_file: Path) -> tuple[str, str]:
    """Extract H1 title and first description sentence from a Markdown file."""
    title = ""
    desc = ""
    try:
        for line in md_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line == "On this page":
                continue
            if not title and line.startswith("# "):
                title = line[2:].strip()
                continue
            if title and not desc and not line.startswith("#"):
                # Strip markdown links/formatting for a clean description
                import re
                clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
                clean = re.sub(r'[`*_]', '', clean)
                desc = clean[:120].rstrip()
                break
    except Exception:
        pass
    return title, desc


def generate_llms_txt(output_dir: Path, base_url: str):
    """Generate a grouped llms.txt index with titles and descriptions."""
    md_files = sorted(output_dir.rglob("*.md"))
    parsed_base = urlparse(base_url)
    domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

    # Group files by top-level section
    sections: dict[str, list[Path]] = {}
    for f in md_files:
        rel = f.relative_to(output_dir)
        section = rel.parts[0] if len(rel.parts) > 1 else "root"
        sections.setdefault(section, []).append(f)

    # Section display names
    section_labels = {
        "advanced": "Advanced Guides",
        "api": "API Reference",
        "getting-started": "Getting Started",
        "in-depth-tutorial": "In-Depth Tutorial",
        "root": "General",
    }

    lines = [
        f"# RemNote Plugin Documentation",
        f"> Auto-generated index of {len(md_files)} pages from {domain}",
        f"> All pages have been downloaded locally. Use the local file path instead of crawling the URL.",
        "",
    ]

    for section, files in sorted(sections.items()):
        label = section_labels.get(section, section.replace("-", " ").title())
        lines += [f"## {label}", ""]

        # Sub-group api section by type (classes, enums, interfaces)
        if section == "api":
            sub: dict[str, list[Path]] = {}
            for f in files:
                rel = f.relative_to(output_dir)
                sub_key = rel.parts[1] if len(rel.parts) > 2 else "other"
                sub.setdefault(sub_key, []).append(f)
            for sub_label, sub_files in sorted(sub.items()):
                lines.append(f"### {sub_label.title()}")
                lines.append("")
                for f in sub_files:
                    rel = f.relative_to(output_dir)
                    url_path = "/".join(rel.parts).replace("/index.md", "").removesuffix(".md")
                    url = f"{domain}/{url_path}"
                    title, desc = _extract_title_and_desc(f)
                    name = title or (rel.stem if rel.stem != "index" else rel.parent.name)
                    desc_part = f" {desc}" if desc else ""
                    lines.append(f"- [{name}]({url}):{desc_part} (local: {f})")
                lines.append("")
        else:
            for f in files:
                rel = f.relative_to(output_dir)
                url_path = "/".join(rel.parts).replace("/index.md", "").removesuffix(".md")
                url = f"{domain}/{url_path}"
                title, desc = _extract_title_and_desc(f)
                name = title or (rel.stem if rel.stem != "index" else rel.parent.name)
                desc_part = f" {desc}" if desc else ""
                lines.append(f"- [{name}]({url}):{desc_part} (local: {f})")
            lines.append("")

    llms_path = output_dir / "llms.txt"
    llms_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄 llms.txt written to: {llms_path}")


async def crawl(args):
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BFSDeepCrawlStrategy, FilterChain, URLPatternFilter, DomainFilter
    except ImportError:
        print("crawl4ai not installed. Run: pip install crawl4ai")
        return

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved = 0
    failed = 0

    # ─── Sitemap File Mode ───────────────────────────────────────────────────────
    if args.sitemap_file:
        print(f"🔍 Sitemap File Mode: Parsing {args.sitemap_file}")
        print(f"   Prefix filter: '{args.prefix or '(none)'}' | Output: {output_dir}")
        print(f"   Note: --depth is ignored in sitemap file mode\n")
        
        try:
            # Parse local sitemap file and extract URLs
            urls = await parse_sitemap_file(args.sitemap_file)
            
            if not urls:
                print(f"⚠️  Warning: No URLs found in sitemap file {args.sitemap_file}")
                return
            
            print(f"📋 Found {len(urls)} URLs in sitemap file")
            
            # Apply prefix filter
            if args.prefix:
                urls_before = len(urls)
                urls = [u for u in urls if urlparse(u).path.startswith(args.prefix)]
                print(f"   Prefix filter: {urls_before} → {len(urls)} URLs")
                if not urls:
                    print(f"⚠️  Warning: No URLs match the prefix filter")
                    return
            
            # Determine base URL and domain
            if args.url:
                # User provided explicit base URL
                parsed = urlparse(args.url)
                domain = parsed.netloc
                base_url = args.url
                print(f"   Using explicit base URL: {base_url}")
                
                # Apply domain filter when --url is explicitly set
                urls_before_domain = len(urls)
                urls = [u for u in urls if urlparse(u).netloc == domain]
                
                if not urls:
                    print(f"⚠️  Warning: No URLs remain after domain filtering!")
                    print(f"   Base domain: {domain}")
                    print(f"   URL domains differ - consider adjusting --url\n")
                    return
                
                if urls_before_domain != len(urls):
                    print(f"   Domain filter: {urls_before_domain} → {len(urls)} URLs")
            else:
                # Auto-detect domain from first URL in sitemap
                first_url = urlparse(urls[0])
                domain = first_url.netloc
                base_url = f"{first_url.scheme}://{first_url.netloc}"
                print(f"   Auto-detected base URL: {base_url}")
                print(f"   Note: No domain filtering applied (use --url to filter)")
            
            print(f"   Starting crawl of {len(urls)} URLs...\n")
            
            # Crawl each URL individually
            config = CrawlerRunConfig(
                excluded_selector=args.exclude,
                remove_overlay_elements=True,
            )
            
            async with AsyncWebCrawler() as crawler:
                for i, url in enumerate(urls, 1):
                    try:
                        result = await crawler.arun(url=url, config=config)
                        
                        # arun returns a list, get the first result
                        if isinstance(result, list) and len(result) > 0:
                            result = result[0]
                        
                        if not result.success:
                            print(f"  [{i}/{len(urls)}] ✗ Failed: {url}")
                            failed += 1
                            continue
                        
                        out_path = url_to_filepath(url, base_url, output_dir)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Use fit_markdown if available (more compact for LLMs), else raw markdown
                        content = getattr(result.markdown, "fit_markdown", None) or result.markdown
                        out_path.write_text(str(content), encoding="utf-8")
                        
                        print(f"  [{i}/{len(urls)}] ✓ {url}")
                        print(f"             → {out_path}")
                        saved += 1
                        
                    except Exception as e:
                        print(f"  [{i}/{len(urls)}] ✗ Error: {url}")
                        print(f"             {e}")
                        failed += 1
        
        except Exception as e:
            print(f"❌ Error parsing sitemap file: {e}")
            return
    
    # ─── Sitemap Mode (URL) ──────────────────────────────────────────────────────
    elif args.from_sitemap:
        parsed = urlparse(args.url)
        domain = parsed.netloc
        print(f"🔍 Sitemap Mode: Parsing {args.url}")
        print(f"   Prefix filter: '{args.prefix or '(none)'}' | Output: {output_dir}")
        print(f"   Note: --depth is ignored in sitemap mode\n")
        
        try:
            # Parse sitemap and extract URLs
            urls = await parse_sitemap(args.url)
            
            if not urls:
                print(f"⚠️  Warning: No URLs found in sitemap {args.url}")
                return
            
            print(f"📋 Found {len(urls)} URLs in sitemap")
            
            # Apply prefix filter
            if args.prefix:
                urls_before = len(urls)
                urls = [u for u in urls if urlparse(u).path.startswith(args.prefix)]
                print(f"   Prefix filter: {urls_before} → {len(urls)} URLs\n")
                if not urls:
                    print(f"⚠️  Warning: No URLs match the prefix filter")
                    return
            
            # Apply domain filter
            urls_before_domain = len(urls)
            urls = [u for u in urls if urlparse(u).netloc == domain]
            
            if not urls:
                print(f"⚠️  Warning: No URLs remain after domain filtering!")
                print(f"   Sitemap domain: {domain}")
                print(f"   URL domains differ - consider using the correct sitemap URL\n")
                return
            
            if urls_before_domain != len(urls):
                print(f"   Domain filter: {urls_before_domain} → {len(urls)} URLs")
            
            print(f"   Starting crawl of {len(urls)} URLs...\n")
            
            # Crawl each URL individually
            config = CrawlerRunConfig(
                excluded_selector=args.exclude,
                remove_overlay_elements=True,
                # No deep crawl strategy - just crawl the single URL
            )
            
            async with AsyncWebCrawler() as crawler:
                for i, url in enumerate(urls, 1):
                    try:
                        result = await crawler.arun(url=url, config=config)
                        
                        # arun returns a list, get the first result
                        if isinstance(result, list) and len(result) > 0:
                            result = result[0]
                        
                        if not result.success:
                            print(f"  [{i}/{len(urls)}] ✗ Failed: {url}")
                            failed += 1
                            continue
                        
                        out_path = url_to_filepath(url, args.url, output_dir)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Use fit_markdown if available (more compact for LLMs), else raw markdown
                        content = getattr(result.markdown, "fit_markdown", None) or result.markdown
                        out_path.write_text(str(content), encoding="utf-8")
                        
                        print(f"  [{i}/{len(urls)}] ✓ {url}")
                        print(f"             → {out_path}")
                        saved += 1
                        
                    except Exception as e:
                        print(f"  [{i}/{len(urls)}] ✗ Error: {url}")
                        print(f"             {e}")
                        failed += 1
        
        except Exception as e:
            print(f"❌ Error parsing sitemap: {e}")
            print(f"   Falling back to normal crawl mode...\n")
            args.from_sitemap = False
            # Fall through to normal mode
    
    # ─── Normal Mode ─────────────────────────────────────────────────────────────
    else:
        parsed = urlparse(args.url)
        domain = parsed.netloc
        
        filters = [DomainFilter(allowed_domains=[domain])]
        if args.prefix:
            filters.append(URLPatternFilter(patterns=[f"*{args.prefix}*"]))

        config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=args.depth,
                filter_chain=FilterChain(filters=filters),
            ),
            excluded_selector=args.exclude,
            remove_overlay_elements=True,
        )

        print(f"🔍 Normal Mode: Crawling {args.url}")
        print(f"   Prefix filter: '{args.prefix or '(none)'}' | Depth: {args.depth} | Output: {output_dir}\n")

        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url=args.url, config=config)

            for result in results:
                if not result.success:
                    print(f"  ✗ Failed: {result.url}")
                    failed += 1
                    continue

                out_path = url_to_filepath(result.url, args.url, output_dir)
                out_path.parent.mkdir(parents=True, exist_ok=True)

                # Use fit_markdown if available (more compact for LLMs), else raw markdown
                content = getattr(result.markdown, "fit_markdown", None) or result.markdown
                out_path.write_text(content, encoding="utf-8")

                print(f"  ✓ {result.url}")
                print(f"    → {out_path}")
                saved += 1

    print(f"\n✅ Done: {saved} pages saved, {failed} failed.")

    if args.llms_txt:
        generate_llms_txt(output_dir, args.url)


def main():
    args = parse_args()
    asyncio.run(crawl(args))


if __name__ == "__main__":
    main()