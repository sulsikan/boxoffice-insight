from django.db import models

#영화 기본 정보
class MovieBasicInfo(models.Model):
    movie_name = models.CharField(max_length=255, verbose_name="영화명") # 영화명
    release_date = models.CharField(max_length=20, verbose_name="개봉일") # 개봉일
    genre = models.CharField(max_length=100, verbose_name="장르") # 장르
    is_now_showing = models.BooleanField(default=False, verbose_name="현재 상영 여부") # 현재 상영 여부
    country= models.CharField(max_length=30, verbose_name="국가") # 국가


# 영화 누적관객 수 및 시각화
class MovieDetail(models.Model):
    rank = models.IntegerField(verbose_name="연도별 순위")
    movie_name = models.CharField(max_length=255, verbose_name="영화명")
    release_date = models.CharField(max_length=20, verbose_name="개봉일")
    sales = models.CharField(max_length=30, verbose_name="누적판매액")
    audience = models.CharField(max_length=30, verbose_name="누적관객수")
    screen = models.CharField(max_length=20, verbose_name="스크린수")
    genre = models.CharField(max_length=100, verbose_name="장르")