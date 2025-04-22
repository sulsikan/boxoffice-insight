from django.contrib import admin

from .models import MovieInfo, DailyBoxoffice
# Register your models here.
admin.site.register(MovieInfo)
admin.site.register(DailyBoxoffice)