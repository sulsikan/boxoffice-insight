from django.urls import path
from . import views

urlpatterns = [
    path('regional_cumulative/', views.regional_cumulative, name='regional_cumulative'),
    path('api/movie_stats/', views.get_movie_stats, name='movie_stats'),
    path('api/top_movies_by_region/', views.get_top_movies_by_region, name='top_movies_by_region'),
]