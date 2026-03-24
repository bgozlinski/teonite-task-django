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

    def clean_author_names(self, name: str):
        if name.startswith("By ") or name.startswith("Authors: "):
            name = name.replace("By ", "").replace("Authors: ", "").strip()

        names  = [n.strip() for n in name.split(", ")]

        valid = [n for n in names if len(n.split(" ")) <= 3]

        return valid if valid else ["Unknown Author"]

    def clean_content(self, content: str):
        medium_noise = [
            "Listen Share",
            "Join Medium for free to get updates from\xa0this\xa0writer.",
            "Join Medium for free to get updates from this writer.",
            "Remember me for faster sign in",
            "Follow",
        ]
        for phrase in medium_noise:
            content = content.replace(phrase, "")

        content = re.sub(r'\s+', ' ', content).strip()

        return content

    def process_item(self, item, spider):
        author_names = self.clean_author_names(item['author_name'])
        if author_names:
            clean_text = self.clean_content(item['content'])

            article, _ = Article.objects.update_or_create(
                url=item['url'],
                defaults={
                    'title': item['title'],
                    'content': clean_text,
                }
            )

            article.authors.clear()
            for name in author_names:
                author, _ = Author.objects.get_or_create(name=name)
                article.authors.add(author)

            text = clean_text.lower()
            text = re.sub(r'[^\w\s]', '', text)
            words = text.split()
            words = [w for w in words if w not in self.stop_words and w.isalpha() and len(w) > 2]
            word_counts = Counter(words)

            for word, count in word_counts.items():
                WordCount.objects.update_or_create(
                    word=word, article=article,
                    defaults={'count': count}
                )

        return item
