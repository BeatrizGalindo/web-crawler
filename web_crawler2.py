import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

start_url = "https://monzo.com/"
visited = set()
list_of_all_monzo_links = []
queue = deque([start_url])
lock = Lock()

def crawl_page(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text,'html.parser')
        all_links = soup.find_all('a', attrs={'href': re.compile("^https?://.*")})

        found_links = []

        for link in all_links:
            href = link["href"]
            absolute_link = urljoin(url, href)  # Handle relative links
            if urlparse(absolute_link).netloc == urlparse(start_url).netloc:
                with lock:
                    queue.append(absolute_link)
                    if absolute_link not in visited:
                        visited.add(absolute_link)
                        found_links.append(absolute_link)
                        list_of_all_monzo_links.append(absolute_link)
        return found_links

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return []


def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        while queue or any(future.running() for future in futures):
            if queue:
                url = queue.popleft()

            with lock:
                if url not in visited:
                    visited.add(url)
                    futures.append(executor.submit(crawl_page, url))


        for future in futures:
            if future.done():
                futures.remove(future)
                for link in future.result():
                    queue.append(link)

if __name__ == "__main__":
    main()
    print(f"Found {len(list_of_all_monzo_links)} links:")
    for link in list_of_all_monzo_links:
        print(link)



