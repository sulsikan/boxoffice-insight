from django.urls import path
from . import views

app_name = 'korean_boxoffice'
urlpatterns = [
    path('', views.index, name='index'),
    path('daily_boxoffice/<int:target_date>', views.daily_boxoffice, name='daily_boxoffice'), #YYYYMMDD

]
