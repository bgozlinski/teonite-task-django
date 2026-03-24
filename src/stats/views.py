from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Sum
from stats.models import WordCount
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from stats.models import Author


class StatsView(APIView):
    def get(self, request):
        top_words = WordCount.objects.values('word').annotate(total=Sum('count')).order_by('-total')[:10]
        result = {item['word']: item['total'] for item in top_words}

        return Response(result)


class AuthorStatsView(APIView):
    def get(self, request, slug):
        author = get_object_or_404(Author, slug=slug)

        top_words = (WordCount.objects
        .filter(article__authors=author)
        .values('word')
        .annotate(total=Sum('count'))
        .order_by('-total')[:10])

        result = {item['word']: item['total'] for item in top_words}
        return Response(result)


class AuthorsListView(APIView):
    def get(self, request):
        authors = Author.objects.all()
        result = {author.slug: author.name for author in authors}
        return Response(result)