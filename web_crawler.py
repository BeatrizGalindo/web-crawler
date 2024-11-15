import re
from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

start_url = "https://monzo.com/"
queue = deque([start_url])
visited = set()
list_of_all_monzo_links = []

while queue:
    url = queue.popleft()
    if url not in visited:
        page_to_scrape = requests.get(url, timeout=10)
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        all_links = soup.find_all("a", attrs={"href": re.compile("^https?://.*")})

        # print(f"Visiting: {url}")
        # print(f"Found {len(all_links)} total links")

        for link in all_links:
            href = link["href"]
            absolute_link = urljoin(url, href)  # Handle relative links
            if urlparse(absolute_link).netloc == urlparse(start_url).netloc:
                if absolute_link not in visited:
                    queue.append(absolute_link)
                    list_of_all_monzo_links.append(absolute_link)
        # print(f"Queue size: {len(queue)}")
        # print("-----")

        visited.add(url)

print(list_of_all_monzo_links)