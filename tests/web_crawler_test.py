import unittest
from unittest.mock import patch, MagicMock

import requests

from web_crawler import fetch_url, crawl_website

class TestWebCrawler(unittest.TestCase):
    def setUp(self):
        """Set up common variables or mocks for tests."""
        self.mock_session = MagicMock()
        self.valid_url = "https://example.com"
        self.invalid_url = "https://nonexistent.example.com"
        self.page_content = "<html><body><a href='/link1'>Link 1</a></body></html>"

    def test_fetch_url_success(self):
        """Test if fetch_url successfully fetches content for a valid URL."""
        self.mock_session.get.return_value = MagicMock(
            status_code=200, text=self.page_content, raise_for_status=MagicMock()
        )
        result = fetch_url(self.mock_session, self.valid_url)
        self.assertEqual(result, self.page_content)

    def test_fetch_url_failure(self):
        """Test if fetch_url returns None for an invalid URL."""
        self.mock_session.get.side_effect = requests.exceptions.RequestException
        result = fetch_url(self.mock_session, self.invalid_url)
        self.assertIsNone(result)

    @patch("web_crawler.requests.Session")
    def test_crawl_website_basic(self, mock_session):
        """Test if crawl_website processes a basic site with one link."""
        mock_session.return_value.get.return_value = MagicMock(
            status_code=200, text=self.page_content, raise_for_status=MagicMock()
        )

        result = crawl_website("https://example.com", max_depth=2, max_workers=2)
        self.assertIn("https://example.com", result)  # Root URL should be visited
        self.assertIn("https://example.com/link1", result)  # Link from the page should be visited

    @patch("web_crawler.requests.Session")
    def test_crawl_website_max_depth(self, mock_session):
        """Test if crawl_website respects the maximum depth limit."""
        mock_session.return_value.get.return_value = MagicMock(
            status_code=200, text=self.page_content, raise_for_status=MagicMock()
        )

        result = crawl_website("https://example.com", max_depth=0, max_workers=2)
        self.assertEqual(len(result), 0)  # No links should be visited if max_depth is 0

    @patch("web_crawler.requests.Session")
    def test_crawl_website_robotstxt(self, mock_session):
        """Test if crawl_website respects robots.txt rules."""
        # Simulate a disallow rule in robots.txt
        with patch("web_crawler.RobotFileParser") as mock_robots:
            mock_robots.return_value.can_fetch.return_value = False
            mock_session.return_value.get.return_value = MagicMock(
                status_code=200, text=self.page_content, raise_for_status=MagicMock()
            )

            result = crawl_website("https://example.com", max_depth=2, max_workers=2)
            self.assertNotIn("https://example.com", result)  # Root URL shouldn't be crawled

    def tearDown(self):
        """Clean up after tests if necessary."""
        pass

if __name__ == "__main__":
    unittest.main()
