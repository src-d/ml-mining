from io import BytesIO
import json
from zipfile import ZipFile

import scrapy


class JavaStdlibSpider(scrapy.Spider):
    """Spider for scraping the Java standard libraries."""

    name = "java-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        url = "https://docs.oracle.com/javase/%d/docs/api/overview-summary.html"
        for version in [6, 7, 8]:
            request = scrapy.Request(url % version, callback=self._parse_css)
            request.meta["version"] = str(version)
            if version == 6:
                request.meta["css"] = "tr.TableRowColor > td > b > a::text"
            else:
                request.meta["css"] = "tr.altColor > td > a::text"
            yield request
        url = "https://docs.oracle.com/javase/%d/docs/api/module-search-index.zip"
        for version in [9, 10]:
            request = scrapy.Request(url % version, callback=self._parse_zip)
            request.meta["version"] = str(version)
            yield request

    def _parse_css(self, response):
        """Parse the response for the index."""
        library_metadata = [response.meta["version"]]
        for library_name in response.css(response.meta["css"]).getall():
            yield {
                "library_name": library_name,
                "lang": "java",
                "library_metadata": library_metadata,
            }

    def _parse_zip(self, response):
        """Parse the response for each package."""
        library_metadata = [response.meta["version"]]
        content = json.loads(
            ZipFile(BytesIO(response.body))
            .read("module-search-index.json")
            .decode(encoding="utf-8")
        )
        for d in content:
            yield {
                "library_name": d["l"],
                "lang": "java",
                "library_metadata": library_metadata,
            }
