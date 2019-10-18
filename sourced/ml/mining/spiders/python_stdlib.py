import zlib

import scrapy


class PythonStdlibSpider(scrapy.Spider):
    """Spider for scraping the Python standard libraries."""

    name = "python-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        url = "http://docs.python.org/%.1f/objects.inv"
        for v in [2.6, 3.0, 3.1]:
            request = scrapy.Request(url % v, callback=self._parse_old_sphinx)
            request.meta["version"] = str(v)
            yield request
        for v in [2.7, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8]:
            request = scrapy.Request(url % v, callback=self._parse_new_sphinx)
            request.meta["version"] = str(v)
            yield request

    def _parse_old_sphinx(self, response):
        """Parse the response for old sphinx docs."""
        content = response.body.decode(encoding="utf-8")
        library_metadata = [response.meta["version"]]
        for line in content.splitlines():
            line = line.split()
            if line[1] == "mod":
                yield {
                    "library_name": line[0],
                    "lang": "python",
                    "library_metadata": library_metadata,
                }

    def _parse_new_sphinx(self, response):
        """Parse the response for new sphinx docs."""
        body = response.body
        for start in range(len(body)):
            try:
                content = zlib.decompress(body[start:])
                break
            except zlib.error:
                pass
        library_metadata = [response.meta["version"]]
        for line in content.decode(encoding="utf-8").splitlines()[2:]:
            line = line.split()
            if line[1] == "py:module":
                yield {
                    "library_name": line[0],
                    "lang": "python",
                    "library_metadata": library_metadata,
                }
