import scrapy


class ArticleItem(scrapy.Item):
    """Empty Container for Scrapy Data, works as dictionary with key-value pairs"""
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    author_name = scrapy.Field()
