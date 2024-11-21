import logging
import asyncio
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse, quote
import aiohttp
from bs4 import BeautifulSoup

class WebsiteCrawler:
    def __init__(self):
        self.visited = set()
        self.found_links = {}

    async def fetch_url(self, session, url):
        """
        Fetches the content of a URL using the provided async HTTP session.
        Handles exceptions to ensure errors do not stop the program.
        """
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}: HTTP {response.status}")
        except aiohttp.ClientError as e:
            print(f"Failed to fetch {url}: {e}")
        return None

    async def robot_policy_passes(self, start_url):
        """
        Checks if robots.txt policy allows access to the start_url.
        """
        robots_url = urljoin(start_url, "/robots.txt")
        rp = RobotFileParser()

        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception as e:
            logging.warning(f"Can't read robots file {robots_url}: {e}")
            return False  # Assume compliance failed if parsing errors occur.

        return rp.can_fetch("*", start_url)

    def is_same_domain(self, base_url, link):
        """
        Checks if a link belongs to the same domain as the base URL.
        """
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        return base_domain == link_domain or link_domain == ""

    async def process_url(self, session, url, base_url):
        """
        Processes a single URL: fetches the content, parses it, and extracts links.
        """
        if url in self.visited:
            return []

        page_content = await self.fetch_url(session, url)
        if not page_content:
            return []

        if not await self.robot_policy_passes(url):
            return []

        soup = BeautifulSoup(page_content, "lxml")
        self.visited.add(url)  # Mark the URL as visited

        # Extract and normalize links
        all_links = soup.find_all("a", href=True)
        links_on_page = set() # do not duplicate same link found on website multiple times
        for link in all_links:
            href = link.get('href')
            if href:  # Check if 'href' exists
                # Exclude 'tel:' links
                if href.startswith('tel:'):
                    continue
                # Exclude 'mailto:' links
                if href.startswith('mailto:'):
                    continue

                # Encode the href and resolve to an absolute URL
                absolute_link = urljoin(url, quote(href, safe=':/#?=&'))

                # Check if the link is in the same domain
                if self.is_same_domain(base_url, absolute_link):
                    # Strip fragment identifiers and add the cleaned link
                    clean_link = urlparse(absolute_link)._replace(fragment='').geturl()
                    links_on_page.add(clean_link)

        self.found_links[url] = links_on_page
        return links_on_page

    async def scrape_depth(self, base_urls, max_depth):
        """
        Scrapes a set of URLs up to a specified depth.
        """
        async with aiohttp.ClientSession() as session:
            current_level = base_urls
            for depth in range(max_depth):
                print(f"Processing depth {depth}...")
                tasks = [self.process_url(session, url, base_urls[0]) for url in current_level]
                results = await asyncio.gather(*tasks)

                # Flatten results and remove already visited URLs
                next_level = set(link for links in results for link in links if link not in self.visited)
                current_level = next_level  # Prepare for the next depth
        return self.found_links

    def crawl_website(self, start_url, max_depth=2):
        """Function to crawl website with user-defined start URL and depth."""
        self.visited.clear()  # Clear visited and found_links before each crawl
        self.found_links.clear()

        return asyncio.run(self.scrape_depth([start_url], max_depth))


