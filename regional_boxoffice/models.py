from django.db import models

class RegionalBoxOffice(models.Model):
    지역 = models.CharField(max_length=5)
    
    한국_상영편수 = models.IntegerField()
    한국_매출액 = models.BigIntegerField()
    한국_관객수 = models.IntegerField()
    한국_점유율 = models.FloatField()

    외국_상영편수 = models.IntegerField()
    외국_매출액 = models.BigIntegerField()
    외국_관객수 = models.IntegerField()
    외국_점유율 = models.FloatField()

    전체_상영편수 = models.IntegerField()
    전체_매출액 = models.BigIntegerField()
    전체_관객수 = models.IntegerField()
    전체_점유율 = models.FloatField()

    기준_시작일 = models.DateField()
    기준_종료일 = models.DateField()

    class Meta:
        verbose_name = "지역별 점유율"
        verbose_name_plural = "지역별 점유율"

    def __str__(self):
        return f"{self.지역} ({self.기준_시작일} ~ {self.기준_종료일})"