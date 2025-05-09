from django.db import models


class MovieInfo(models.Model):
    # 박스오피스내 영화정보를 담는 테스트용 모델
    # id 자동생성
    movie_id = models.IntegerField(unique=True, blank=False, null=True)  # 중복입력방지용
    movie_name = models.CharField(max_length=255)
    release_date = models.DateTimeField(null=True)
    genre = models.CharField(max_length=255, null=True)
    is_now_showing = models.BooleanField(default=False)
    nation = models.CharField(max_length=255, null=True)
    movie_img = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f'{self.movie_name}-{self.genre}'


# Create your models here.
class DailyBoxoffice(models.Model):
    # id 자동생성
    movie_id = models.ForeignKey(MovieInfo, related_name='daily_boxoffices', on_delete=models.CASCADE, null=True)
    ranking_date_rank = models.CharField(unique=True, max_length=255, blank=False, null=False)  # 중복입력방지용
    ranking_date = models.DateTimeField()
    rank = models.IntegerField()
    movie_name = models.CharField(max_length=255)
    revenue = models.IntegerField()
    release_date = models.DateTimeField(null=True)
    revenue_share = models.FloatField()
    revenue_fluctuation = models.IntegerField()
    revenue_cumulative = models.IntegerField()
    moviegoers_num = models.IntegerField()
    moviegoers_fluctuation = models.IntegerField()
    moviegoers_cumulative = models.IntegerField()
    screens_num = models.IntegerField()
    screenings_num = models.IntegerField()

    def __str__(self):
        return f'{self.ranking_date}-{self.rank}-{self.movie_name}-{self.revenue}'


class MonthlyBoxoffice(models.Model):
    # id 자동생성
    movie_id = models.ForeignKey(MovieInfo, related_name='monthly_boxoffices', on_delete=models.CASCADE, null=True)
    ranking_date_rank = models.CharField(unique=True, max_length=255, blank=False, null=False)  # 중복입력방지용
    ranking_date = models.CharField()
    rank = models.IntegerField()
    movie_name = models.CharField(max_length=255)
    revenue = models.IntegerField()
    release_date = models.DateTimeField(null=True)
    revenue_share = models.FloatField()
    revenue_cumulative = models.IntegerField()
    moviegoers_num = models.IntegerField()
    moviegoers_cumulative = models.IntegerField()
    screens_num = models.IntegerField()
    screenings_num = models.IntegerField()

    def __str__(self):
        return f'{self.ranking_date}-{self.rank}-{self.movie_name}-{self.revenue}'


class AnnualBoxoffice(models.Model):
    # id 자동생성
    movie_id = models.ForeignKey(MovieInfo, related_name='annual_boxoffices', on_delete=models.CASCADE, null=True)
    ranking_date_rank = models.CharField(unique=True, max_length=255, blank=False, null=False)  # 중복입력방지용
    ranking_date = models.CharField()
    rank = models.IntegerField()
    movie_name = models.CharField(max_length=255)
    revenue = models.IntegerField()
    release_date = models.DateTimeField(null=True)
    revenue_share = models.FloatField()
    moviegoers_num = models.IntegerField()
    screens_num = models.IntegerField()
    screenings_num = models.IntegerField()

    def __str__(self):
        return f'{self.ranking_date}-{self.rank}-{self.movie_name}-{self.revenue}'