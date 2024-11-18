import logging
import time
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

def fetch_url(session, url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Ensure HTTP errors are raised
        return response.text
    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
        return None

def crawl_website(start_url, max_depth=3):
    queue = deque([(start_url, 0)])
    visited = set()
    list_of_all_monzo_links = set()

    robots_url = urljoin(start_url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        logging.warning(f"Could not read robots.txt: {e}")
        rp = None  # Disable robots.txt compliance if it fails

    session = requests.Session()  # Reuse connections
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust the number of threads as needed
        while queue:
            url, depth = queue.popleft()
            if url in visited or (rp and not rp.can_fetch("*", url)) or depth >= max_depth:
                continue

            page_content = fetch_url(session, url)
            if page_content:
                soup = BeautifulSoup(page_content, "lxml")  # Faster parser
                visited.add(url)

                all_links = soup.find_all("a", href=True)
                for link in all_links:
                    href = link["href"]
                    absolute_link = urljoin(url, href)

                    if urlparse(absolute_link).netloc == urlparse(start_url).netloc and absolute_link not in visited and absolute_link not in list_of_all_monzo_links:
                        queue.append((absolute_link, depth + 1))
                        list_of_all_monzo_links.add(absolute_link)

    return list_of_all_monzo_links

if __name__ == "__main__":
    start_url = "https://monzo.com/"
    links = crawl_website(start_url)
    print(f"Found {len(links)} links:")
    for link in links:
        print(link)
