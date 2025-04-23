from django.urls import path
from . import views

urlpatterns = [
    path('regional_boxoffice/', views.regional_boxoffice, name='regional_boxoffice'),
    ]