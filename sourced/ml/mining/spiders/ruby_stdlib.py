from pathlib import Path

import scrapy


class RubyStdlibSpider(scrapy.Spider):
    """Spider for scraping the Ruby standard libraries."""

    name = "ruby-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        url = "https://ruby-doc.org"
        yield scrapy.Request(url, callback=self._parse_index)

    def _parse_index(self, response):
        """Parse the response for the index."""
        root = Path("/")
        for href in response.css(
            "ul#stdlib-api-list > li > span > a::attr(href)"
        ).getall():
            url = response.url + (root / href / "toc.html").as_posix()
            yield scrapy.Request(url, callback=self._parse)

    def _parse(self, response):
        """Parse the response for each package."""
        version = response.url.split("/")[-2].split("-")[1]
        library_metadata = [version]
        for library_name in response.css("a.mature::text").getall():
            yield {
                "library_name": library_name,
                "lang": "ruby",
                "library_metadata": library_metadata,
            }
