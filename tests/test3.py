import unittest
from unittest.mock import patch, MagicMock

import requests

from web_crawler3 import crawl_website, fetch_url  # Replace 'web_crawler3' with the correct module name if needed


class TestWebCrawler(unittest.TestCase):

    @patch('requests.Session.get')  # Mock the requests.get call
    def test_fetch_url_success(self, mock_get):
        # Mock the response object
        mock_response = MagicMock()
        mock_response.text = "<html><a href='/page1'>Link</a></html>"
        mock_response.raise_for_status = MagicMock()  # Mock raise_for_status to do nothing
        mock_get.return_value = mock_response

        session = requests.Session()
        url = "https://monzo.com/"
        result = fetch_url(session, url)

        # Ensure fetch_url returns the correct HTML content
        self.assertEqual(result, "<html><a href='/page1'>Link</a></html>")
        mock_get.assert_called_once_with(url, timeout=10)

    @patch('requests.Session.get')  # Mock the requests.get call
    def test_fetch_url_failure(self, mock_get):
        # Simulate an exception when making the request
        mock_get.side_effect = requests.exceptions.RequestException("Error processing URL")

        session = requests.Session()
        url = "https://monzo.com/"
        result = fetch_url(session, url)

        # Ensure fetch_url handles the exception and returns None
        self.assertIsNone(result)
        mock_get.assert_called_once_with(url, timeout=10)



    @patch('requests.Session.get')  # Mock the requests.get call
    @patch('bs4.BeautifulSoup.find_all')  # Mock BeautifulSoup.find_all
    @patch('urllib.robotparser.RobotFileParser.can_fetch')  # Mock robots.txt compliance
    def test_crawl_website_with_robots_txt_restrictions(self, mock_can_fetch, mock_find_all, mock_get):
        # Mock robots.txt to disallow crawling
        mock_can_fetch.return_value = False

        # Set up the queue and visited sets for crawl_website
        start_url = "https://monzo.com/"
        max_depth = 2

        result = crawl_website(start_url, max_depth)

        # Ensure no URLs are visited when robots.txt disallows crawling
        self.assertEqual(len(result), 0)


    @patch('requests.Session.get')  # Mock requests.get for crawl_website
    @patch('bs4.BeautifulSoup.find_all')  # Mock BeautifulSoup.find_all
    @patch('urllib.robotparser.RobotFileParser.can_fetch')  # Mock robots.txt compliance
    def test_crawl_website(self, mock_can_fetch, mock_find_all, mock_get):
        # Mock can_fetch to allow crawling
        mock_can_fetch.return_value = True

        # Mock the response from the first URL
        mock_response = MagicMock()
        mock_response.text = "<html><a href='/page1'>Link</a><a href='/page2'>Link</a></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock find_all to return links in the mock HTML content
        mock_find_all.return_value = [
            MagicMock(href="/page1"),
            MagicMock(href="/page2")
        ]

        # Set up the queue and visited sets for crawl_website
        start_url = "https://monzo.com/"
        max_depth = 2

        result = crawl_website(start_url, max_depth)

        # Ensure the mock functions were called correctly
        mock_get.assert_called_once_with(start_url, timeout=10)
        mock_find_all.assert_called_once_with("a", href=True)

        # Check that the result contains the links we mocked
        self.assertIn("https://monzo.com/page1", result)
        self.assertIn("https://monzo.com/page2", result)

    @patch('requests.Session.get')  # Mock the requests.get call
    @patch('bs4.BeautifulSoup.find_all')  # Mock BeautifulSoup.find_all
    @patch('urllib.robotparser.RobotFileParser.can_fetch')  # Mock robots.txt compliance
    def test_crawl_website_with_max_depth(self, mock_can_fetch, mock_find_all, mock_get):
        # Mock robots.txt to allow crawling
        mock_can_fetch.return_value = True

        # Mock the response from the first URL
        mock_response = MagicMock()
        mock_response.text = "<html><a href='/page1'>Link</a></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock find_all to return links in the mock HTML content
        mock_find_all.return_value = [
            MagicMock(href="/page1"),
            MagicMock(href="/page2")
        ]

        # Set up the queue and visited sets for crawl_website
        start_url = "https://monzo.com/"
        max_depth = 1

        result = crawl_website(start_url, max_depth)

        # Check that the result contains the links we mocked
        self.assertEqual(len(result), 1)  # Only one link should be added since max_depth is 1
        self.assertIn("https://monzo.com/page1", result)
        self.assertNotIn("https://monzo.com/page2", result)


if __name__ == '__main__':
    unittest.main()
