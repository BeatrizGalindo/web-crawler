import os
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
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
        }
        form {
            background: #ffffff;
            padding: 20px;
            margin: 20px auto;
            max-width: 500px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            background-color: #45a049;
        }
        h2 {
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background: #ffffff;
            margin: 5px 0;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .message {
            color: red;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Web Crawler</h1>
    <form method="post" action="/">
        <label for="url">Enter a URL to crawl:</label>
        <input type="text" id="url" name="url" placeholder="https://example.com" required>
        <button type="submit">Start Crawling</button>
    </form>
    <h2>Crawled URLs:</h2>
    {% if message %}
    <p class="message">{{ message }}</p>
    {% endif %}
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
    message = None
    if request.method == "POST":
        start_url = request.form.get("url")  # Get the URL from the form input
        if start_url:
            try:
                # Call your crawl_website function
                crawled_urls = crawl_website(start_url, max_depth=2, max_workers=5)
                if not crawled_urls:
                    message = "No URLs found :("
            except Exception as e:
                logging.error(f"Error during crawling: {e}")
                message = "An error occurred during crawling"

    return render_template_string(HTML_TEMPLATE, crawled_urls=crawled_urls, message=message)


if __name__ == "__main__":
    # Use Render's dynamic port or default to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
