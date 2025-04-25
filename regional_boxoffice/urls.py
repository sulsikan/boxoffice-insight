from django.urls import path
from . import views

urlpatterns = [
    path('regional_boxoffice/', views.regional_boxoffice, name='regional_boxoffice'),
    path('get_trend_data/', views.get_trend_data, name='get_trend_data'),
]