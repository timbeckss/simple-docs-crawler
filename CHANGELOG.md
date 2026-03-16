# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-16

### Added
- **Local Sitemap File Feature**: New `--sitemap-file` option to parse local `.xml` sitemap files
  - Supports both standard sitemaps and sitemap index files
  - Automatic domain detection from URLs in sitemap (when `--url` not set)
  - Domain filtering only applied when `--url` is explicitly provided
  - Sub-sitemaps in index files are automatically fetched via HTTP
- New internal function `_parse_sitemap_xml()` for shared XML parsing logic
- New function `parse_sitemap_file()` for local sitemap processing
- Validation: `--sitemap-file` and `--from-sitemap` are mutually exclusive
- Three crawl modes now available: Normal, Sitemap-URL, Sitemap-File

### Changed
- Refactored: Extracted XML parsing logic from `parse_sitemap()` for better code reusability
- Improved error handling in sitemap modes
- Updated CLI help and documentation
- Base URL can now be explicitly set or automatically detected
- Flexible domain filtering depending on crawl mode

[0.1.0]: https://github.com/username/crawl4ai-project/releases/tag/v0.1.0
