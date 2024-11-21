import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from web_crawler_with_async import WebsiteCrawler  # Adjust this import as needed


@pytest.fixture
def website_crawler():
    return WebsiteCrawler()


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_fetch_url_success(mock_get, website_crawler):
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<html><a href='/test1'>Test</a></html>")  # Mock async method
    mock_get.return_value.__aenter__.return_value = mock_response  # __aenter__ needed for async mocking

    # Use an actual aiohttp.ClientSession in the test
    async with aiohttp.ClientSession() as session:
        result = await website_crawler.fetch_url(session, "http://test.com")

    # Ensure the result is the expected content
    assert result == "<html><a href='/test1'>Test</a></html>"


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_fetch_url_failure(mock_get, website_crawler):
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status = 404
    mock_get.return_value = mock_response

    async with aiohttp.ClientSession() as session:
        result = await website_crawler.fetch_url(session, "http://test.com")

    assert result is None


@pytest.mark.asyncio
@patch('urllib.robotparser.RobotFileParser.can_fetch')
@patch('urllib.robotparser.RobotFileParser.read')
@patch('urllib.robotparser.RobotFileParser.set_url')
async def test_robot_policy_passes(mock_set_url, mock_read, mock_can_fetch, website_crawler):
    # Mock robots.txt behavior
    mock_set_url.return_value = None
    mock_read.return_value = None
    mock_can_fetch.return_value = True  # Simulate that robots.txt allows the URL

    result = await website_crawler.robot_policy_passes("http://test.com")

    assert result is True


@pytest.mark.asyncio
@patch('urllib.robotparser.RobotFileParser.read')
@patch('urllib.robotparser.RobotFileParser.set_url')
async def test_robot_policy_fails(mock_set_url, mock_read, website_crawler):
    # Simulate an exception to simulate robots.txt failure
    mock_set_url.return_value = None
    mock_read.side_effect = Exception("Error reading robots.txt")

    result = await website_crawler.robot_policy_passes("http://test.com")

    assert result is False


def test_is_same_domain():
    crawler = WebsiteCrawler()

    # Same domain
    base_url = "http://test.com"
    link = "http://test.com/page"
    result = crawler.is_same_domain(base_url, link)
    assert result is True

    # Different domain
    link = "http://other.com/page"
    result = crawler.is_same_domain(base_url, link)
    assert result is False


@pytest.mark.asyncio
async def test_process_url(website_crawler):
    # Mock the methods
    website_crawler.visited = set()

    # Mock fetching the HTML
    mock_page = "<html><a href='/link1'>Link 1</a><a href='tel:+123'>Call</a></html>"
    with patch.object(website_crawler, "fetch_url", return_value=mock_page), \
            patch.object(website_crawler, "robot_policy_passes", return_value=True), \
            patch.object(website_crawler, "is_same_domain", return_value=True):
        result = await website_crawler.process_url(AsyncMock(), "http://example.com", "http://example.com")

    # Assert that the valid link was processed
    assert "http://example.com/link1" in result
    # Assert that 'tel:' links were excluded
    assert "tel:+123" not in result  # "tel:" links should be excluded


@pytest.mark.asyncio
async def test_scrape_depth(website_crawler):
    # Mock method calls to simulate a typical crawl
    mock_page = "<html><a href='/link1'>Link 1</a><a href='/link2'>Link 2</a></html>"

    with patch.object(website_crawler, "fetch_url", return_value=mock_page), \
         patch.object(website_crawler, "robot_policy_passes", return_value=True), \
         patch.object(website_crawler, "is_same_domain", return_value=True):
        result = await website_crawler.scrape_depth(["http://example.com"], max_depth=1)

    # Assert scrape_depth correctly collected base_url as one of the urls
    assert 'http://example.com' in result
    # Assert scrape_depth correctly identified the 2 links
    assert 'http://example.com/link1' in result['http://example.com']
    assert 'http://example.com/link2' in result['http://example.com']
