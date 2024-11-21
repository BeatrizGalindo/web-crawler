import time

from flask import Flask, request, render_template
from web_crawler_with_async import WebsiteCrawler  # Assuming the above code is in a file named crawler.py
import os
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        depth = int(request.form.get('depth', 2))  # Default depth to 2 if not provided

        # Create an instance of WebsiteCrawler
        crawler = WebsiteCrawler()

        # Use the crawl_website method to start the crawling process
        crawled_links = crawler.crawl_website(url, depth)

        # Build a result string to show all found links
        results = []
        for key, value in crawled_links.items():
            links_html = "<ul>" + "".join(
                f"<li><a href='{link}' target='_blank'>{link}</a></li>" for link in value) + "</ul>"
            results.append(
                f"<h3>For <a href='{key}' target='_blank'>{key}</a>, we found {len(value)} links:</h3>{links_html}")

        # Join all results with line breaks
        result = "".join(results)

        return render_template('index.html', result=result)

    return render_template('index.html', result=None)


if __name__ == '__main__':
    # Use Render's dynamic port or default to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
