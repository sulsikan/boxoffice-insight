from django.urls import path
from . import views

urlpatterns = [
    path('international-visualization/', views.international_visualization_view, name='international_boxoffice_visualization'),
    path('api/boxoffice/', views.get_boxoffice_data, name='boxoffice_data'),
    path('api/countries/', views.get_countries, name='available_countries'),
    path('api/date-range/', views.get_date_range, name='date_range'),
] 