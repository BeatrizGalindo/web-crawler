# Web Crawler

A simple Python-based web crawler that starts from a given URL, crawls the website up to a specified depth, and collects all unique URLs found during the crawl. The crawler uses multi-threading to fetch URLs concurrently and respects `robots.txt` rules.

## Features
- Crawls a website up to a specified depth.
- Uses multi-threading for concurrent URL fetching.
- Handles exceptions gracefully to avoid stopping the program.
- Respects `robots.txt` crawling rules to ensure ethical crawling.
- Supports configurable depth and number of concurrent workers.

## Requirements
- Python 3.13+
- Libraries: `requests`, `beautifulsoup4`, `lxml`

To install the required dependencies, you can use `pip`:

```bash
pip install -r requirements.txt
