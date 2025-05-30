"""
URL configuration for boxoffice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('international-visualization/', TemplateView.as_view(template_name='international_boxoffice/international-visualization.html'), name='international_boxoffice_visualization'),
    path('international_boxoffice/', include('international_boxoffice.urls')),
    path('korean_boxoffice/', include('korean_boxoffice.urls')),
    path("genre/", include('genre_trend.urls')),
    path('regional_cumulative_stats/', include('regional_cumulative_stats.urls')),
    path('regional_boxoffice/', include('regional_boxoffice.urls')),
    path('movie_performance_summary/', include('movie_performance_summary.urls')),
]
