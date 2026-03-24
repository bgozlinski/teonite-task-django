BOT_NAME = 'scraper'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 0.5

ITEM_PIPELINES = {
    'scraper.pipelines.ArticlePipeline': 300,
}