from django.test import TestCase
from scraper.pipelines import ArticlePipeline
from rest_framework.test import APITestCase
from stats.models import Author, Article, WordCount


class CleanAuthorNameTest(TestCase):
    def setUp(self):
        self.pipeline = ArticlePipeline()

    def test_removes_by_prefix(self):
        self.assertEqual(self.pipeline.clean_author_names("By Harshad Sane"), ["Harshad Sane"])

    def test_takes_first_author(self):
        self.assertIn("Valentin Geffrier", self.pipeline.clean_author_names("Valentin Geffrier, Tanguy Cornuau"))
        self.assertIn("Tanguy Cornuau", self.pipeline.clean_author_names("Valentin Geffrier, Tanguy Cornuau"))

    def test_no_author(self):
        self.assertEqual(self.pipeline.clean_author_names("From Structured Queries to Natural Language"), ["Unknown Author"])

class AuthorSlugTest(TestCase):
    def test_slug_no_hyphens(self):
        author = Author(name="Kamil Chudy")
        author.save()
        self.assertEqual(author.slug, "kamilchudy")


class StatsAPITest(APITestCase):
    def setUp(self):
        author = Author.objects.create(name="Test Author")
        article = Article.objects.create(
            title="Test Article",
            url="https://example.com/test",
            content="test content",
        )
        article.authors.add(author)  # ← M2M
        WordCount.objects.create(word="python", count=10, article=article)
        WordCount.objects.create(word="django", count=5, article=article)

    def test_global_stats_returns_200(self):
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, 200)

    def test_global_stats_format(self):
        response = self.client.get('/stats/')
        data = response.json()
        self.assertIn('python', data)
        self.assertEqual(data['python'], 10)

    def test_author_stats_returns_200(self):
        response = self.client.get('/stats/testauthor/')
        self.assertEqual(response.status_code, 200)

    def test_author_stats_404_for_unknown(self):
        response = self.client.get('/stats/nieistniejacy/')
        self.assertEqual(response.status_code, 404)

    def test_authors_list(self):
        response = self.client.get('/authors/')
        data = response.json()
        self.assertIn('testauthor', data)
        self.assertEqual(data['testauthor'], 'Test Author')
