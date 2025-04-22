from django.contrib import admin
from .models import Movie10days
from .models import Movie

class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'release_date', 'total_revenue', 'total_moviegoers_num')
    search_fields = ['movie_name']

admin.site.register(Movie, MovieAdmin)

class Movie10daysAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'days_since_release', 'moviegoers_num', 'moviegoers_cumulative', 'revenue', 'revenue_cumulative')
    search_fields = ['movie_name']

admin.site.register(Movie10days, Movie10daysAdmin)