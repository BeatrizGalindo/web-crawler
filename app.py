import asyncio

import requests
from flask import Flask, request, render_template, jsonify

from website_crawler import WebsiteCrawler
import os
app = Flask(__name__)

# Global error handler for timeouts
@app.errorhandler(asyncio.TimeoutError)
def handle_timeout_error(error):
    return render_template('index.html', result="<h3>Oops, there has been an error with the timeout. Please try again by refreshing the page.</h3>")

# Global error handler for request exceptions
@app.errorhandler(requests.exceptions.RequestException)
def handle_request_exception(error):
    return render_template('index.html', result="<h3>There was an issue with the website's accessibility. Please ensure the URL is correct and try again.</h3>")

# Global error handler for any other exception
@app.errorhandler(Exception)
def handle_generic_error(error):
    return render_template('index.html', result=f"<h3>An unexpected error occurred: {str(error)}</h3>")

# Web interface route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        depth = int(request.form.get('depth', 2))  # Default depth to 2 if not provided

        # Create an instance of WebsiteCrawler
        crawler = WebsiteCrawler()

        # Use the crawl_website method to start the crawling process
        crawled_links = crawler.crawl_website(url, depth)

        # If no links are found, display a specific message
        if not crawled_links:
            result = "<h3>No links were found because the page blocked our request or denied us access :(</h3>"
        else:
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


# API route
@app.route('/api/crawl', methods=['POST'])
def api_crawler():
    try:
        data = request.get_json()
        url = data.get('url')
        depth = int(data.get('depth', 2))
        crawler = WebsiteCrawler()
        crawled_links = crawler.crawl_website(url, depth)

        # Convert any sets in crawled_links to lists to make them JSON serializable
        crawled_links_serializable = {
            key: list(value) if isinstance(value, set) else value
            for key, value in crawled_links.items()
        }

        if not crawled_links_serializable:
            return jsonify({"message": "No links were found. The page might have blocked or denied access."}), 200

        return jsonify({"url": url, "depth": depth, "links": crawled_links_serializable}), 200
    except ValueError:
        return jsonify({"error": "Invalid depth value. It must be an integer."}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Use Render's dynamic port or default to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
