import unittest
from unittest.mock import patch, MagicMock

import aiohttp

from web_crawler_with_async import WebsiteCrawler


class TestWebsiteCrawler(unittest.TestCase):

    @patch('aiohttp.ClientSession.get')
    async def test_fetch_url_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text.return_value = "Test Content"
        mock_get.return_value = mock_response

        crawler = WebsiteCrawler()
        async with aiohttp.ClientSession() as session:
            result = await crawler.fetch_url(session, "http://test.com")

        self.assertEqual(result, "Test Content")

    @patch('aiohttp.ClientSession.get')
    async def test_fetch_url_failure(self, mock_get):
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status = 404
        mock_get.return_value = mock_response

        crawler = WebsiteCrawler()
        async with aiohttp.ClientSession() as session:
            result = await crawler.fetch_url(session, "http://test.com")

        self.assertIsNone(result)

    @patch('urllib.robotparser.RobotFileParser.read')
    @patch('urllib.robotparser.RobotFileParser.set_url')
    async def test_robot_policy_passes(self, mock_set_url, mock_read):
        # Mock robots.txt reading to pass
        mock_set_url.return_value = None
        mock_read.return_value = None

        crawler = WebsiteCrawler()
        result = await crawler.robot_policy_passes("http://test.com")

        self.assertTrue(result)

    @patch('urllib.robotparser.RobotFileParser.read')
    @patch('urllib.robotparser.RobotFileParser.set_url')
    async def test_robot_policy_fails(self, mock_set_url, mock_read):
        # Simulate an exception to simulate robots.txt failure
        mock_set_url.return_value = None
        mock_read.side_effect = Exception("Error reading robots.txt")

        crawler = WebsiteCrawler()
        result = await crawler.robot_policy_passes("http://test.com")

        self.assertFalse(result)

    def test_is_same_domain(self):
        crawler = WebsiteCrawler()

        # Same domain
        base_url = "http://test.com"
        link = "http://test.com/page"
        result = crawler.is_same_domain(base_url, link)
        self.assertTrue(result)

        # Different domain
        link = "http://other.com/page"
        result = crawler.is_same_domain(base_url, link)
        self.assertFalse(result)


    @patch('website_crawler.WebsiteCrawler.fetch_url')
    @patch('website_crawler.WebsiteCrawler.robot_policy_passes')
    @patch('website_crawler.BeautifulSoup')
    async def test_process_url(self, mock_bs, mock_robot_policy_passes, mock_fetch_url):
        # Mocking BeautifulSoup and fetch_url
        crawler = WebsiteCrawler()
        mock_fetch_url.return_value = "<html><a href='/test1'>Test</a><a href='tel:+123'>Call</a></html>"
        mock_robot_policy_passes.return_value = True

        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [MagicMock(get=lambda x: '/test1')]
        mock_bs.return_value = mock_soup

        base_url = "http://test.com"
        result = await crawler.process_url(mock_fetch_url, "http://test.com", base_url)

        self.assertIn("http://test.com/test1", result)
        self.assertNotIn("tel:+123", result)  # "tel:" links should be excluded


if __name__ == "__main__":
    unittest.main()
