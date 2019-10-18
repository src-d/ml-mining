import json

import scrapy


class CSharpStdlibSpider(scrapy.Spider):
    """Spider for scraping the C# standard libraries."""

    name = "csharp-stdlib-spider"

    def start_requests(self):
        """Start making requests."""
        url = "https://docs.microsoft.com/_api/familyTrees/byPlatform/dotnet"
        yield scrapy.Request(url, callback=self._parse_index)

    def _parse_index(self, response):
        """Parse the response for the index."""
        index = json.loads(response.text)
        url = "https://docs.microsoft.com/api/apibrowser/dotnet/namespaces?moniker=%s"
        for family in index:
            family_name = family["familyName"]
            for product in family["products"]:
                product_name = product["productName"]
                for package in product["packages"]:
                    version = package["versionDisplayName"]
                    moniker = package["monikerName"]
                    request = scrapy.Request(url % moniker, callback=self._parse)
                    request.meta["family"] = family_name
                    request.meta["product"] = product_name
                    request.meta["version"] = version
                    yield request

    def _parse(self, response):
        """Parse the response for each package."""
        content = json.loads(response.text)
        library_metadata = [
            response.meta["family"],
            response.meta["product"],
            response.meta["version"],
        ]
        for c in content["namespaces"]:
            yield {
                "library_name": c["displayName"],
                "lang": "csharp",
                "library_metadata": library_metadata,
            }
