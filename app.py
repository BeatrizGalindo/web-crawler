import os
from flask import Flask, request, render_template
import logging
from web_crawler import crawl_website

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    crawled_links = {}
    num_visited = 0
    message = None
    loading_message = None
    if request.method == "POST":
        start_url = request.form.get("url")
        if start_url:
            try:
                loading_message = "We are fetching the links, please wait a moment..."

                # Call crawl_website and get detailed results
                crawled_links = crawl_website(start_url, max_depth=2, max_workers=5)
                num_visited = sum(len(links) for links in crawled_links.values())
                if not crawled_links:
                    message = "No URLs found :("
            except Exception as e:
                logging.error(f"Error during crawling: {e}")
                message = "An error occurred during crawling"

    return render_template('index.html', crawled_links=crawled_links, message=message, num_visited=num_visited, loading_message=loading_message)

if __name__ == "__main__":
    # Use Render's dynamic port or default to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
