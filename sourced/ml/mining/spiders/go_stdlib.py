import scrapy


class GoStdlibSpider(scrapy.Spider):
    """Spider for scraping the Go standard libraries."""

    name = "go-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        for url, kind in [
            ("https://godoc.org/-/go", "core"),
            ("https://godoc.org/-/subrepo", "subrepo"),
        ]:
            request = scrapy.Request(url, callback=self._parse)
            request.meta["kind"] = kind
            yield request

    def _parse(self, response):
        """Parse the response for the index."""
        library_metadata = [response.meta["kind"]]
        for library_name in response.css("td > a::attr(href)").getall():
            yield {
                "library_name": library_name.strip("/"),
                "lang": "go",
                "library_metadata": library_metadata,
            }
