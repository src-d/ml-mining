import argparse
import logging

from scrapy.crawler import CrawlerProcess

from sourced.ml.mining.models import StandardLibraries
from sourced.ml.mining.spiders import (
    CppStdlibSpider,
    CSharpStdlibSpider,
    GoStdlibSpider,
    JavaStdlibSpider,
    PythonStdlibSpider,
    RubyStdlibSpider,
)
from sourced.ml.mining.utils import check_remove_filepath, path_with_suffix


class StdlibPipeline(object):
    """Item pipeline that holds data in memory then saves it as a StandardLibraries model."""

    library_names = {}
    library_metadata = {}
    pending_spiders = 0

    def __init__(self, output_path):
        """Create the item pipeline."""
        self.output_path = output_path

    @classmethod
    def from_crawler(cls, crawler):
        """Pass the output path to the constructor when instantiating from the crawler."""
        return cls(output_path=crawler.settings["OUTPUT_PATH"])

    def open_spider(self, spider):
        """Open a spider."""
        type(self).pending_spiders += 1
        log = logging.getLogger(spider.name)
        log.info("Opened spider, pending: %d", self.pending_spiders)

    def close_spider(self, spider):
        """Close a spider, and save the model if it is the last to terminate."""
        log = logging.getLogger(spider.name)
        type(self).pending_spiders -= 1
        log.info("Closed spider, pending: %d", self.pending_spiders)
        if self.pending_spiders == 0:
            log.info("No more spiders are running, creating the model ...")
            StandardLibraries(log_level=logging.INFO).construct(
                self.library_names, self.library_metadata
            ).save(self.output_path, series="stdlib")
            log.info("Saved model to %s", self.output_path)

    def process_item(self, item, spider):
        """Process an item returned by one of the spiders."""
        lang, library_name = item["lang"], item["library_name"]
        if lang not in self.library_names:
            self.library_names[lang] = set()
            self.library_metadata[lang] = {}
        self.library_names[lang].add(library_name)
        for meta in item["library_metadata"]:
            if meta not in self.library_metadata[lang]:
                self.library_metadata[lang][meta] = set()
            self.library_metadata[lang][meta].add(library_name)


def collect_stdlibs(args: argparse.Namespace):
    """
    Collect the lists of standard library_names for each language Babelfish can parse.
    """
    log = logging.getLogger("collect_stdlibs")
    output_path = path_with_suffix(args.output_path, ".asdf")
    check_remove_filepath(output_path, log, args.force)
    process = CrawlerProcess(
        settings={
            "BOT_NAME": "vegeta",
            "ITEM_PIPELINES": {
                "sourced.ml.mining.cmd.collect_stdlibs.StdlibPipeline": 100
            },
            "LOG_ENABLED": 0,
            "OUTPUT_PATH": output_path,
        }
    )
    logging.getLogger("scrapy").setLevel(logging.WARNING)

    for spider in [
        CppStdlibSpider,
        CSharpStdlibSpider,
        GoStdlibSpider,
        JavaStdlibSpider,
        PythonStdlibSpider,
        RubyStdlibSpider,
    ]:
        process.crawl(spider)
    process.start()
    process.stop()
