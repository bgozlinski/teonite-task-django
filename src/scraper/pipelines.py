import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

import django
django.setup()

from stats.models import Author, Article, WordCount
from nltk.corpus import stopwords
from collections import Counter
import re

class ArticlePipeline:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_author_name(self, raw_name: str):
        new_name = raw_name
        if raw_name.startswith("By ") or raw_name.startswith("Authors: "):
            new_name = raw_name.replace("By ", "").replace("Authors: ", "").strip()
        new_name = new_name.split(", ")[0]
        if len(new_name.split(" ")) > 3:
            return "Unknown Author"

        return new_name

    def process_item(self, item, spider):
        author_name = self.clean_author_name(item['author_name'])
        if author_name:
            author, _ = Author.objects.get_or_create(name=author_name)
            article, _ = Article.objects.update_or_create(
                url=item['url'],
                defaults={
                    'title': item['title'],
                    'content': item['content'],
                    'author': author,
                }

            )

            text = item['content'].lower()
            text = re.sub(r'[^\w\s]', '', text)
            words = text.split()
            words = [w for w in words if w not in self.stop_words and w.isalpha() and len(w) > 2]

            word_counts = Counter(words)

            for word, count in word_counts.items():
                WordCount.objects.update_or_create(
                    word=word,
                    article=article,
                    defaults={'count': count}
                )

        return item
