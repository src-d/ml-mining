import scrapy


class CppStdlibSpider(scrapy.Spider):
    """Spider for scraping the C/C++ standard libraries."""

    name = "cpp-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        url = "https://en.cppreference.com/w/%s/header"
        for lang in ["c", "cpp"]:
            request = scrapy.Request(url % lang, callback=self._parse)
            request.meta["lang"] = lang
            yield request

    def _parse(self, response):
        """Parse the response for the index."""
        lang = response.meta["lang"]
        if lang == "c":
            default_since = "since C89/90"
        else:
            default_since = "since C++95"
        for block in response.css("tr.t-dsc > td"):
            library_name = block.css("b::text").get()
            if library_name is None and lang == "cpp":
                library_name = block.css("tt::text").get()
            if not library_name:
                continue
            since = default_since
            library_metadata = []
            for i in block.css("span::text").getall():
                i = i.strip("()")
                if i.startswith("since"):
                    since = i
                else:
                    library_metadata.append(i)
            library_metadata.append(since)
            yield {
                "library_name": library_name.strip("<>"),
                "lang": lang,
                "library_metadata": library_metadata,
            }
