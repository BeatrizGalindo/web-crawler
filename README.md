# Web Crawler

A simple Python-based web crawler that starts from a given URL, crawls the website up to a specified depth, and collects all unique URLs found during the crawl. The crawler uses multi-threading to fetch URLs concurrently and respects `robots.txt` rules.

## Features
- Crawls a website up to a specified depth.
- Uses multi-threading for concurrent URL fetching.
- Handles exceptions to avoid stopping the program.
- Respects `robots.txt` crawling rules to ensure ethical crawling.
- Supports configurable depth and number of concurrent workers.
- Outputs visited URLs and links found on each page

## Requirements
- Python 3.13+
- Libraries: `requests`, `beautifulsoup4`, `lxml`

To install the required dependencies, you can use `pip`:

```bash
pip install -r requirements.txt
```

### Run the app
Use the following command to run the app on your terminal. 
```bash
python app.py 
```

You can find this app uploaded to Render.com

## Testing
Unit tests are provided to validate the functionality of the crawler. Run the tests using the following command and you'll also be able to see the coverage of the tests:
```bash
coverage run -m unittest tests.web_crawler_test.TestWebCrawler
coverage report
```



## DESIGN CHOICES / TRADE OFF

#### **1. Structure and Modularity**

The code is split into reusable functions (`fetch_url`, `crawl_website`) and a dedicated test suite. This modularity makes the program easier to understand, maintain, and extend.
- **Trade-off**: There is limited separation of concerns. For example, `crawl_website` handles fetching, parsing, queue management, and domain validation. Splitting these into separate classes or modules (e.g., `QueueManager`, `DomainFilter`) could improve testability and maintainability.

#### **2. Concurrency**

The use of `ThreadPoolExecutor` enables concurrent crawling, improving performance when fetching multiple pages.
- **Trade-off**: Threads are limited by Python's Global Interpreter Lock (GIL). For a high-performance crawler, using `asyncio` for asynchronous I/O might be more efficient. However, the current approach is simpler to implement and sufficient for small-scale crawling.


#### **4. Error Handling**

The program includes robust error handling for HTTP requests using `try`/`except`, ensuring that failed requests don't crash the program.
- **Trade-off**: Some errors (e.g., transient network issues) might be recoverable. Implementing retry logic for specific exceptions could make the crawler more reliable.

#### **5. Robots.txt Compliance**

The crawler respects robots.txt using `RobotFileParser`, adhering to best practices for web scraping.
- **Potential Improvement**: Robots.txt rules are fetched and parsed synchronously, adding latency. This could be pre-fetched or cached if crawling the same domain repeatedly.

#### **8. Parsing**

 BeautifulSoup is used for HTML parsing, which is reliable and easy to use.
- **Potential Improvement**: Handling non-HTML content (e.g., PDFs, JSON APIs) could extend the crawler's versatility.

#### **9. Test Coverage**

 The test suite covers key functionality, including edge cases like robots.txt compliance and invalid URLs.
- **Potential Improvement**: Add tests for concurrency (e.g., ensuring thread safety) and edge cases like circular links.

## FUTURE WORK

**Politeness Policy**: Introduce delay between requests to avoid overloading servers.
**Data Export**: Enable saving results to files in formats like JSON or CSV.
**Testing Coverage**: Expand test cases to cover more scenarios.