from django.contrib import admin
from .models import MovieBasicInfo
from .models import MovieDetail

@admin.register(MovieBasicInfo)
class MovieBasicInfoAdming(admin.ModelAdmin):
    list_display = ('movie_name', 'release_date', 'genre', 'country','is_now_showing')
    search_fields = ('movie_name',)
    list_filter = ('genre', 'release_date')

@admin.register(MovieDetail)
class MovieDetail(admin.ModelAdmin):
    list_display = ('genre', 'movie_name', 'release_date', 'sales','audience','screen')
    search_fields = ('movie_name',)
    list_filter = ('genre', 'release_date')