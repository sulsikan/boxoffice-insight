from django.urls import path
from . import views

app_name = 'korean_boxoffice'
urlpatterns = [
    path('', views.daily_boxoffice, name='index'),
    path('daily_boxoffice/', views.daily_boxoffice, name='daily_boxoffice'),
    path('<int:pk>/', views.movie_info, name='movie_info'),

]
