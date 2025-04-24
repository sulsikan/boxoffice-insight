from django.shortcuts import render
from collections import defaultdict
from genre_trend.models import MovieDetail
from django.db.models import Sum, Count, IntegerField
from django.db.models.functions import Substr, Cast
from collections import defaultdict
import re

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

def parse_int(value):
    """쉼표(,) 제거하고 정수로 변환. 실패 시 0 반환"""
    try:
        return int(re.sub(r'[^\d]', '', value))  # 숫자만 추출
    except:
        return 0

def genre_yearly_trends(request):
    default_year = '2025'
    selected_year = request.GET.get('year') or '2025'  # 선택된 연도 받기
    movies = MovieDetail.objects.all()

    all_years = sorted(set(m.release_date[:4] for m in movies))  # 연도 목록

    if selected_year:
        movies = movies.filter(release_date__startswith=selected_year)

    result = defaultdict(lambda: {
        'total_sales': 0,
        'total_audience': 0,
        'total_screens': 0,
        'movie_count': 0
    })

    for movie in movies:
        year = movie.release_date[:4]
        genres = [g.strip() for g in movie.genre.split(',')]
        for genre in genres:
            key = (year, genre)
            result[key]['total_sales'] += parse_int(movie.sales)
            result[key]['total_audience'] += parse_int(movie.audience)
            result[key]['total_screens'] += parse_int(movie.screen)
            result[key]['movie_count'] += 1

    sorted_data = sorted(
        [
            {'year': year, 'genre': genre, **values}
            for (year, genre), values in result.items()
        ],
        key=lambda x: (x['year'], x['genre'])
    )
    top5_data = sorted_data[:5]
    return render(request, 'genre_trend/genre_yearly_trends.html', {
        'data': sorted_data,
        'years': all_years,
        'selected_year': selected_year,
        'top5': top5_data
    })


