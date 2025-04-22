from django.shortcuts import render
from .models import Movie10days
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager
from io import BytesIO
from django.http import HttpResponse

# 억 단위로 변환하는 함수
def format_revenue(x, pos):
    return f"{x:.1f}억" if x >= 0 else ""

# "만" 단위로 변환해주는 함수
def format_audience(x, pos):
    return f"{x/10000:.1f}만" if x >= 0 else ""

# 영화 데이터를 처리하고 시각화하는 뷰
def movie_summary(request):
    # Movie10days 테이블에서 데이터 가져오기
    movie_data = Movie10days.objects.all()

    # # 영화 데이터를 pandas DataFrame으로 변환
    # movie_daily_data_list = []
    # for movie in movie_data:
    #     movie_daily_data_list.append({
    #         "movie_name": movie.movie_name,
    #         "days_since_release": movie.days_since_release,
    #         "moviegoers_cumulative": movie.moviegoers_cumulative,
    #         "moviegoers_num": movie.moviegoers_num,
    #         "revenue_cumulative": movie.revenue_cumulative,
    #     })

    df = pd.DataFrame(movie_data)

    # 컬럼 이름 공백 제거
    df.columns = df.columns.str.strip()

    # 🧹 데이터 전처리
    # df["release_day_text"] = df["days_since_release"].str.extract(r'(개봉\d+일)')
    df["release_day_text"] = df["days_since_release"].astype(str).str.extract(r'(개봉\d+일)')

    df["moviegoers_cumulative"] = pd.to_numeric(df["moviegoers_cumulative"].str.replace(",", ""), errors="coerce")
    df["moviegoers_num"] = pd.to_numeric(df["moviegoers_num"].str.replace(",", ""), errors="coerce")
    df["revenue_cumulative"] = pd.to_numeric(df["revenue_cumulative"].str.replace(",", ""), errors="coerce")
    df["revenue_cumulative"] = df["revenue_cumulative"] / 100000000

    # 영화 제목을 인덱스로 사용하여 원하는 영화 선택 (예: 두 번째 영화 선택)
    selected_movie_index = 1  # 예시 : 두 번째 영화 선택 (0부터 시작)
    df_selected_movie = df.iloc[selected_movie_index:selected_movie_index+2]

    # 시각화
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 누적 관객 수 그래프
    sns.lineplot(data=df_selected_movie, x="release_day_text", y="moviegoers_cumulative", ax=ax1,label="누적 관객 수", marker="o", color="blue")
    # 일일 관객 수 그래프
    sns.lineplot(data=df_selected_movie, x="release_day_text", y="moviegoers_num", ax=ax1,label="일일 관객 수", marker="s", color="green")
    ax1.set_xlabel("개봉 후 경과일")
    ax1.set_ylabel("관객 수")
    ax1.tick_params(axis='x', rotation=45)

    # 🎯 막대 그래프 - 누적 매출 (두 번째 y축)
    ax2 = ax1.twinx()
    sns.barplot(data=df_selected_movie, x="release_day_text", y="revenue_cumulative", ax=ax2, alpha=0.3, color="orange")
    ax2.set_ylabel("누적 매출액 (막대)")

    # 막대그래프 아래 y축 포맷 변경
    ax1.yaxis.set_major_formatter(FuncFormatter(format_audience))
    ax2.yaxis.set_major_formatter(FuncFormatter(format_revenue))

    plt.title("영화 흥행 요약 정보")
    ax1.legend(loc="upper left")
    plt.tight_layout()

    # 그래프를 이미지로 저장
    import os
    from django.conf import settings
    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    graph_image_path = os.path.join(graph_dir, 'graph.png')
    plt.savefig(graph_image_path)
    plt.close()

    # 템플릿에 전달할 경로
    # graph_image_url = os.path.join(settings.MEDIA_URL, 'graphs', 'graph.png')
    graph_image_url = settings.MEDIA_URL + 'graphs/graph.png'


    return render(request, 'movie_summary.html', {'graph_image': graph_image_url})
    # 이미지 파일로 저장 (메모리 버퍼에 저장)
    # buf = BytesIO()
    # plt.savefig(buf, format='png')
    # buf.seek(0)

    # # HttpResponse를 이용해 이미지를 직접 응답으로 보냄
    # return HttpResponse(buf, content_type='image/png')



def graph_view(request):
    # 그래프 생성
    font_path = '/Users/sulsikan/Documents/programmers/jupyter/실습파일_4/BMHANNAPro.ttf'  # 시스템에 맞는 경로로 변경 필요
    font_prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()

    # 주어진 데이터
    data = [
        {'movie_name': '명량', 'days_since_release': '개봉이전', 'moviegoers_cumulative': '22,500'},
        {'movie_name': '명량', 'days_since_release': '개봉1일(07/30)', 'moviegoers_cumulative': '705,201'}
    ]

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