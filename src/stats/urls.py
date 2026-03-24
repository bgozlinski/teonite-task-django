from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.StatsView.as_view(), name='global-stats'),
    path('stats/<slug:slug>/', views.AuthorStatsView.as_view(), name='author-stats'),
    path('authors/', views.AuthorsListView.as_view(), name='authors-list'),
]