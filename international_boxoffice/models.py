from django.db import models

class InternationalBoxOffice(models.Model):
    """해외 박스오피스 데이터 모델"""
    
    COUNTRY_CHOICES = [
        ('US', '미국'),
        ('UK', '영국'),
        ('DE', '독일'),
        ('JP', '일본'),
    ]
    
    CURRENCY_CHOICES = [
        ('$', 'USD'),
        ('£', 'GBP'),
        ('€', 'EUR'),
        ('¥', 'JPY'),
    ]
    
    rank = models.IntegerField(verbose_name='순위')
    title = models.CharField(max_length=255, verbose_name='영화제목')
    release_date = models.DateField(verbose_name='개봉일')
    weekend_revenue = models.FloatField(verbose_name='주말매출액')
    weekend_revenue_currency = models.CharField(
        max_length=1, 
        choices=CURRENCY_CHOICES, 
        verbose_name='주말매출액 통화',
        default='$'
    )
    total_revenue = models.FloatField(verbose_name='누적매출액')
    total_revenue_currency = models.CharField(
        max_length=1, 
        choices=CURRENCY_CHOICES, 
        verbose_name='누적매출액 통화',
        default='$'
    )
    distributor = models.CharField(max_length=255, verbose_name='배급사')
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, verbose_name='국가')
    year = models.IntegerField(verbose_name='연도')
    week = models.IntegerField(verbose_name='주차')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    
    class Meta:
        db_table = 'international_boxoffice'
        indexes = [
            models.Index(fields=['country', 'year', 'week']),
            models.Index(fields=['title']),
        ]
        unique_together = [['country', 'year', 'week', 'title']]
        verbose_name = '해외 박스오피스'
        verbose_name_plural = '해외 박스오피스'
    
    def __str__(self):
        return f"{self.country} - {self.title} ({self.year}년 {self.week}주차)"
