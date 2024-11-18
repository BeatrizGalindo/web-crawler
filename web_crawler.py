import logging
import re
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO)

def crawl_website(start_url):
    """Crawl all links on the same domain as the start URL."""
    queue = deque([start_url])
    visited = set()
    list_of_all_monzo_links = set()

    # Parse robots.txt
    robots_url = urljoin(start_url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        logging.warning(f"Could not read robots.txt: {e}")
        rp = None  # Disable robots.txt compliance if it fails

    while queue:
        url = queue.popleft()

        # Skip visited or disallowed URLs
        if url in visited or (rp and not rp.can_fetch("*", url)):
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Ensure HTTP errors are raised
            soup = BeautifulSoup(response.text, "html.parser")

            logging.info(f"Visiting: {url}")
            visited.add(url)  # Mark as visited

            # Extract and process links
            all_links = soup.find_all("a", attrs={"href": re.compile("^https?://.*")})
            for link in all_links:
                href = link["href"]
                absolute_link = urljoin(url, href)

                if urlparse(absolute_link).netloc == urlparse(start_url).netloc:
                    if absolute_link not in visited:
                        queue.append(absolute_link)
                        list_of_all_monzo_links.add(absolute_link)

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

    return list_of_all_monzo_links

if __name__ == "__main__":
    start_url = "https://monzo.com/"
    links = crawl_website(start_url)
    print(f"Found {len(links)} links:")
    for link in links:
        print(link)
