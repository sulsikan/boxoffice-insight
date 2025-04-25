from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_performance_summary, name='movie_performance_summary'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),  # 영화 상세 페이지 URL
    path('movie_performance_comparison/', views.movie_performance_comparison, name='movie_performance_comparison'),  # 영화 성과 비교 페이지
]