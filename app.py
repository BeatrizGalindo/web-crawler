from flask import Flask, request, render_template_string
import logging

from web_crawler import crawl_website

app = Flask(__name__)

# Basic HTML template with a text box and submit button
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Crawler</title>
</head>
<body>
    <h1>Enter the URL to Start Crawling</h1>
    <form method="post" action="/">
        <label for="url">Start URL:</label>
        <input type="text" id="url" name="url" placeholder="https://example.com" required>
        <button type="submit">Start Crawling</button>
    </form>
    <h2>Crawled URLs</h2>
    <ul>
        {% for url in crawled_urls %}
        <li>{{ url }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    crawled_urls = []
    if request.method == "POST":
        start_url = request.form.get("url")  # Get the URL from the form input
        if start_url:
            try:
                # Call your crawl_website function
                crawled_urls = crawl_website(start_url, max_depth=2, max_workers=5)
            except Exception as e:
                logging.error(f"Error during crawling: {e}")

    return render_template_string(HTML_TEMPLATE, crawled_urls=crawled_urls)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
