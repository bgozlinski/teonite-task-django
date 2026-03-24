from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os


class Command(BaseCommand):
    help = "Scrape Netflix Tech Blog articles"

    def handle(self, *args, **options):
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.settings")

        process = CrawlerProcess(get_project_settings())
        process.crawl("blog")
        process.start()
        self.stdout.write(self.style.SUCCESS("Scraping completed successfully"))