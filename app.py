import logging
from web_crawler import crawl_website

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    start_url = input("Enter the URL to start crawling (e.g., https://example.com/): ").strip()

    if not start_url:
        logging.error("No URL provided. Exiting...")
    else:
        # Perform the crawl and collect all discovered links
        links = crawl_website(start_url)
        logging.info(f"Found {len(links)} links:")
        for link in links:
            print(link)
