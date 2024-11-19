import logging
import time
from collections import deque
from urllib.parse import urljoin, urlparse, quote
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor


def fetch_url(session, url):
    """
    Fetches the content of a URL using the provided HTTP session.
    Handles exceptions to ensure errors do not stop the program.
    """
    try:
        response = session.get(url, timeout=10)  # Fetch the URL with a 10-second timeout
        response.raise_for_status()  # Raise an error for HTTP errors like 404
        return response.text  # Return the response content as text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
    return None  # Return None if an error occurs


def crawl_website(start_url, max_depth=2, max_workers=10):
    """
    Crawls a website starting from the given URL, up to a specified depth.
    Uses multi-threading to fetch URLs concurrently.

    Args:
        start_url (str): The URL to start crawling from.
        max_depth (int): The maximum depth to crawl (default: 2).
        max_workers (int): The number of threads to use for concurrent crawling (default: 5).

    Returns:
        set: A set of unique URLs discovered during the crawl.
    """
    start_time = time.time()  # Start a timer to measure the crawling time
    logging.info(f"Starting crawl with {max_workers} workers and max depth {max_depth}...")

    queue = deque([(start_url, 0)])  # Queue for URLs to crawl, starting with the root URL at depth 0
    visited = set()  # Set to track visited URLs to avoid re-crawling

    # Parse and read robots.txt to respect crawling rules
    robots_url = urljoin(start_url, "/robots.txt")
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)  # Set the robots.txt URL
        rp.read()  # Read and parse the file
    except Exception as e:
        logging.warning(f"Could not read robots.txt at {robots_url}: {e}")
        rp = None  # Disable robots.txt compliance if parsing fails

    # Create a session for reusing HTTP connections
    session = requests.Session()
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:  # Thread pool for parallel crawling
            while queue:
                url, depth = queue.popleft()  # Get the next URL and its depth from the queue
                if depth >= max_depth:  # Skip if the maximum depth is reached
                    logging.info(f"Reached max depth for URL: {url}")
                    continue
                if url in visited:  # Skip if the URL has already been crawled
                    logging.debug(f"Skipping already visited URL: {url}")
                    continue
                if rp and not rp.can_fetch("*", url):  # Check robots.txt rules
                    logging.info(f"Blocked by robots.txt: {url}")
                    continue

                logging.info(f"Crawling URL: {url} at depth {depth}")
                # Fetch the page content
                page_content = fetch_url(session, url)
                if not page_content:  # Skip if fetching fails
                    continue

                # Parse the page content with BeautifulSoup
                soup = BeautifulSoup(page_content, "lxml")
                visited.add(url)  # Mark the URL as visited

                # Find all hyperlinks on the page
                all_links = soup.find_all("a", href=True)
                for link in all_links:
                    href = link["href"]
                    try:
                        # Encode and resolve the URL to an absolute link
                        encoded_href = quote(href, safe=':/#?=&')
                        absolute_link = urljoin(url, encoded_href)

                        # Ensure the link belongs to the same domain and hasn't been visited
                        parsed_start = urlparse(start_url)
                        parsed_link = urlparse(absolute_link)
                        if (parsed_link.netloc == parsed_start.netloc and
                                absolute_link not in visited):
                            queue.append((absolute_link, depth + 1))  # Add the link to the queue for crawling
                    except Exception as e:
                        logging.warning(f"Error processing link {href} on {url}: {e}")
    finally:
        session.close()  # Close the session after crawling completes

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    logging.info(f"Crawl completed in {elapsed_time:.2f} seconds.")  # Log the total time taken

    return visited  # Return the set of visited URLs

