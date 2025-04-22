from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('genre_stat/',views.genre_stat, name='genre_stat'),
]