import json
import time
import scrapy
import re
from w3lib.html import remove_tags
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


def comment_processor(value):
    if value is not None:
        #re.sub('<[^>]*>', '', value)
        value = value.replace(u'\u2192','')
        value = value.replace(u'\u200e','')
        value = value.lstrip('(')
        value = value.rstrip(')')
        return value


def size_processor(value):
    if value is not None:
        value = value.lstrip('(')
        value = value.rstrip(')')
        return value


# Item processors
class RevisionItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    comment_in = MapCompose(remove_tags,comment_processor)
    comment_out = TakeFirst()
    size_in = MapCompose(size_processor)


# Revision item
class RevisionItem(scrapy.Item):
    comment = scrapy.Field()
    date = scrapy.Field()
    ip = scrapy.Field()
    user = scrapy.Field()
    size = scrapy.Field()
    tags = scrapy.Field()
    extracted_date = scrapy.Field()


# Pipelines
# Export items to file
class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('revision.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)

        return item


class RevisionSpider(scrapy.Spider):
    name = "revision"

    allowed_domains = ["mediawiki.org", "wikipedia.org", "wikimedia.org"]

    custom_settings = {
        'ITEM_PIPELINES': {
                'wiki.pipelines.WikiPipeline': 300,
                'wiki.pipelines.JsonWriterPipeline': 800,
            },
        'BOT_NAME': 'wiki-history-extractor',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3
    }


    def parse(self, response):

        # Extract current revisions
        for revision in response.css('ul#pagehistory li'):

            loader = RevisionItemLoader(RevisionItem(), selector=revision, response=response)

            loader.add_css('comment', 'span.comment')
            loader.add_css('date', 'a.mw-changeslist-date::text')
            loader.add_css('ip', 'a.mw-anonuserlink bdi::text')
            loader.add_css('user', 'a.mw-userlink bdi::text')
            loader.add_css('size', 'span.history-size::text')
            loader.add_css('tags', 'span.mw-tag-marker::text')
            loader.add_value('extracted_date', time.strftime("%c"))

            yield loader.load_item()

        # Get next revision history page
        next_page = response.css('a.mw-nextlink::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            # Be kind and treat wikimedia with care
            # time.sleep(1)
            yield scrapy.Request(next_page, callback=self.parse)


class RevisionCrawler(object):

    def __init__(self,urls=[]):
        self.urls = urls

    def start(self):
        process = CrawlerProcess({
            'USER_AGENT': 'wiki-history-extractor'
        })

        process.crawl(RevisionSpider,start_urls=self.urls)
        process.start()
