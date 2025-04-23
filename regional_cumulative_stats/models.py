from django.db import models

class RegionalCumulativeStats(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    region = models.CharField(max_length=50, verbose_name="지역")
    screens = models.IntegerField(verbose_name="스크린수")
    revenue_total = models.BigIntegerField(verbose_name="누적매출액(원)")
    revenue_share = models.FloatField(verbose_name="매출점유율(%)")
    audience_total = models.BigIntegerField(verbose_name="누적관객수(명)")
    audience_share = models.FloatField(verbose_name="관객점유율(%)")

    class Meta:
        verbose_name = "지역별 누적통계"
        verbose_name_plural = "지역별 누적통계"

    def __str__(self):
        return f"{self.title} - {self.region}"
