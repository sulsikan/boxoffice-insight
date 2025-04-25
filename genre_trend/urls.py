from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('genre_cumulative_stats/', views.genre_cumulative_stats, name='genre_cumulative_stats'),
    path('genre_yearly_trends/', views.genre_yearly_trends, name='genre_yearly_trends'),
]