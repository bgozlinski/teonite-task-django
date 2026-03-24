import scrapy
from scrapy import Selector
from scrapy.http import Request, Response
from scraper.items import ArticleItem

class BlogSpider(scrapy.Spider):
    name = "blog"
    start_urls = ["https://netflixtechblog.com/feed"]

    def parse(self, response: Response):
        sel = Selector(response, type='xml')
        sel.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')
        for item in sel.css('item'):
            link = item.css('link::text').get()
            if link:
                yield response.follow(link, callback=self.parse_article)

    def parse_article(self, response: Response):
        yield ArticleItem(
            title=(response.css('title::text').get() or '').split('|')[0].strip(),
            url=response.url,
            author_name=response.css('meta[property="og:description"]::attr(content)').get(),
            content=' '.join(response.css('article p::text').getall()),
        )

