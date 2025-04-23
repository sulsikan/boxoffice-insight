from django.http import HttpResponse
from django.shortcuts import render
from selenium.webdriver.common.devtools.v133.page import print_to_pdf
from collections import defaultdict
from genre_trend.models import MovieBasicInfo
from genre_trend.models import MovieDetail
import pandas as pd


def index(request):
    return render(request, 'base.html')


#
def genre_cumulative_stats(request):
    movies = MovieDetail.objects.all()
    genre_stats = defaultdict(lambda: {"매출액": 0, "관객수": 0, "스크린수": 0, "개봉편수": 0})

    # 장르별 매출액, 관객수, 스크린수. 개봉편수 전달
    for movie in MovieDetail.objects.all():
        genres = [g.strip() for g in movie.genre.split(",")]
        for genre in genres:
            genre_stats[genre]["매출액"] += int(movie.sales.replace(",", ""))
            genre_stats[genre]["관객수"] += int(movie.audience.replace(",", ""))
            genre_stats[genre]["스크린수"] += int(movie.screen.replace(",", ""))
            genre_stats[genre]["개봉편수"] += 1

    labels = list(genre_stats.keys())
    sales = [genre_stats[g]["매출액"] for g in labels]
    audience = [genre_stats[g]["관객수"] for g in labels]
    screens = [genre_stats[g]["스크린수"] for g in labels]
    movie_counts = [genre_stats[g]["개봉편수"] for g in labels]

    context = {
        "labels": labels,
        "sales": sales,
        "audience": audience,
        "screens": screens,
        "movie_counts": movie_counts,

    }

    return render(request, 'genre_trend/genre_cumulative_stats.html', context)


def genre_yearly_trends(request):
    selected_year = int(request.GET.get('year', 2010))

    qs = MovieDetail.objects.all().values()
    df = pd.DataFrame(list(qs))
    # 예시 데이터프레임 (이미 있는 상태라고 가정)
    df['sales'] = df['sales'].str.replace(',', '').astype(int)
    df['audience'] = df['audience'].str.replace(',', '').astype(int)
    df['screen'] = df['screen'].str.replace(',', '').astype(int)
    df['release_year'] = pd.to_datetime(df['release_date']).dt.year

    # genre 다중 분해
    df['genre'] = df['genre'].str.split(',')
    df = df.explode('genre')
    df['genre'] = df['genre'].str.strip()

    # 집계
    agg_df = df.groupby(['release_year', 'genre']).agg({
        'sales': 'sum',
        'audience': 'sum',
        'screen': 'sum',
        'movie_name': 'count'
    }).rename(columns={'movie_name': 'release_count'}).reset_index()

    chart_info = [
        ('salesChart', '판매액', 'sales'),
        ('audienceChart', '관객수', 'audience'),
        ('screenChart', '스크린 수', 'screen'),
        ('countChart', '편수', 'release_count')
    ]

    data = agg_df.to_dict(orient='records')
    filtered = agg_df[agg_df['release_year'] == selected_year]
    return render(request, 'genre_trend/genre_yearly_trends.html', {
        'data': filtered.to_dict(orient='records'),
        'selected_year': selected_year,
        'year_choices': sorted(agg_df['release_year'].unique(), reverse=True),
        'chart_info': chart_info,
    })


def genre_stat(request):
    movies = MovieBasicInfo.objects.all()
    data = {}
    for movie in movies:
        genres = movie.genre.split(",")
        for genre in genres:
            genre = genre.strip()
            data[genre] = data.get(genre, 0) + 1
    context = {
        'labels': list(data.keys()),
        'values': list(data.values()),
    }
    return render(request, 'genre_trend/genre_stat.html', context)
