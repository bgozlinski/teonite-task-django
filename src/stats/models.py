from django.db import models
from django.template.defaultfilters import slugify

class Author(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name).replace("-", "")
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    content = models.TextField()
    authors = models.ManyToManyField(Author, related_name='articles')

    def __str__(self):
        return self.title

class WordCount(models.Model):
    word = models.CharField(max_length=255, db_index=True)
    count = models.PositiveIntegerField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="word_count")

    def __str__(self):
        return f"{self.word}: {self.count}"

    class Meta:
        unique_together = ('word', 'article')
