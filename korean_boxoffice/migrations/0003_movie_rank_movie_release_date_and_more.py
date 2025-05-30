# Generated by Django 5.2 on 2025-04-22 01:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("korean_boxoffice", "0002_movie"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="rank",
            field=models.IntegerField(null=True, verbose_name="순위"),
        ),
        migrations.AddField(
            model_name="movie",
            name="release_date",
            field=models.DateField(null=True, verbose_name="개봉일"),
        ),
        migrations.AddField(
            model_name="movie",
            name="total_moviegoers_num",
            field=models.IntegerField(null=True, verbose_name="관객수"),
        ),
        migrations.AddField(
            model_name="movie",
            name="total_revenue",
            field=models.IntegerField(null=True, verbose_name="매출액"),
        ),
        migrations.AlterField(
            model_name="movie",
            name="movie_name",
            field=models.CharField(max_length=255, verbose_name="영화 제목"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="days_since_release",
            field=models.CharField(max_length=50, verbose_name="개봉 경과"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="movie_name",
            field=models.CharField(max_length=255, verbose_name="영화 제목"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="moviegoers_cumulative",
            field=models.IntegerField(verbose_name="누적 관객 수"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="moviegoers_num",
            field=models.IntegerField(verbose_name="일일 관객 수"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="revenue",
            field=models.IntegerField(verbose_name="일일 수익"),
        ),
        migrations.AlterField(
            model_name="movie10days",
            name="revenue_cumulative",
            field=models.IntegerField(verbose_name="누적 수익"),
        ),
    ]
