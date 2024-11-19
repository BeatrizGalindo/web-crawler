import unittest
from unittest.mock import patch, Mock
from urllib.parse import urljoin

import requests

from web_crawler3 import crawl_website


class TestCrawlWebsite(unittest.TestCase):

    @patch("web_crawler.requests.get")
    @patch("web_crawler.RobotFileParser")
    def test_crawl_website(self, mock_robot_parser, mock_get):
        # Mock robots.txt behavior
        mock_robot_parser_instance = Mock()
        mock_robot_parser.return_value = mock_robot_parser_instance
        mock_robot_parser_instance.can_fetch.return_value = True

        # Mock responses for the main page
        base_url = "https://example.com/"
        page_html = """
        <html>
            <body>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="https://otherdomain.com/">Other Domain</a>
            </body>
        </html>
        """
        mock_get.return_value = Mock(status_code=200, text=page_html)

        # Call the function
        links = crawl_website(base_url)

        # Validate results
        expected_links = {
            urljoin(base_url, "/about"),
            urljoin(base_url, "/contact"),
        }
        print(f"Mocked page HTML: {mock_get.return_value.text}")
        print(f"Extracted links: {links}")
        print(f"Extracted links length: {len(links)}")
        print(f"this are the expected links: {expected_links}")
        print(f"Extracted links length: {len(expected_links)}")
        self.assertEqual(links, expected_links)

        # Verify robots.txt interactions
        mock_robot_parser_instance.set_url.assert_called_once_with(urljoin(base_url, "/robots.txt"))
        mock_robot_parser_instance.read.assert_called_once()

        # Verify HTTP requests
        mock_get.assert_any_call(base_url, timeout=10)
        self.assertEqual(mock_get.call_count, 3)  # Only one request made due to local links

    @patch("web_crawler.requests.get")
    @patch("web_crawler.RobotFileParser")
    def test_crawl_website_robots_disallow(self, mock_robot_parser, mock_get):
        # Mock robots.txt behavior
        mock_robot_parser_instance = Mock()
        mock_robot_parser.return_value = mock_robot_parser_instance
        mock_robot_parser_instance.can_fetch.return_value = False  # Disallow crawling

        # Mock responses for the main page
        base_url = "https://example.com/"
        mock_get.return_value = Mock(status_code=200, text="")

        # Call the function
        links = crawl_website(base_url)

        # Validate results (empty because crawling was disallowed)
        self.assertEqual(links, set())

        # Verify robots.txt interactions
        mock_robot_parser_instance.set_url.assert_called_once_with(urljoin(base_url, "/robots.txt"))
        mock_robot_parser_instance.read.assert_called_once()

    @patch("web_crawler.requests.get")
    @patch("web_crawler.RobotFileParser")
    def test_crawl_website_http_error(self, mock_robot_parser, mock_get):
        # Mock robots.txt behavior
        mock_robot_parser_instance = Mock()
        mock_robot_parser.return_value = mock_robot_parser_instance
        mock_robot_parser_instance.can_fetch.return_value = True

        # Mock a failed HTTP request
        base_url = "https://example.com/"
        mock_get.side_effect = requests.exceptions.RequestException("HTTP error")

        # Call the function
        links = crawl_website(base_url)

        # Validate results (empty because of an HTTP error)
        self.assertEqual(links, set())

        # Verify HTTP requests
        mock_get.assert_called_once_with(base_url, timeout=10)

if __name__ == "__main__":
    unittest.main()
