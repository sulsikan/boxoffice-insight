from django.urls import path
from . import views

urlpatterns = [
    path('regional_cumulative/', views.regional_cumulative, name='regional_cumulative')
    ]