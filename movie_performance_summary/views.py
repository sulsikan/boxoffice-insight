import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 대신 Agg 백엔드 사용

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager as fm
from io import BytesIO
import base64
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Movie, Movie10days

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # MacOS의 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# "억" 단위로 변환하는 함수
def format_revenue(x, pos):
    return f"{x:.0f}억" if x >= 0 else ""  # 소수점 없이 정수로 표시

# "만" 단위로 변환하는 함수
def format_audience(x, pos):
    return f"{x:.0f}만" if x >= 0 else ""  # 소수점 없이 정수로 표시

def graph_view(request):
    # 그래프 생성
    font_path = '/Users/sulsikan/Documents/programmers/jupyter/실습파일_4/BMHANNAPro.ttf'  # 시스템에 맞는 경로로 변경 필요
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()

    # x축: days_since_release, y축: moviegoers_cumulative
    x = [entry['days_since_release'] for entry in data]
    y = [int(entry['moviegoers_cumulative'].replace(',', '')) for entry in data]

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue', label='명량')
    plt.title('누적 관객 수 변화')
    plt.xlabel('개봉 경과일')
    plt.ylabel('누적 관객 수')
    plt.grid(True)
    plt.legend()

    # 이미지 파일로 저장 (메모리 버퍼에 저장)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # HttpResponse를 이용해 이미지를 직접 응답으로 보냄
    return HttpResponse(buf, content_type='image/png')

def movie_performance_summary(request):
    query = request.GET.get('q', '')  # 'q' 파라미터로 검색어를 가져옴
    if query:
        movies = Movie.objects.filter(movie_name__icontains=query)  # 검색어가 포함된 영화 필터링
    else:
        movies = Movie.objects.all()  # 검색어가 없으면 전체 데이터 반환
    return render(request, 'movie_performance_summary/movie_performance_summary.html', {'movies': movies, 'query': query})

def movie_detail(request, movie_id):
    # 영화 객체 가져오기
    movie = get_object_or_404(Movie, id=movie_id)

    # Movie10days 데이터 가져오기
    movie_daily_data = Movie10days.objects.filter(movie_name=movie.movie_name).order_by('days_since_release')

    # 데이터를 DataFrame으로 변환
    movie_daily_data_list = list(movie_daily_data.values())
    df = pd.DataFrame(movie_daily_data_list)

    # 데이터 전처리
    df["release_day_text"] = df["days_since_release"].str.extract(r'(개봉\d+일)')
    df["release_day_number"] = df["days_since_release"].str.extract(r'(\d+)')  # 숫자 추출
    df["release_day_number"] = pd.to_numeric(df["release_day_number"], errors="coerce")  # 숫자로 변환, 변환 불가 시 NaN
    df = df.dropna(subset=["release_day_number"])  # NaN 값 제거
    df["release_day_number"] = df["release_day_number"].astype(int)  # 정수형 변환

    df["moviegoers_cumulative"] = pd.to_numeric(df["moviegoers_cumulative"], errors="coerce") / 10000  # 만 단위로 변환
    df["moviegoers_num"] = pd.to_numeric(df["moviegoers_num"], errors="coerce") / 10000  # 만 단위로 변환
    df["revenue_cumulative"] = pd.to_numeric(df["revenue_cumulative"], errors="coerce") / 100000000  # 억 단위로 변환
    df["screen_num"] = pd.to_numeric(df["screen_num"], errors="coerce")  # 스크린 수 데이터 추가

    # 개봉일 순서대로 정렬
    df = df.sort_values(by="release_day_number")

    # Chart.js에 전달할 데이터 준비
    chart_data = {
        "labels": df["release_day_text"].tolist(),  # x축 라벨
        "moviegoers_cumulative": df["moviegoers_cumulative"].tolist(),  # 누적 관객 수
        "moviegoers_num": df["moviegoers_num"].tolist(),  # 일일 관객 수
        "revenue_cumulative": df["revenue_cumulative"].tolist(),  # 누적 매출액
        "screen_count": df["screen_num"].tolist(),  # 스크린 수 데이터 추가
    }

    return render(request, 'movie_performance_summary/movie_detail.html', {
        'movie': movie,
        'chart_data': chart_data,  # Chart.js 데이터 전달
    })

def movie_performance_comparison(request):
    # 연도 범위 설정
    start_year = 2005
    end_year = 2024

    # 검색어 가져오기
    search_query = request.GET.get('search', '').strip()

    # 연도별 데이터 저장용 딕셔너리
    chart_data_by_year = {}

    # 검색어가 있는 경우
    if search_query:
        # 검색어로 필터링된 영화 가져오기
        searched_movies = Movie.objects.filter(movie_name__icontains=search_query)

        # 검색된 영화의 연도를 기준으로 해당 연도의 모든 영화 가져오기
        years_with_searched_movies = searched_movies.values_list('release_date__year', flat=True).distinct()

        for year in years_with_searched_movies:
            movies = Movie.objects.filter(release_date__year=year)  # 해당 연도의 모든 영화 가져오기
            labels = [movie.movie_name for movie in movies]  # 영화 제목
            data = [movie.total_moviegoers_num for movie in movies]  # 관객수

            # Chart.js에 전달할 데이터 저장
            if labels:
                chart_data_by_year[year] = {
                    'labels': labels,
                    'data': data,
                }
    else:
        # 검색어가 없는 경우 전체 연도 처리
        for year in range(start_year, end_year + 1):
            movies = Movie.objects.filter(release_date__year=year)  # 해당 연도의 영화 데이터 필터링
            labels = [movie.movie_name for movie in movies]  # 영화 제목
            data = [movie.total_moviegoers_num for movie in movies]  # 관객수

            # Chart.js에 전달할 데이터 저장
            if labels:
                chart_data_by_year[year] = {
                    'labels': labels,
                    'data': data,
                }

    # 연도를 역순으로 정렬
    sorted_chart_data_by_year = dict(sorted(chart_data_by_year.items(), key=lambda x: x[0], reverse=True))

    return render(request, 'movie_performance_summary/movie_performance_comparison.html', {
        'chart_data_by_year': sorted_chart_data_by_year,  # 연도별 데이터 전달
        'search_query': search_query,  # 검색어 전달
    })