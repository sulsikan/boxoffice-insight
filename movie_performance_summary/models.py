from django.db import models

class Movie(models.Model):
    # 영화 흥행 성적 비교용으로 만든 모델
    rank = models.IntegerField(null=True, verbose_name='순위')
    movie_name = models.CharField(max_length=255, verbose_name='영화 제목')
    release_date = models.DateField(null=True, verbose_name='개봉일')
    total_revenue = models.IntegerField(null=True, verbose_name='매출액')
    total_moviegoers_num = models.IntegerField(null=True, verbose_name='관객수')

    def __str__(self):
        return f'{self.movie_name}'
    
    
class Movie10days(models.Model):
    movie_name = models.CharField(max_length=255, verbose_name='영화 제목')
    # movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    days_since_release = models.CharField(max_length=50, verbose_name='개봉 경과')
    screen_num = models.IntegerField()
    screenings_num = models.IntegerField()
    revenue = models.IntegerField(verbose_name='일일 수익')
    moviegoers_num = models.IntegerField(verbose_name='일일 관객 수')
    revenue_cumulative = models.IntegerField(verbose_name='누적 수익')  
    moviegoers_cumulative = models.IntegerField(verbose_name='누적 관객 수')
    rank = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.movie_name}_개봉 경과 : {self.days_since_release}'