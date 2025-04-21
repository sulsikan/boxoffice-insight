from django.db import models

class Movie10days(models.Model):
    movie_name = models.CharField(max_length=255)
    days_since_release = models.CharField(max_length=50)
    screen_num = models.IntegerField()
    screenings_num = models.IntegerField()
    revenue = models.IntegerField()
    moviegoers_num = models.IntegerField()
    revenue_cumulative = models.IntegerField()
    moviegoers_cumulative = models.IntegerField()
    rank = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.movie_name}_개봉 경과 : {self.days_since_release}'