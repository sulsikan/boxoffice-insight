from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('daily_boxoffice/', views.daily_boxoffice, name='daily_boxoffice'),

]
