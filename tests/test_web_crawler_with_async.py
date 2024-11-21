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

    @patch('website_crawler.WebsiteCrawler.process_url')
    async def test_scrape_depth(self, mock_process_url):
        # Mock process_url to return a predefined set of links
        crawler = WebsiteCrawler()
        mock_process_url.return_value = ["http://test.com/page1", "http://test.com/page2"]

        start_url = "http://test.com"
        max_depth = 2
        result = await crawler.scrape_depth([start_url], max_depth)

        self.assertIn("http://test.com/page1", result)
        self.assertIn("http://test.com/page2", result)
        self.assertEqual(len(result), 2)  # Ensure the correct number of links is found

    # @patch('website_crawler.WebsiteCrawler.scrape_depth')
    # def test_crawl_website(self, mock_scrape_depth):
    #     # Mock the scrape_depth method to simulate crawling
    #     crawler = WebsiteCrawler()
    #     mock_scrape_depth.return_value = {"http://test.com": ["http://test.com/page1"]}
    #
    #     result = crawler.crawl_website("http://test.com", max_depth=2)
    #
    #     self.assertIn("http://test.com", result)
    #     self.assertIn("http://test.com/page1", result)
    #     self.assertEqual(len(result), 1)  # Only one link should be found in this mock scenario

    @patch('aiohttp.ClientSession.get')
    async def test_fetch_url_throws_exception(self, mock_get):
        # Simulate an exception during fetching the URL
        mock_get.side_effect = aiohttp.ClientError("Connection failed")

        crawler = WebsiteCrawler()
        async with aiohttp.ClientSession() as session:
            result = await crawler.fetch_url(session, "http://test.com")

        self.assertIsNone(result)  # The result should be None if an exception is thrown

    @patch('website_crawler.WebsiteCrawler.fetch_url')
    @patch('website_crawler.WebsiteCrawler.robot_policy_passes')
    @patch('website_crawler.BeautifulSoup')
    async def test_process_url_empty_content(self, mock_bs, mock_robot_policy_passes, mock_fetch_url):
        # Simulate an empty page (no links)
        crawler = WebsiteCrawler()
        mock_fetch_url.return_value = ""
        mock_robot_policy_passes.return_value = True

        base_url = "http://test.com"
        result = await crawler.process_url(mock_fetch_url, "http://test.com", base_url)

        self.assertEqual(result, [])  # No links should be found if the page content is empty

    @patch('website_crawler.WebsiteCrawler.fetch_url')
    @patch('website_crawler.WebsiteCrawler.robot_policy_passes')
    @patch('website_crawler.BeautifulSoup')
    async def test_process_url_no_links(self, mock_bs, mock_robot_policy_passes, mock_fetch_url):
        # Simulate a page with no links
        crawler = WebsiteCrawler()
        mock_fetch_url.return_value = "<html><body>No links here</body></html>"
        mock_robot_policy_passes.return_value = True

        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []
        mock_bs.return_value = mock_soup

        base_url = "http://test.com"
        result = await crawler.process_url(mock_fetch_url, "http://test.com", base_url)

        self.assertEqual(result, [])  # No links should be found

    @patch('web_crawler_with_async.WebsiteCrawler.process_url')
    @patch('aiohttp.ClientSession.get')
    async def test_crawl_website(self, mock_get, mock_process_url):
        # Mock the response from the HTTP request
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html><a href='/test1'>Test</a></html>"
        mock_get.return_value = mock_response

        # Mock process_url to simulate crawling URLs
        mock_process_url.return_value = ['http://test.com/test1']

        # Instantiate the crawler
        crawler = WebsiteCrawler()

        # Call the crawl_website method with the start URL and max depth
        result = await crawler.crawl_website('http://test.com', max_depth=2)

        # Ensure process_url is called with the correct parameters
        mock_process_url.assert_called_with(mock_get, 'http://test.com', 'http://test.com')

        # Verify that the result contains the correct URLs
        self.assertIn('http://test.com/test1', result['http://test.com'])

        # Verify that the mock was called with the expected arguments
        self.assertEqual(mock_process_url.call_count, 1)  # Ensures it's called only once for the depth level


if __name__ == "__main__":
    unittest.main()
