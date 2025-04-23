# crawl_info.py에서 rank 데이터가 제대로 안받아질 때만 사용되는 코드입니다.
# 실행 방법 : 프로젝트 루트 폴더에서 python movie_performance_summary/crawl_rank.py
import django
import os
import sys
# Django 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 불러오기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from .models import Movie

# 모든 영화 데이터를 개봉일 기준으로 정렬 (원하는 기준으로 정렬 가능)
movies = Movie.objects.all().order_by('id')

# 순위 넣기
for idx, movie in enumerate(movies, start=1):
    movie.rank = idx
    movie.save()
