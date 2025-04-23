from django.urls import path
from . import views

urlpatterns = [
    path('international-visualization/', views.international_visualization_view, name='international_boxoffice_visualization'),
    path('api/boxoffice/', views.get_boxoffice_data, name='boxoffice_data'),
    path('api/countries/', views.get_countries, name='available_countries'),
    path('api/date-range/', views.get_date_range, name='date_range'),
    path('api/movie-revenue/', views.get_movie_revenue_data, name='get_movie_revenue_data'),
    path('movie-international-visualization/', views.movie_international_visualization_view, name='movie_international_visualization'),
    path('genre-analysis/', views.genre_analysis_view, name='genre_analysis'),
    path('api/genre-analysis/', views.get_genre_analysis_data, name='get_genre_analysis_data'),
    path('genre-stat/', views.genre_stat_view, name='genre_stat'),
] 